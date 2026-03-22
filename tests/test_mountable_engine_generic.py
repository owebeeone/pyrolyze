from __future__ import annotations

from dataclasses import dataclass, field

from frozendict import frozendict
import pytest

from pyrolyze.api import UIElement
from pyrolyze.backends.model import (
    ChildPolicy,
    FillPolicy,
    MethodMode,
    MountPointSpec,
    PropMode,
    TypeRef,
    UiMethodSpec,
    UiParamSpec,
    UiPropSpec,
    UiWidgetSpec,
)
from pyrolyze.backends.mountable_engine import MountableEngine


class _FakePlacement:
    pass


@dataclass
class _FakeRemountable:
    name: str
    parent: object | None = None
    updates: list[tuple[str, object]] | None = None

    def __post_init__(self) -> None:
        if self.updates is None:
            self.updates = []

    def set_name(self, value: str) -> None:
        self.name = value
        self.updates.append(("name", value))


@dataclass
class _FakeRangeMountable:
    minimum: int = 0
    maximum: int = 0
    range_calls: list[tuple[int, int]] | None = None

    def __post_init__(self) -> None:
        if self.range_calls is None:
            self.range_calls = []

    def setRange(self, minimum: int, maximum: int) -> None:
        self.minimum = minimum
        self.maximum = maximum
        self.range_calls.append((minimum, maximum))

    def read_minimum(self) -> int:
        return self.minimum

    def read_maximum(self) -> int:
        return self.maximum


@dataclass
class _FakeA:
    name: str
    children: list[object] = field(default_factory=list)

    def sync_children(self, children: list[object]) -> None:
        self.children = list(children)


@dataclass
class _FakeB(_FakeA):
    pass


@dataclass
class _FakeC:
    name: str


@dataclass
class _FakeD:
    name: str
    children: list[object] = field(default_factory=list)

    def sync_children(self, children: list[object]) -> None:
        self.children = list(children)


@dataclass
class _FakeY:
    name: str


@dataclass
class _FakeZ:
    name: str


@dataclass
class _FakeX(_FakeY, _FakeZ):
    pass


@dataclass
class _FakeAcceptsY:
    name: str
    children: list[object] = field(default_factory=list)

    def sync_children(self, children: list[object]) -> None:
        self.children = list(children)


@dataclass
class _FakeAcceptsZ:
    name: str
    children: list[object] = field(default_factory=list)

    def sync_children(self, children: list[object]) -> None:
        self.children = list(children)


def _matrix_specs() -> dict[str, UiWidgetSpec]:
    def prop_name() -> frozendict[str, UiPropSpec]:
        return frozendict(
            {
                "name": UiPropSpec(
                    name="name",
                    annotation=TypeRef("str"),
                    mode=PropMode.CREATE_UPDATE,
                    constructor_name="name",
                )
            }
        )

    child_mount_a = MountPointSpec(
        name="standard",
        accepted_produced_type=TypeRef("tests.test_mountable_engine_generic._FakeA"),
        sync_method_name="sync_children",
    )
    child_mount_c = MountPointSpec(
        name="standard",
        accepted_produced_type=TypeRef("tests.test_mountable_engine_generic._FakeC"),
        sync_method_name="sync_children",
    )
    return {
        "A": UiWidgetSpec(
            kind="A",
            mounted_type_name="tests.test_mountable_engine_generic._FakeA",
            constructor_params=frozendict({"name": UiParamSpec(name="name", annotation=TypeRef("str"))}),
            props=prop_name(),
            methods=frozendict(),
            child_policy=ChildPolicy.NONE,
            mount_points=frozendict({"standard": child_mount_a}),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
        "B": UiWidgetSpec(
            kind="B",
            mounted_type_name="tests.test_mountable_engine_generic._FakeB",
            constructor_params=frozendict({"name": UiParamSpec(name="name", annotation=TypeRef("str"))}),
            props=prop_name(),
            methods=frozendict(),
            child_policy=ChildPolicy.NONE,
            mount_points=frozendict({"standard": child_mount_c}),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
        "C": UiWidgetSpec(
            kind="C",
            mounted_type_name="tests.test_mountable_engine_generic._FakeC",
            constructor_params=frozendict({"name": UiParamSpec(name="name", annotation=TypeRef("str"))}),
            props=prop_name(),
            methods=frozendict(),
            child_policy=ChildPolicy.NONE,
        ),
        "D": UiWidgetSpec(
            kind="D",
            mounted_type_name="tests.test_mountable_engine_generic._FakeD",
            constructor_params=frozendict({"name": UiParamSpec(name="name", annotation=TypeRef("str"))}),
            props=prop_name(),
            methods=frozendict(),
            child_policy=ChildPolicy.NONE,
            mount_points=frozendict({"standard": child_mount_a}),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
    }


def _multi_inheritance_specs() -> dict[str, UiWidgetSpec]:
    def prop_name() -> frozendict[str, UiPropSpec]:
        return frozendict(
            {
                "name": UiPropSpec(
                    name="name",
                    annotation=TypeRef("str"),
                    mode=PropMode.CREATE_UPDATE,
                    constructor_name="name",
                )
            }
        )

    mount_y = MountPointSpec(
        name="standard",
        accepted_produced_type=TypeRef("tests.test_mountable_engine_generic._FakeY"),
        sync_method_name="sync_children",
    )
    mount_z = MountPointSpec(
        name="standard",
        accepted_produced_type=TypeRef("tests.test_mountable_engine_generic._FakeZ"),
        sync_method_name="sync_children",
    )
    return {
        "AcceptsY": UiWidgetSpec(
            kind="AcceptsY",
            mounted_type_name="tests.test_mountable_engine_generic._FakeAcceptsY",
            constructor_params=frozendict({"name": UiParamSpec(name="name", annotation=TypeRef("str"))}),
            props=prop_name(),
            methods=frozendict(),
            child_policy=ChildPolicy.NONE,
            mount_points=frozendict({"standard": mount_y}),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
        "AcceptsZ": UiWidgetSpec(
            kind="AcceptsZ",
            mounted_type_name="tests.test_mountable_engine_generic._FakeAcceptsZ",
            constructor_params=frozendict({"name": UiParamSpec(name="name", annotation=TypeRef("str"))}),
            props=prop_name(),
            methods=frozendict(),
            child_policy=ChildPolicy.NONE,
            mount_points=frozendict({"standard": mount_z}),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
        "X": UiWidgetSpec(
            kind="X",
            mounted_type_name="tests.test_mountable_engine_generic._FakeX",
            constructor_params=frozendict({"name": UiParamSpec(name="name", annotation=TypeRef("str"))}),
            props=prop_name(),
            methods=frozendict(),
            child_policy=ChildPolicy.NONE,
        ),
    }


def test_mountable_engine_uses_hooks_for_create_only_remount() -> None:
    spec = UiWidgetSpec(
        kind="FakeRemountable",
        mounted_type_name="tests.test_mountable_engine_generic._FakeRemountable",
        constructor_params=frozendict(
            {
                "name": UiParamSpec(name="name", annotation=TypeRef("str")),
                "parent": UiParamSpec(name="parent", annotation=TypeRef("object")),
            }
        ),
        props=frozendict(
            {
                "name": UiPropSpec(
                    name="name",
                    annotation=TypeRef("str"),
                    mode=PropMode.CREATE_UPDATE,
                    constructor_name="name",
                    setter_kind=None,
                ),
                "parent": UiPropSpec(
                    name="parent",
                    annotation=TypeRef("object"),
                    mode=PropMode.CREATE_ONLY_REMOUNT,
                    constructor_name="parent",
                ),
            }
        ),
        methods=frozendict(),
        child_policy=ChildPolicy.NONE,
    )
    captured: list[tuple[str, object]] = []

    engine = MountableEngine(
        {"FakeRemountable": spec},
        capture_placement=lambda mountable: _FakePlacement(),
        restore_placement=lambda mountable, placement: captured.append(("restore", placement)),
        dispose_mountable=lambda mountable: captured.append(("dispose", mountable)),
    )
    parent_a = object()
    parent_b = object()

    node = engine.mount(
        UIElement(kind="FakeRemountable", props={"name": "One", "parent": parent_a}),
        slot_id=("root", 1),
        call_site_id=11,
    )
    first_mountable = node.mountable

    updated = engine.update(
        node,
        UIElement(kind="FakeRemountable", props={"name": "One", "parent": parent_b}),
    )

    assert updated is node
    assert node.mountable is not first_mountable
    assert node.effective_props == {"name": "One", "parent": parent_b}
    assert len(captured) == 2
    assert captured[0][0] == "restore"
    assert captured[1] == ("dispose", first_mountable)


def test_mountable_engine_uses_read_hook_for_retain_effective_method_backfill() -> None:
    spec = UiWidgetSpec(
        kind="FakeRange",
        mounted_type_name="tests.test_mountable_engine_generic._FakeRangeMountable",
        constructor_params=frozendict(),
        props=frozendict(
            {
                "minimum": UiPropSpec(
                    name="minimum",
                    annotation=TypeRef("int"),
                    mode=PropMode.CREATE_UPDATE,
                    getter_kind=None,
                ),
                "maximum": UiPropSpec(
                    name="maximum",
                    annotation=TypeRef("int"),
                    mode=PropMode.CREATE_UPDATE,
                    getter_kind=None,
                ),
            }
        ),
        methods=frozendict(
            {
                "setRange": UiMethodSpec(
                    name="setRange",
                    mode=MethodMode.CREATE_UPDATE,
                    params=(
                        UiParamSpec(name="minimum", annotation=TypeRef("int")),
                        UiParamSpec(name="maximum", annotation=TypeRef("int")),
                    ),
                    source_props=("minimum", "maximum"),
                    fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                    constructor_equivalent=True,
                ),
            }
        ),
        child_policy=ChildPolicy.NONE,
    )

    def read_current(mountable: object, _spec: UiWidgetSpec, prop_name: str) -> object:
        target = mountable
        if prop_name == "minimum":
            return target.read_minimum()
        if prop_name == "maximum":
            return target.read_maximum()
        return object()

    engine = MountableEngine({"FakeRange": spec}, read_current_prop_value=read_current)

    node = engine.mount(
        UIElement(kind="FakeRange", props={"minimum": 1, "maximum": 10}),
        slot_id=("root", 2),
        call_site_id=22,
    )

    updated = engine.update(
        node,
        UIElement(kind="FakeRange", props={"maximum": 12}),
    )

    assert updated is node
    assert node.effective_props == {"minimum": 1, "maximum": 12}
    assert node.mountable.range_calls == [(1, 10), (1, 12)]


def test_mountable_engine_preserves_old_tree_when_parent_kind_remount_becomes_incompatible() -> None:
    engine = MountableEngine(_matrix_specs())

    node = engine.mount(
        UIElement(
            kind="B",
            props={"name": "parent-b"},
            children=(UIElement(kind="C", props={"name": "child-c"}),),
        ),
        slot_id=("root", "matrix", 1),
        call_site_id=51,
    )

    original_mountable = node.mountable
    original_child_mountable = node.child_nodes[0].mountable

    with pytest.raises(ValueError, match="Cannot attach child kind 'C' to parent 'A'"):
        engine.update(
            node,
            UIElement(
                kind="A",
                props={"name": "parent-a"},
                children=(UIElement(kind="C", props={"name": "child-c"}),),
            ),
        )

    assert node.mountable is original_mountable
    assert isinstance(node.mountable, _FakeB)
    assert node.child_nodes[0].mountable is original_child_mountable
    assert isinstance(node.child_nodes[0].mountable, _FakeC)
    assert node.element.kind == "B"


def test_mountable_engine_preserves_old_tree_when_child_update_becomes_incompatible() -> None:
    engine = MountableEngine(_matrix_specs())

    node = engine.mount(
        UIElement(
            kind="B",
            props={"name": "parent-b"},
            children=(UIElement(kind="C", props={"name": "child-c"}),),
        ),
        slot_id=("root", "matrix", 2),
        call_site_id=52,
    )

    original_mountable = node.mountable
    original_child_mountable = node.child_nodes[0].mountable

    with pytest.raises(ValueError, match="Cannot attach child kind 'D' to parent 'B'"):
        engine.update(
            node,
            UIElement(
                kind="B",
                props={"name": "parent-b"},
                children=(UIElement(kind="D", props={"name": "child-d"}),),
            ),
        )

    assert node.mountable is original_mountable
    assert isinstance(node.mountable, _FakeB)
    assert node.child_nodes[0].mountable is original_child_mountable
    assert isinstance(node.child_nodes[0].mountable, _FakeC)
    assert node.element.children[0].kind == "C"


def test_mountable_engine_allows_child_when_new_parent_accepts_alternate_base() -> None:
    engine = MountableEngine(_multi_inheritance_specs())

    node = engine.mount(
        UIElement(
            kind="AcceptsY",
            props={"name": "parent-y"},
            children=(UIElement(kind="X", props={"name": "child-x"}),),
        ),
        slot_id=("root", "matrix", 3),
        call_site_id=53,
    )

    updated = engine.update(
        node,
        UIElement(
            kind="AcceptsZ",
            props={"name": "parent-z"},
            children=(UIElement(kind="X", props={"name": "child-x"}),),
        ),
    )

    assert updated is node
    assert isinstance(node.mountable, _FakeAcceptsZ)
    assert len(node.child_nodes) == 1
    assert isinstance(node.child_nodes[0].mountable, _FakeX)
    assert node.element.kind == "AcceptsZ"
