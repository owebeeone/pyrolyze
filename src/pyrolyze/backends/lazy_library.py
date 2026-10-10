"""Index-driven resolution of generated native definition groups."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
import importlib
import inspect
from threading import RLock
from typing import Any, Protocol

from pyrolyze.backends.model import UiWidgetSpec


class DefinitionEntry(Protocol):
    @property
    def module_name(self) -> str: ...

    @property
    def class_name(self) -> str: ...

    @property
    def public_name(self) -> str: ...


@dataclass(frozen=True, slots=True)
class _GroupFailure:
    message: str


class LazyLibraryCatalog(Mapping[str, UiWidgetSpec]):
    def __init__(self, package: str, generation: str, entries: Mapping[str, DefinitionEntry]) -> None:
        self._package = package
        self._generation = generation
        self._entries = dict(entries)
        self._public = {entry.public_name: kind for kind, entry in entries.items()}
        if len(self._public) != len(entries):
            raise ValueError("duplicate public name in generated index")
        self._groups: dict[str, list[str]] = {}
        group_classes: dict[str, str] = {}
        for kind, entry in entries.items():
            if not entry.module_name.isidentifier():
                raise ValueError("invalid generated group module name")
            self._groups.setdefault(entry.module_name, []).append(kind)
            if group_classes.setdefault(entry.module_name, entry.class_name) != entry.class_name:
                raise ValueError("generated group must use one internal library class")
        self._specs: dict[str, UiWidgetSpec] = {}
        self._callables: dict[str, Any] = {}
        self._failures: dict[str, _GroupFailure] = {}
        self._loading: set[str] = set()
        self._lock = RLock()
        self._owner: type[Any] | None = None

    def bind_owner(self, owner: type[Any]) -> None:
        if self._owner is not None and self._owner is not owner:
            raise RuntimeError("generated catalog cannot be rebound")
        self._owner = owner

    def __iter__(self) -> Iterator[str]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, kind: object) -> bool:
        return kind in self._entries

    def __getitem__(self, kind: str) -> UiWidgetSpec:
        with self._lock:
            entry = self._entries[kind]
            self._load_group(entry.module_name, entry.public_name)
            return self._specs[kind]

    def member_names(self) -> tuple[str, ...]:
        return tuple(self._public)

    def resolve_member(self, name: str) -> Any:
        with self._lock:
            if name not in self._public:
                raise AttributeError(name)
            kind = self._public[name]
            self._load_group(self._entries[kind].module_name, name)
            return self._callables[name]

    def _load_group(self, module_name: str, requested: str) -> None:
        failure = self._failures.get(module_name)
        if failure is not None:
            raise RuntimeError(f"{failure.message}; requested={requested}") from None
        kinds = self._groups[module_name]
        if kinds[0] in self._specs:
            return
        if module_name in self._loading:
            message = f"reentrant generated group resolution: {self._package}.{module_name}"
            self._failures[module_name] = _GroupFailure(message)
            raise RuntimeError(message)
        if self._owner is None:
            raise RuntimeError("generated catalog has no facade owner")
        self._loading.add(module_name)
        try:
            module = importlib.import_module(f".{module_name}", self._package)
            if module.GENERATION != self._generation:
                raise ValueError("generation identity mismatch")
            candidate_specs: dict[str, UiWidgetSpec] = {}
            candidate_callables: dict[str, Any] = {}
            libraries: dict[str, Any] = {}
            expected_kinds = set(kinds)
            for kind in kinds:
                entry = self._entries[kind]
                if entry.class_name not in libraries:
                    library = getattr(module, entry.class_name)
                    if set(library.WIDGET_SPECS) != expected_kinds:
                        raise ValueError("group spec inventory mismatch")
                    libraries[entry.class_name] = library
                library = libraries[entry.class_name]
                spec = library.WIDGET_SPECS[kind]
                if not isinstance(spec, UiWidgetSpec) or spec.kind != kind:
                    raise ValueError(f"invalid spec for {kind}")
                manifest_entry = library.UI_INTERFACE.entries[entry.public_name]
                if manifest_entry.kind != kind:
                    raise ValueError(f"invalid manifest for {kind}")
                descriptor = inspect.getattr_static(library, entry.public_name)
                if not isinstance(descriptor, classmethod) or not inspect.isfunction(descriptor.__func__):
                    raise ValueError(f"invalid classmethod for {kind}")
                bound = descriptor.__get__(None, self._owner)
                if getattr(bound, "_pyrolyze_meta", None) is None:
                    raise ValueError(f"uncompiled component for {kind}")
                candidate_specs[kind] = spec
                candidate_callables[entry.public_name] = bound
            if module_name in self._failures:
                raise RuntimeError(self._failures[module_name].message)
            # All siblings validate before either cache becomes visible.
            self._specs.update(candidate_specs)
            self._callables.update(candidate_callables)
        except Exception as error:
            message = (
                f"invalid generated group {self._package}.{module_name}; "
                f"generation={self._generation}; {type(error).__name__}: {error}"
            )
            self._failures[module_name] = _GroupFailure(message)
            raise RuntimeError(f"{message}; requested={requested}") from error
        finally:
            self._loading.remove(module_name)


class LazyUiLibraryMeta(type):
    def __new__(mcls, name: str, bases: tuple[type[Any], ...], namespace: dict[str, Any]) -> Any:
        owner = super().__new__(mcls, name, bases, namespace)
        if "_lazy_catalog" in namespace:
            namespace["_lazy_catalog"].bind_owner(owner)
        return owner

    def __getattribute__(cls, name: str) -> Any:
        value = super().__getattribute__(name)
        if inspect.ismethod(value) and value.__self__ is not cls:
            catalog = type.__getattribute__(cls, "_lazy_catalog")
            if name in catalog._public:
                value = classmethod(value.__func__).__get__(None, cls)
                type.__setattr__(cls, name, value)
        return value

    def __getattr__(cls, name: str) -> Any:
        catalog = type.__getattribute__(cls, "_lazy_catalog")
        bound = catalog.resolve_member(name)
        if bound.__self__ is not cls:
            bound = classmethod(bound.__func__).__get__(None, cls)
        type.__setattr__(cls, name, bound)
        return bound

    def __dir__(cls) -> list[str]:
        catalog = type.__getattribute__(cls, "_lazy_catalog")
        return sorted(set(super().__dir__()) | set(catalog.member_names()))
