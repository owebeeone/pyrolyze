from __future__ import annotations

"""Paired mutable/frozen dataclass helpers.

This module supports two symmetric pairing styles:

- `freezable_dataclass` + `frozen_dataclass`
  Use when the mutable class is the canonical authored definition and the
  frozen peer should be generated from it. Instances convert with
  `to_frozen()` and `to_mutable()`.

- `thawable_dataclass` + `thawed_dataclass`
  Use when the frozen class is the canonical authored definition and the
  mutable peer should be generated from it. Instances convert with
  `to_thawed()` and `to_frozen()`.

In both directions, the generated peer is a distinct dataclass type rather
than a subclass of the source type. That keeps mutability explicit in the type
system and allows the frozen peer to use real `dataclass(frozen=True)`
semantics.

Optional deep conversion can also:

- convert nested paired objects by calling their conversion methods
- normalize `list[...] <-> tuple[...]` across mutable/frozen boundaries

Annotation-driven deep conversion depends on how postponed annotations are
resolved. See `HintResolutionMode` for the tradeoffs between lexical accuracy
and portability.
"""

import sys
import types
import typing
from dataclasses import MISSING, Field, dataclass, field, fields, make_dataclass
from enum import Enum
from typing import Any, Callable, Union, get_args, get_origin


class HintResolutionMode(Enum):
    """Controls how freezable decorators resolve postponed annotations.

    `STRICT_FRAME` uses `sys._getframe()` to capture the decorator caller's
    globals and locals. This is the most accurate mode for classes defined in
    local scopes, but it depends on implementation-specific frame support and
    may fail on some Python runtimes.

    `FRAME_WITH_FALLBACK` first attempts frame-based resolution and falls back
    to module-global resolution if frame access is unavailable. This is the
    default best-effort mode and may produce different results across Python
    implementations.

    `STRICT_MODULE` resolves annotations using only the defining module's
    globals. This is the most portable mode, but local-scope forward references
    may fail to resolve and fall back to the original annotations.
    """

    STRICT_FRAME = "strict_frame"
    FRAME_WITH_FALLBACK = "frame_with_fallback"
    STRICT_MODULE = "strict_module"


def _get_resolved_hints(cls: type[Any]) -> dict[str, Any]:
    cached = getattr(cls, "__resolved_type_hints__", None)
    if cached is None:
        try:
            cached = typing.get_type_hints(cls, include_extras=True)
        except (AttributeError, NameError, TypeError):
            cached = getattr(cls, "__annotations__", {})
        setattr(cls, "__resolved_type_hints__", cached)
    return cached


def _ensure_cached_hints(cls: type[Any]) -> None:
    if getattr(cls, "__resolved_type_hints__", None) is not None:
        return
    mode = getattr(cls, "_hint_resolution", HintResolutionMode.STRICT_FRAME)
    globalns, localns = _hint_namespaces(cls, mode=mode)
    _cache_resolved_hints(cls, globalns=globalns, localns=localns)


def _cache_resolved_hints(
    cls: type[Any],
    *,
    globalns: dict[str, Any] | None,
    localns: dict[str, Any] | None,
) -> None:
    try:
        resolved = typing.get_type_hints(
            cls,
            globalns=globalns,
            localns=localns,
            include_extras=True,
        )
    except (AttributeError, NameError, TypeError):
        resolved = getattr(cls, "__annotations__", {})
    setattr(cls, "__resolved_type_hints__", resolved)


def _module_globalns(cls: type[Any]) -> dict[str, Any]:
    module = sys.modules.get(cls.__module__)
    if module is None:
        raise ModuleNotFoundError(
            f"Cannot resolve type hints: module {cls.__module__} not loaded"
        )
    return vars(module)


def _hint_namespaces(
    cls: type[Any],
    *,
    mode: HintResolutionMode,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if mode is HintResolutionMode.STRICT_MODULE:
        return _module_globalns(cls), None

    if mode is HintResolutionMode.STRICT_FRAME:
        frame = sys._getframe(2)
        return frame.f_globals, frame.f_locals

    try:
        frame = sys._getframe(2)
    except (AttributeError, ValueError):
        return _module_globalns(cls), None
    return frame.f_globals, frame.f_locals


def _extract_collection_info(hint: Any) -> tuple[Any | None, tuple[Any, ...]]:
    origin = get_origin(hint)
    args = get_args(hint)

    if origin is Union or (hasattr(types, "UnionType") and origin is types.UnionType):
        non_none = tuple(arg for arg in args if arg is not type(None))
        if len(non_none) == 1:
            return _extract_collection_info(non_none[0])
        return None, ()

    if origin in (list, tuple):
        return origin, args
    if hint in (list, tuple):
        return hint, ()
    return None, ()


def _transform_value(
    value: Any,
    hint: Any,
    *,
    to_frozen: bool,
    list_params: bool,
    freeze_params: bool,
) -> Any:
    if value is None:
        return None

    collection_origin, collection_args = _extract_collection_info(hint)
    item_hint = collection_args[0] if collection_args else Any

    target_collection: type[Any] | None = None
    if list_params and collection_origin is list and isinstance(value, (list, tuple)):
        target_collection = tuple if to_frozen else list
    elif list_params and collection_origin is tuple and isinstance(value, (list, tuple)):
        target_collection = tuple if to_frozen else list

    if target_collection is not None:
        items = (
            [
                _transform_value(
                    item,
                    item_hint,
                    to_frozen=to_frozen,
                    list_params=list_params,
                    freeze_params=freeze_params,
                )
                for item in value
            ]
            if freeze_params
            else list(value)
        )
        return target_collection(items)

    if freeze_params:
        method_names = ("to_frozen",) if to_frozen else ("to_mutable", "to_thawed")
        for method_name in method_names:
            method = getattr(value, method_name, None)
            if callable(method):
                return method()

    return value


def _resolve_paired_type(owner_type: type[Any]) -> type[Any]:
    """Resolve paired type with lazy evaluation, caching, and dotted-name support."""
    paired = getattr(owner_type, "_paired_type", None)
    if isinstance(paired, type):
        return paired
    if isinstance(paired, str):
        module = sys.modules.get(owner_type.__module__)
        if module is None:
            raise ModuleNotFoundError(
                f"Cannot resolve paired type: module {owner_type.__module__} not loaded"
            )
        for part in paired.split("."):
            try:
                module = getattr(module, part)
            except AttributeError as exc:
                raise AttributeError(
                    f"Cannot resolve paired type {paired!r} in module {owner_type.__module__}"
                ) from exc
        paired = module
        setattr(owner_type, "_paired_type", paired)
    if not isinstance(paired, type):
        raise TypeError(
            f"{owner_type.__name__} has no valid paired type (got {type(paired).__name__})"
        )
    return paired


def _dataclass_field_spec(item: Field[Any]) -> tuple[Any, ...]:
    """Format fields for `make_dataclass`, preserving default/factory values."""
    if item.default is not MISSING:
        return (item.name, item.type, field(default=item.default))
    if item.default_factory is not MISSING:
        return (item.name, item.type, field(default_factory=item.default_factory))
    return (item.name, item.type)


def _direct_dataclass_bases(owner_type: type[Any]) -> tuple[type[Any], ...]:
    return tuple(
        base
        for base in owner_type.__bases__
        if hasattr(base, "__dataclass_fields__")
    )


def freezable_dataclass(
    *,
    frozen_type: str | type[Any],
    slots: bool = True,
    freeze_params: bool = True,
    list_params: bool = True,
    # Default to STRICT_FRAME because lexical-scope resolution is the least
    # surprising behavior for local classes and postponed annotations. More
    # portable modes are opt-in because they may silently change semantics.
    hint_resolution: HintResolutionMode = HintResolutionMode.STRICT_FRAME,
    **dataclass_kwargs: Any,
) -> Callable[[type[Any]], type[Any]]:
    def decorate(cls: type[Any]) -> type[Any]:
        wrapped = dataclass(slots=slots, **dataclass_kwargs)(cls)
        setattr(wrapped, "_paired_type", frozen_type)
        setattr(wrapped, "_freeze_params", freeze_params)
        setattr(wrapped, "_list_params", list_params)
        setattr(wrapped, "_hint_resolution", hint_resolution)
        globalns, localns = _hint_namespaces(wrapped, mode=hint_resolution)
        _cache_resolved_hints(
            wrapped,
            globalns=globalns,
            localns=localns,
        )

        def to_frozen(self):
            frozen_cls = _resolve_paired_type(type(self))
            _ensure_cached_hints(type(self))
            resolved_hints = _get_resolved_hints(type(self))
            values: dict[str, Any] = {}
            for item in fields(self):
                if not item.init:
                    continue
                value = getattr(self, item.name)
                if freeze_params or list_params:
                    value = _transform_value(
                        value,
                        resolved_hints.get(item.name, item.type),
                        to_frozen=True,
                        list_params=list_params,
                        freeze_params=freeze_params,
                    )
                values[item.name] = value
            return frozen_cls(**values)

        setattr(wrapped, "to_frozen", to_frozen)
        return wrapped

    return decorate


def frozen_dataclass(
    *,
    mutable_type: type[Any],
    slots: bool = True,
    # Match the mutable-side default: fail explicitly rather than silently
    # degrading local annotation resolution on runtimes without frame support.
    hint_resolution: HintResolutionMode = HintResolutionMode.STRICT_FRAME,
    **dataclass_kwargs: Any,
) -> Callable[[type[Any]], type[Any]]:
    def decorate(cls: type[Any]) -> type[Any]:
        if not hasattr(mutable_type, "__dataclass_fields__"):
            raise TypeError(f"mutable_type {mutable_type.__name__} must be a dataclass")

        mutable_bases = _direct_dataclass_bases(mutable_type)
        frozen_bases = tuple(_resolve_paired_type(base) for base in mutable_bases)
        inherited_field_names = {
            item.name
            for base in mutable_bases
            for item in fields(base)
        }
        mutable_fields = tuple(
            _dataclass_field_spec(item)
            for item in fields(mutable_type)
            if item.name not in inherited_field_names
        )
        namespace = {
            key: value
            for key, value in cls.__dict__.items()
            if key not in {
                "__dict__",
                "__weakref__",
                "__doc__",
                "__annotations__",
                "__dataclass_fields__",
                "__dataclass_params__",
                "__match_args__",
                "__slots__",
            }
        }

        wrapped = make_dataclass(
            cls.__name__,
            mutable_fields,
            bases=frozen_bases,
            namespace=namespace,
            frozen=True,
            slots=slots,
            **dataclass_kwargs,
        )

        freeze_params = getattr(mutable_type, "_freeze_params", False)
        list_params = getattr(mutable_type, "_list_params", False)
        setattr(wrapped, "_hint_resolution", hint_resolution)
        globalns, localns = _hint_namespaces(wrapped, mode=hint_resolution)

        def to_mutable(self):
            _ensure_cached_hints(mutable_type)
            resolved_hints = _get_resolved_hints(mutable_type)
            values: dict[str, Any] = {}
            for item in fields(self):
                if not item.init:
                    continue
                value = getattr(self, item.name)
                if freeze_params or list_params:
                    value = _transform_value(
                        value,
                        resolved_hints.get(item.name, item.type),
                        to_frozen=False,
                        list_params=list_params,
                        freeze_params=freeze_params,
                    )
                values[item.name] = value
            return mutable_type(**values)

        setattr(wrapped, "to_mutable", to_mutable)
        setattr(wrapped, "_paired_type", mutable_type)
        setattr(mutable_type, "_paired_type", wrapped)
        wrapped.__module__ = cls.__module__
        wrapped.__qualname__ = cls.__qualname__
        wrapped.__doc__ = cls.__doc__
        _cache_resolved_hints(
            wrapped,
            globalns=globalns,
            localns=localns,
        )
        return wrapped

    return decorate


def thawable_dataclass(
    *,
    thawed_type: str | type[Any],
    slots: bool = True,
    freeze_params: bool = True,
    list_params: bool = True,
    # Default to STRICT_FRAME because lexical-scope resolution is the least
    # surprising behavior for local classes and postponed annotations. More
    # portable modes are opt-in because they may silently change semantics.
    hint_resolution: HintResolutionMode = HintResolutionMode.STRICT_FRAME,
    **dataclass_kwargs: Any,
) -> Callable[[type[Any]], type[Any]]:
    def decorate(cls: type[Any]) -> type[Any]:
        wrapped = dataclass(slots=slots, frozen=True, **dataclass_kwargs)(cls)
        setattr(wrapped, "_paired_type", thawed_type)
        setattr(wrapped, "_freeze_params", freeze_params)
        setattr(wrapped, "_list_params", list_params)
        setattr(wrapped, "_hint_resolution", hint_resolution)
        globalns, localns = _hint_namespaces(wrapped, mode=hint_resolution)
        _cache_resolved_hints(
            wrapped,
            globalns=globalns,
            localns=localns,
        )

        def to_thawed(self):
            thawed_cls = _resolve_paired_type(type(self))
            _ensure_cached_hints(type(self))
            resolved_hints = _get_resolved_hints(type(self))
            values: dict[str, Any] = {}
            for item in fields(self):
                if not item.init:
                    continue
                value = getattr(self, item.name)
                if freeze_params or list_params:
                    value = _transform_value(
                        value,
                        resolved_hints.get(item.name, item.type),
                        to_frozen=False,
                        list_params=list_params,
                        freeze_params=freeze_params,
                    )
                values[item.name] = value
            return thawed_cls(**values)

        setattr(wrapped, "to_thawed", to_thawed)
        return wrapped

    return decorate


def thawed_dataclass(
    *,
    frozen_type: type[Any],
    slots: bool = True,
    # Match the frozen-side default: fail explicitly rather than silently
    # degrading local annotation resolution on runtimes without frame support.
    hint_resolution: HintResolutionMode = HintResolutionMode.STRICT_FRAME,
    **dataclass_kwargs: Any,
) -> Callable[[type[Any]], type[Any]]:
    def decorate(cls: type[Any]) -> type[Any]:
        if not hasattr(frozen_type, "__dataclass_fields__"):
            raise TypeError(f"frozen_type {frozen_type.__name__} must be a dataclass")

        frozen_bases = _direct_dataclass_bases(frozen_type)
        thawed_bases = tuple(_resolve_paired_type(base) for base in frozen_bases)
        inherited_field_names = {
            item.name
            for base in frozen_bases
            for item in fields(base)
        }
        thawed_fields = tuple(
            _dataclass_field_spec(item)
            for item in fields(frozen_type)
            if item.name not in inherited_field_names
        )
        namespace = {
            key: value
            for key, value in cls.__dict__.items()
            if key not in {
                "__dict__",
                "__weakref__",
                "__doc__",
                "__annotations__",
                "__dataclass_fields__",
                "__dataclass_params__",
                "__match_args__",
                "__slots__",
            }
        }

        wrapped = make_dataclass(
            cls.__name__,
            thawed_fields,
            bases=thawed_bases,
            namespace=namespace,
            frozen=False,
            slots=slots,
            **dataclass_kwargs,
        )

        freeze_params = getattr(frozen_type, "_freeze_params", False)
        list_params = getattr(frozen_type, "_list_params", False)
        setattr(wrapped, "_hint_resolution", hint_resolution)
        globalns, localns = _hint_namespaces(wrapped, mode=hint_resolution)

        def to_frozen(self):
            _ensure_cached_hints(frozen_type)
            resolved_hints = _get_resolved_hints(frozen_type)
            values: dict[str, Any] = {}
            for item in fields(self):
                if not item.init:
                    continue
                value = getattr(self, item.name)
                if freeze_params or list_params:
                    value = _transform_value(
                        value,
                        resolved_hints.get(item.name, item.type),
                        to_frozen=True,
                        list_params=list_params,
                        freeze_params=freeze_params,
                    )
                values[item.name] = value
            return frozen_type(**values)

        setattr(wrapped, "to_frozen", to_frozen)
        setattr(wrapped, "_paired_type", frozen_type)
        setattr(frozen_type, "_paired_type", wrapped)
        wrapped.__module__ = cls.__module__
        wrapped.__qualname__ = cls.__qualname__
        wrapped.__doc__ = cls.__doc__
        _cache_resolved_hints(
            wrapped,
            globalns=globalns,
            localns=localns,
        )
        return wrapped

    return decorate


__all__ = [
    "HintResolutionMode",
    "freezable_dataclass",
    "frozen_dataclass",
    "thawable_dataclass",
    "thawed_dataclass",
]
