"""Shared backend model types for generated UI libraries and mountable specs."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any, TypeVar

from frozendict import frozendict


class AccessorKind(StrEnum):
    METHOD = "method"
    QT_PROPERTY = "qt_property"
    TK_CONFIG = "tk_config"
    PYTHON_PROPERTY = "python_property"
    DPG_CONFIG = "dpg_config"
    DPG_VALUE = "dpg_value"


class PropMode(StrEnum):
    CREATE_ONLY = "create_only"
    CREATE_ONLY_REMOUNT = "create_only_remount"
    UPDATE_ONLY = "update_only"
    CREATE_UPDATE = "create_update"
    READONLY = "readonly"


class MethodMode(StrEnum):
    CREATE_ONLY = "create_only"
    CREATE_ONLY_REMOUNT = "create_only_remount"
    UPDATE_ONLY = "update_only"
    CREATE_UPDATE = "create_update"


class EventPayloadPolicy(StrEnum):
    NONE = "none"
    FIRST_ARG = "first_arg"
    # DearPyGui item ``callback`` is ``(sender, app_data, user_data)``; use ``app_data`` only.
    SECOND_ARG = "second_arg"
    ALL_ARGS = "all_args"


class FillPolicy(StrEnum):
    RETAIN_EFFECTIVE = "retain_effective"
    TOOLKIT_DEFAULT = "toolkit_default"


class MountReplayKind(StrEnum):
    NONE = "none"
    INDEX = "index"
    ANCHOR_BEFORE = "anchor_before"


class ChildPolicy(StrEnum):
    NONE = "none"
    ORDERED = "ordered"
    SINGLE = "single"


@dataclass(frozen=True, slots=True)
class TypeRef:
    expr: str
    value: object | None = None


@dataclass(frozen=True, slots=True)
class UiParamSpec:
    name: str
    annotation: TypeRef | None
    default_repr: str | None = None


@dataclass(frozen=True, slots=True)
class UiPropSpec:
    name: str
    annotation: TypeRef | None
    mode: PropMode
    constructor_name: str | None = None
    setter_kind: AccessorKind | None = None
    setter_name: str | None = None
    getter_kind: AccessorKind | None = None
    getter_name: str | None = None
    affects_identity: bool = False


@dataclass(frozen=True, slots=True)
class UiMethodSpec:
    name: str
    mode: MethodMode
    params: tuple[UiParamSpec, ...]
    source_props: tuple[str, ...]
    fill_policy: FillPolicy
    constructor_equivalent: bool = False


@dataclass(frozen=True, slots=True)
class UiEventSpec:
    name: str
    signal_name: str
    payload_policy: EventPayloadPolicy = EventPayloadPolicy.NONE


@dataclass(frozen=True, slots=True)
class MountParamSpec:
    name: str
    annotation: TypeRef | None
    keyed: bool = False
    default_repr: str | None = None


@dataclass(frozen=True, slots=True)
class MountPointSpec:
    name: str
    accepted_produced_type: TypeRef
    params: tuple[MountParamSpec, ...] = ()
    min_children: int = 0
    max_children: int | None = None
    apply_method_name: str | None = None
    sync_method_name: str | None = None
    place_method_name: str | None = None
    append_method_name: str | None = None
    detach_method_name: str | None = None
    replay_kind: MountReplayKind = MountReplayKind.NONE
    prefer_sync: bool = False

    def instance_key(self, values: dict[str, Any]) -> tuple[object, ...]:
        return (self.name, *(values[param.name] for param in self.params if param.keyed))


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class MountState:
    mount_point: MountPointSpec
    instance_key: tuple[object, ...]
    values: frozendict[str, Any]
    objects: tuple[Any, ...]


@dataclass(frozen=True, slots=True)
class UiWidgetSpec:
    kind: str
    mounted_type_name: str
    constructor_params: frozendict[str, UiParamSpec]
    props: frozendict[str, UiPropSpec]
    methods: frozendict[str, UiMethodSpec]
    child_policy: ChildPolicy
    events: frozendict[str, UiEventSpec] = frozendict()
    mount_points: frozendict[str, MountPointSpec] = frozendict()
    default_child_mount_point_name: str | None = None
    default_attach_mount_point_names: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class UiPropLearning:
    public: bool | None = None
    signature_annotation: TypeRef | None = None
    signature_default_repr: str | None = None


@dataclass(frozen=True, slots=True)
class UiMethodLearning:
    source_props: tuple[str, ...] | None = None
    fill_policy: FillPolicy | None = None
    mode: MethodMode | None = None
    constructor_equivalent: bool | None = None


@dataclass(frozen=True, slots=True)
class UiEventLearning:
    signal_name: str
    payload_policy: EventPayloadPolicy = EventPayloadPolicy.NONE


@dataclass(frozen=True, slots=True)
class UiMountParamLearning:
    keyed: bool | None = None
    annotation: TypeRef | None = None
    default_repr: str | None = None


@dataclass(frozen=True, slots=True)
class UiMountPointLearning:
    public_name: str | None = None
    enabled: bool | None = None
    accepted_produced_type: TypeRef | None = None
    param_learnings: frozendict[str, UiMountParamLearning] = frozendict()
    default_child: bool | None = None
    default_attach_rank: int | None = None
    replay_kind: MountReplayKind | None = None
    append_method_name: str | None = None
    prefer_sync: bool | None = None


@dataclass(frozen=True, slots=True)
class UiWidgetLearning:
    public_name: str | None = None
    prop_learnings: frozendict[str, UiPropLearning] = frozendict()
    method_learnings: frozendict[str, UiMethodLearning] = frozendict()
    event_learnings: frozendict[str, UiEventLearning] = frozendict()
    mount_point_learnings: frozendict[str, UiMountPointLearning] = frozendict()


@dataclass(frozen=True, slots=True)
class UiInterfaceEntry:
    public_name: str
    kind: str


@dataclass(frozen=True, slots=True)
class UiInterface:
    name: str
    owner: type[Any] | None
    entries: frozendict[str, UiInterfaceEntry]

    def bind_owner(self, owner: type[Any]) -> UiInterface:
        return replace(self, owner=owner)

    def build_element(self, public_name: str, /, **props: Any) -> Any:
        from pyrolyze.api import UIElement

        entry = self.entries[public_name]
        return UIElement(kind=entry.kind, props=dict(props))


__all__ = [
    "AccessorKind",
    "ChildPolicy",
    "EventPayloadPolicy",
    "FillPolicy",
    "MethodMode",
    "MountReplayKind",
    "UiMountParamLearning",
    "UiMountPointLearning",
    "MountParamSpec",
    "MountPointSpec",
    "MountState",
    "PropMode",
    "TypeRef",
    "UiEventLearning",
    "UiEventSpec",
    "UiInterface",
    "UiInterfaceEntry",
    "UiMethodLearning",
    "UiMethodSpec",
    "UiParamSpec",
    "UiPropLearning",
    "UiPropSpec",
    "UiWidgetLearning",
    "UiWidgetSpec",
]
