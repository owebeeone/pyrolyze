"""Shared backend model types for generated UI libraries and widget specs."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any

from frozendict import frozendict


class AccessorKind(StrEnum):
    METHOD = "method"
    QT_PROPERTY = "qt_property"
    TK_CONFIG = "tk_config"
    PYTHON_PROPERTY = "python_property"


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


class FillPolicy(StrEnum):
    RETAIN_EFFECTIVE = "retain_effective"
    TOOLKIT_DEFAULT = "toolkit_default"


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
class UiWidgetSpec:
    kind: str
    mounted_type_name: str
    constructor_params: frozendict[str, UiParamSpec]
    props: frozendict[str, UiPropSpec]
    methods: frozendict[str, UiMethodSpec]
    child_policy: ChildPolicy


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
    "FillPolicy",
    "MethodMode",
    "PropMode",
    "TypeRef",
    "UiInterface",
    "UiInterfaceEntry",
    "UiMethodSpec",
    "UiParamSpec",
    "UiPropSpec",
    "UiWidgetSpec",
]
