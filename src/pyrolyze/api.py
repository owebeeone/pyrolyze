"""Public source-level API surface for the greenfield prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Any, Callable, Generic, Iterable, Literal, ParamSpec, Protocol, TypeVar, cast

from frozendict import frozendict

from .backends.model import UiInterface

T = TypeVar("T")
P = ParamSpec("P")

# This module is the author-facing source contract that examples and transformed
# source import from; it is intentionally separate from runtime implementation.

@dataclass(frozen=True, slots=True)
class KeyedIterable(Generic[T]):
    """Wrapper used by declarative source to signal keyed iteration semantics."""

    items: Iterable[T]
    key: Callable[[T], Any]


@dataclass(frozen=True, slots=True)
class UIElement:
    """Placeholder UI node returned by declarative widget stubs."""

    kind: str
    props: dict[str, Any]
    children: tuple["EmittedNode", ...] = ()
    call_site_id: int | str | None = field(default=None, compare=False)
    slot_id: Any | None = field(default=None, compare=False)


class MissingType:
    """Sentinel type used by generated UI libraries to represent omission."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "MISSING"


MISSING = MissingType()


class CallFromNonPyrolyzeContext(RuntimeError):
    """Raised when a source-surface ref is called outside component execution."""


@dataclass(frozen=True, slots=True)
class ComponentMetadata(Generic[P]):
    """Metadata attached to public component-ref symbols."""

    name: str
    _func: Callable[..., None]
    packed_kwargs: bool = False
    packed_kwarg_param_names: tuple[str, ...] = ()


class ComponentRef(Protocol[P]):
    """Callable typing surface for component refs exposed to user code."""

    _pyrolyze_meta: ComponentMetadata[P]

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None: ...


@dataclass(frozen=True, slots=True)
class PyrolyzeEventParam:
    """Marker attached to event-boundary callback parameters."""


@dataclass(frozen=True, slots=True)
class PyrolyzeSlottedParam:
    """Marker attached to slotted-helper callable annotations."""


class SlotSelector:
    """Base class for immutable runtime mount selector values."""

    __slots__ = ()


@dataclass(frozen=True, slots=True)
class MountSelector(SlotSelector):
    """Immutable runtime selector descriptor for future `mount(...)` support."""

    kind: Literal["named", "default", "no_emit"]
    name: str | None
    values: frozendict[str, Any] = field(default_factory=frozendict)

    @classmethod
    def named(cls, name: str) -> "MountSelector":
        return cls(kind="named", name=name)

    @classmethod
    def default_selector(cls) -> "MountSelector":
        return cls(kind="default", name="default")

    @classmethod
    def no_emit_selector(cls) -> "MountSelector":
        return cls(kind="no_emit", name=None)

    def __call__(self, /, **values: Any) -> "MountSelector":
        if self.kind != "named":
            raise TypeError(f"{self.kind} selector does not accept parameters")
        if not values:
            return self
        return MountSelector(kind=self.kind, name=self.name, values=frozendict(values))


@dataclass(frozen=True, slots=True)
class MountDirective:
    """Retained structural mount-selection node emitted by transformed source."""

    selectors: tuple[SlotSelector, ...]
    children: tuple["EmittedNode", ...] = ()
    slot_id: Any | None = field(default=None, compare=False)


EmittedNode = UIElement | MountDirective


default = MountSelector.default_selector()
no_emit = MountSelector.no_emit_selector()


def validate_mount_selectors(*selectors: SlotSelector) -> tuple[SlotSelector, ...]:
    """Validate a selector list for the future `mount(...)` special form."""

    if not selectors:
        raise ValueError("mount selector list cannot be empty")
    for selector in selectors:
        if not isinstance(selector, SlotSelector):
            raise TypeError("mount selector terms must be SlotSelector values")
    if any(isinstance(selector, MountSelector) and selector.kind == "no_emit" for selector in selectors):
        if len(selectors) != 1:
            raise ValueError("no_emit must be the sole mount selector term")
    return selectors


def mount(*selectors: SlotSelector) -> object:
    validate_mount_selectors(*selectors)
    raise CallFromNonPyrolyzeContext(
        "mount() may only be used inside a transformed @pyrolyze function"
    )



def keyed(items: Iterable[T], key: Callable[[T], Any]) -> KeyedIterable[T]:
    return KeyedIterable(items=items, key=key)



def pyrolyze(fn: Callable[..., T]) -> Callable[..., T]:
    raise Exception("pyrolyze compiler failed")


def reactive_component(fn: Callable[..., T]) -> Callable[..., T]:
    return pyrolyze(fn)


def ui_interface(cls: type[T]) -> type[T]:
    manifest = getattr(cls, "UI_INTERFACE", None)
    if isinstance(manifest, UiInterface):
        setattr(cls, "UI_INTERFACE", manifest.bind_owner(cls))
    else:
        setattr(
            cls,
            "UI_INTERFACE",
            UiInterface(
                name=cls.__name__,
                owner=cls,
                entries=frozendict(),
            ),
        )
    return cls


def pyrolyze_slotted(fn: Callable[..., T]) -> Callable[..., T]:
    setattr(fn, "_pyrolyze_slotted", True)
    return fn


def pyrolyze_component_ref(
    meta: ComponentMetadata[P],
) -> Callable[[Callable[P, None]], ComponentRef[P]]:
    def decorate(fn: Callable[P, None]) -> ComponentRef[P]:
        setattr(fn, "_pyrolyze_meta", meta)
        return cast(ComponentRef[P], fn)

    return decorate


def call_native(factory: Callable[P, UIElement | None]) -> Callable[P, None]:
    def emit(*args: P.args, **kwargs: P.kwargs) -> None:
        raise CallFromNonPyrolyzeContext(
            "call_native() may only be used inside a transformed @pyrolyze function"
        )

    setattr(emit, "_pyrolyze_call_native_factory", factory)
    return cast(Callable[P, None], emit)


def Label(*, text: str) -> UIElement:
    return UIElement(kind="Label", props={"text": text})


type PyrolyzeHandler[**P, T] = Annotated[Callable[P, T], PyrolyzeEventParam()]
# Temporary compatibility alias for the pre-release typo.
PyrolyteHandler = PyrolyzeHandler
type SlotCallable[**P, T] = Annotated[Callable[P, T], PyrolyzeSlottedParam()]


from .hooks import use_effect, use_grip, use_mount, use_state, use_unmount


__all__ = [
    "CallFromNonPyrolyzeContext",
    "call_native",
    "ComponentMetadata",
    "ComponentRef",
    "KeyedIterable",
    "Label",
    "MISSING",
    "MissingType",
    "MountDirective",
    "MountSelector",
    "PyrolyzeHandler",
    "PyrolyzeEventParam",
    "PyrolyzeSlottedParam",
    "SlotSelector",
    "SlotCallable",
    "UIElement",
    "default",
    "keyed",
    "mount",
    "no_emit",
    "pyrolyze",
    "pyrolyze_component_ref",
    "pyrolyze_slotted",
    "reactive_component",
    "ui_interface",
    "use_effect",
    "use_grip",
    "use_mount",
    "use_state",
    "use_unmount",
    "validate_mount_selectors",
]
