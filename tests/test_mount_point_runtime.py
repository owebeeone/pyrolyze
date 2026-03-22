from __future__ import annotations

from frozendict import frozendict

from pyrolyze.backends.mounts import (
    ImmutableOrderedMountState,
    OrderedMountStateBuilder,
    MountOp,
    MountedRef,
    apply_mount_state,
    choose_mount_applier,
    resolve_mount_ops,
)
from pyrolyze.backends.model import MountPointSpec, MountReplayKind, MountState, TypeRef
from pyrolyze.testing.hydo import (
    HYDO_MOUNTABLE_SPECS,
    HydoGridLayout,
    HydoMenu,
    HydoWidget,
    HydoWindow,
)


def _ordered_state(*mountables: object, revision: int = 1) -> ImmutableOrderedMountState[object]:
    refs = tuple(MountedRef(node_id=("node", index), value=value) for index, value in enumerate(mountables))
    return ImmutableOrderedMountState(revision=revision, objects=refs)


class _AnchorOrderedParent:
    def __init__(self) -> None:
        self.actions: list[object] = []
        self.operations: list[tuple[str, tuple[object, ...]]] = []

    def addAction(self, action: object) -> None:
        self.actions.append(action)
        self.operations.append(("addAction", (action,)))

    def insertAction(self, before: object, action: object) -> None:
        index = self.actions.index(before)
        if action in self.actions:
            self.actions.remove(action)
            index = self.actions.index(before)
        self.actions.insert(index, action)
        self.operations.append(("insertAction", (before, action)))

    def removeAction(self, action: object) -> None:
        if action in self.actions:
            self.actions.remove(action)
        self.operations.append(("removeAction", (action,)))


class _AppendOnlyParent:
    def __init__(self) -> None:
        self.children: list[object] = []
        self.operations: list[tuple[str, tuple[object, ...]]] = []

    def add(self, child: object) -> None:
        self.children.append(child)
        self.operations.append(("add", (child,)))

    def remove(self, child: object) -> None:
        if child in self.children:
            self.children.remove(child)
        self.operations.append(("remove", (child,)))


def _anchor_mount_point() -> MountPointSpec:
    return MountPointSpec(
        name="action",
        accepted_produced_type=TypeRef("Action"),
        max_children=None,
        place_method_name="insertAction",
        detach_method_name="removeAction",
    )


def _append_only_mount_point() -> MountPointSpec:
    return MountPointSpec(
        name="pane",
        accepted_produced_type=TypeRef("Pane"),
        max_children=None,
        append_method_name="add",
        detach_method_name="remove",
        replay_kind=MountReplayKind.INDEX,
    )


def test_ordered_mount_state_builder_builds_immutable_state_with_ops() -> None:
    first = MountedRef(node_id=("node", 1), value=HydoWidget(name="first"))
    second = MountedRef(node_id=("node", 2), value=HydoWidget(name="second"))

    builder = OrderedMountStateBuilder.empty()
    builder.place(0, first)
    builder.place(1, second)
    state = builder.build()

    assert state.revision == 1
    assert state.objects == (first, second)
    assert state.ops == (
        MountOp(kind="place", index=0, ref=first),
        MountOp(kind="place", index=1, ref=second),
    )


def test_resolve_mount_ops_discovers_sync_and_replay_for_hydo_standard_mount() -> None:
    standard_mount = HYDO_MOUNTABLE_SPECS["HydoWidget"].mount_points["standard"]

    ops = resolve_mount_ops(HydoWidget, standard_mount)

    assert ops.sync is not None
    assert ops.place is not None
    assert ops.detach is not None
    assert resolve_mount_ops(HydoWidget, standard_mount) is ops


def test_resolve_mount_ops_discovers_anchor_replay_for_before_style_mounts() -> None:
    ops = resolve_mount_ops(_AnchorOrderedParent, _anchor_mount_point())

    assert ops.place is None
    assert ops.place_before is not None
    assert ops.detach is not None


def test_choose_mount_applier_prefers_incremental_replay_for_small_ordered_delta() -> None:
    standard_mount = HYDO_MOUNTABLE_SPECS["HydoWidget"].mount_points["standard"]
    old_state = _ordered_state(HydoWidget(name="a"), HydoWidget(name="b"), revision=1)

    builder = OrderedMountStateBuilder.from_state(old_state)
    moved = old_state.objects[1]
    builder.place(0, moved)
    new_state = builder.build()

    plan = choose_mount_applier(
        mount_point=standard_mount,
        old_state=old_state,
        new_state=new_state,
        resolved_ops=resolve_mount_ops(HydoWidget, standard_mount),
    )

    assert plan.kind == "incremental_ordered_replay"


def test_choose_mount_applier_prefers_full_rebuild_for_large_replay_only_delta() -> None:
    mount_point = _anchor_mount_point()
    old_state = _ordered_state("a", "b", "c", "d", "e", "f", "g", "h", "i", revision=1)

    builder = OrderedMountStateBuilder.from_state(old_state)
    for _ in range(9):
        builder.place(0, old_state.objects[-1])
    new_state = builder.build()

    plan = choose_mount_applier(
        mount_point=mount_point,
        old_state=old_state,
        new_state=new_state,
        resolved_ops=resolve_mount_ops(_AnchorOrderedParent, mount_point),
    )

    assert plan.kind == "full_rebuild_fallback"


def test_apply_mount_state_uses_sync_for_initial_standard_mount() -> None:
    parent = HydoWidget(name="parent")
    standard_mount = HYDO_MOUNTABLE_SPECS["HydoWidget"].mount_points["standard"]
    first = HydoWidget(name="first")
    second = HydoWidget(name="second")

    state = MountState(
        mount_point=standard_mount,
        instance_key=standard_mount.instance_key({}),
        values=frozendict(),
        objects=_ordered_state(first, second).objects,
    )

    apply_mount_state(parent, old_state=None, new_state=state)

    assert [child.name for child in parent.children] == ["first", "second"]
    assert parent.operations[-1].method == "sync_children"


def test_apply_mount_state_replays_small_standard_delta_with_place_api() -> None:
    parent = HydoWidget(name="parent")
    standard_mount = HYDO_MOUNTABLE_SPECS["HydoWidget"].mount_points["standard"]
    first = HydoWidget(name="first")
    second = HydoWidget(name="second")
    third = HydoWidget(name="third")

    old_order = _ordered_state(first, second, revision=1)
    old_state = MountState(
        mount_point=standard_mount,
        instance_key=standard_mount.instance_key({}),
        values=frozendict(),
        objects=old_order.objects,
    )
    apply_mount_state(parent, old_state=None, new_state=old_state)

    builder = OrderedMountStateBuilder.from_state(old_order)
    builder.place(0, old_order.objects[1])
    builder.place(2, MountedRef(node_id=("node", 3), value=third))
    new_order = builder.build()
    new_state = MountState(
        mount_point=standard_mount,
        instance_key=standard_mount.instance_key({}),
        values=frozendict(),
        objects=new_order.objects,
    )

    apply_mount_state(parent, old_state=old_state, new_state=new_state, ordered_state=new_order)

    assert [child.name for child in parent.children] == ["second", "first", "third"]
    assert [op.method for op in parent.operations[-2:]] == ["place_child", "place_child"]


def test_apply_mount_state_uses_full_rebuild_for_initial_anchor_mount() -> None:
    parent = _AnchorOrderedParent()
    mount_point = _anchor_mount_point()
    first = "first"
    second = "second"
    state = MountState(
        mount_point=mount_point,
        instance_key=mount_point.instance_key({}),
        values=frozendict(),
        objects=_ordered_state(first, second).objects,
    )

    apply_mount_state(parent, old_state=None, new_state=state)

    assert parent.actions == [first, second]
    assert [name for name, _ in parent.operations] == ["addAction", "addAction"]


def test_apply_mount_state_uses_append_only_full_rebuild_when_insert_is_unavailable() -> None:
    parent = _AppendOnlyParent()
    mount_point = _append_only_mount_point()
    first = "first"
    second = "second"

    state = MountState(
        mount_point=mount_point,
        instance_key=mount_point.instance_key({}),
        values=frozendict(),
        objects=_ordered_state(first, second).objects,
    )

    apply_mount_state(parent, old_state=None, new_state=state)

    assert parent.children == [first, second]
    assert parent.operations == [("add", (first,)), ("add", (second,))]


def test_apply_mount_state_rebuilds_append_only_mounts_in_new_order() -> None:
    parent = _AppendOnlyParent()
    mount_point = _append_only_mount_point()
    first = "first"
    second = "second"
    third = "third"

    old_state = MountState(
        mount_point=mount_point,
        instance_key=mount_point.instance_key({}),
        values=frozendict(),
        objects=_ordered_state(first, second).objects,
    )
    apply_mount_state(parent, old_state=None, new_state=old_state)
    parent.operations.clear()

    new_state = MountState(
        mount_point=mount_point,
        instance_key=mount_point.instance_key({}),
        values=frozendict(),
        objects=_ordered_state(third, first).objects,
    )

    apply_mount_state(parent, old_state=old_state, new_state=new_state)

    assert parent.children == [third, first]
    assert parent.operations == [
        ("remove", (first,)),
        ("remove", (second,)),
        ("add", (third,)),
        ("add", (first,)),
    ]


def test_apply_mount_state_replays_small_anchor_delta_with_place_before() -> None:
    parent = _AnchorOrderedParent()
    mount_point = _anchor_mount_point()
    first = "first"
    second = "second"
    third = "third"

    old_order = _ordered_state(first, second, third, revision=1)
    old_state = MountState(
        mount_point=mount_point,
        instance_key=mount_point.instance_key({}),
        values=frozendict(),
        objects=old_order.objects,
    )
    apply_mount_state(parent, old_state=None, new_state=old_state)
    parent.operations.clear()

    builder = OrderedMountStateBuilder.from_state(old_order)
    builder.place(0, old_order.objects[2])
    new_order = builder.build()
    new_state = MountState(
        mount_point=mount_point,
        instance_key=mount_point.instance_key({}),
        values=frozendict(),
        objects=new_order.objects,
    )

    apply_mount_state(parent, old_state=old_state, new_state=new_state, ordered_state=new_order)

    assert parent.actions == [third, first, second]
    assert parent.operations == [("insertAction", (first, third))]


def test_apply_mount_state_handles_keyed_single_mount() -> None:
    parent = HydoWidget(name="parent")
    mount_point = HYDO_MOUNTABLE_SPECS["HydoWidget"].mount_points["corner_widget"]
    child = HydoMenu(name="menu")

    state = MountState(
        mount_point=mount_point,
        instance_key=mount_point.instance_key({"corner": "top_left"}),
        values=frozendict({"corner": "top_left"}),
        objects=(MountedRef(node_id=("node", 1), value=child),),
    )

    apply_mount_state(parent, old_state=None, new_state=state)

    assert parent.corner_widgets["top_left"] is child
    assert parent.operations[-1].method == "set_corner_widget"


def test_apply_mount_state_handles_keyed_single_mount_with_non_keyed_values() -> None:
    parent = HydoGridLayout(name="grid")
    mount_point = HYDO_MOUNTABLE_SPECS["HydoGridLayout"].mount_points["cell_widget"]
    child = HydoWidget(name="cell")

    state = MountState(
        mount_point=mount_point,
        instance_key=mount_point.instance_key({"row": 2, "column": 3, "row_span": 1, "column_span": 2}),
        values=frozendict({"row": 2, "column": 3, "row_span": 1, "column_span": 2}),
        objects=(MountedRef(node_id=("node", 1), value=child),),
    )

    apply_mount_state(parent, old_state=None, new_state=state)

    assert parent.cells[(2, 3)] is child
    assert parent.operations[-1].method == "set_cell_widget"
    assert parent.operations[-1].kwargs == (("column_span", 2), ("row_span", 1))


def test_apply_mount_state_enforces_single_mount_limits() -> None:
    parent = HydoWindow(name="window")
    mount_point = HYDO_MOUNTABLE_SPECS["HydoWindow"].mount_points["main_widget"]

    state = MountState(
        mount_point=mount_point,
        instance_key=mount_point.instance_key({}),
        values=frozendict(),
        objects=(
            MountedRef(node_id=("node", 1), value=HydoWidget(name="first")),
            MountedRef(node_id=("node", 2), value=HydoWidget(name="second")),
        ),
    )

    try:
        apply_mount_state(parent, old_state=None, new_state=state)
    except ValueError as exc:
        assert "max_children" in str(exc)
    else:
        raise AssertionError("expected single-mount validation failure")
