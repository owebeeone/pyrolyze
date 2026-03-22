from __future__ import annotations

from dataclasses import dataclass

from frozendict import frozendict

from pyrolyze.api import UIElement
from pyrolyze.backends.model import (
    ChildPolicy,
    FillPolicy,
    MethodMode,
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
