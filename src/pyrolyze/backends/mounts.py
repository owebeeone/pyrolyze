from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from inspect import signature
from typing import Any, Callable, Generic, Literal, Mapping, Sequence, TypeVar

from frozendict import frozendict

from .model import MountPointSpec, MountState

T = TypeVar("T")

_CHILD_GEOMETRY_SYNC_METHODS = frozenset({"pack", "grid", "place"})
_CHILD_GEOMETRY_FORGET_METHODS = frozenset({"pack_forget", "grid_forget", "place_forget"})


@dataclass(frozen=True, slots=True)
class MountedRef(Generic[T]):
    node_id: object
    value: T


@dataclass(frozen=True, slots=True)
class MountOp(Generic[T]):
    kind: Literal["place", "detach", "clear"]
    index: int | None = None
    ref: MountedRef[T] | None = None


@dataclass(frozen=True, slots=True)
class ImmutableOrderedMountState(Generic[T]):
    revision: int
    objects: tuple[MountedRef[T], ...]
    ops: tuple[MountOp[T], ...] = ()


@dataclass(slots=True)
class OrderedMountStateBuilder(Generic[T]):
    _base: ImmutableOrderedMountState[T]
    _working: list[MountedRef[T]]
    _ops: list[MountOp[T]]

    @classmethod
    def empty(cls) -> OrderedMountStateBuilder[T]:
        return cls(
            _base=ImmutableOrderedMountState(revision=0, objects=()),
            _working=[],
            _ops=[],
        )

    @classmethod
    def from_state(cls, state: ImmutableOrderedMountState[T]) -> OrderedMountStateBuilder[T]:
        return cls(
            _base=state,
            _working=list(state.objects),
            _ops=[],
        )

    def place(self, index: int, ref: MountedRef[T]) -> None:
        self._working = [existing for existing in self._working if existing.node_id != ref.node_id]
        if index < 0:
            index = 0
        if index > len(self._working):
            index = len(self._working)
        self._working.insert(index, ref)
        self._ops.append(MountOp(kind="place", index=index, ref=ref))

    def detach(self, ref: MountedRef[T]) -> None:
        self._working = [existing for existing in self._working if existing.node_id != ref.node_id]
        self._ops.append(MountOp(kind="detach", ref=ref))

    def clear(self) -> None:
        self._working.clear()
        self._ops.append(MountOp(kind="clear"))

    def current_objects(self) -> tuple[MountedRef[T], ...]:
        return tuple(self._working)

    def build(self) -> ImmutableOrderedMountState[T]:
        return ImmutableOrderedMountState(
            revision=self._base.revision + 1,
            objects=tuple(self._working),
            ops=tuple(self._ops),
        )


@dataclass(frozen=True, slots=True)
class ResolvedMountOps:
    apply: Callable[[object, MountState], None] | None = None
    sync: Callable[[object, Sequence[MountState]], None] | None = None
    place: Callable[[object, object, int], None] | None = None
    place_before: Callable[[object, object, object | None], None] | None = None
    append: Callable[[object, object], None] | None = None
    detach: Callable[[object, object], None] | None = None
    capture_snapshot: Callable[[object], object] | None = None
    restore_snapshot: Callable[[object, object], None] | None = None


@dataclass(frozen=True, slots=True)
class MountApplierPlan:
    kind: Literal[
        "skip",
        "direct_sync",
        "incremental_ordered_replay",
        "per_instance_apply",
        "full_rebuild_fallback",
    ]


@lru_cache
def resolve_mount_ops(parent_type: type[object], mount_point: MountPointSpec) -> ResolvedMountOps:
    apply = None
    if mount_point.apply_method_name in _CHILD_GEOMETRY_SYNC_METHODS:
        method_name = mount_point.apply_method_name

        def apply(parent: object, state: MountState, *, _method_name: str = method_name) -> None:
            _apply_child_single_mount(parent, state, _method_name)
    elif mount_point.apply_method_name and hasattr(parent_type, mount_point.apply_method_name):
        method_name = mount_point.apply_method_name

        def apply(parent: object, state: MountState, *, _method_name: str = method_name) -> None:
            _apply_single_mount(parent, state, _method_name)

    sync = None
    if mount_point.sync_method_name in _CHILD_GEOMETRY_SYNC_METHODS:
        method_name = mount_point.sync_method_name
        detach_name = mount_point.detach_method_name or _child_geometry_forget_method_name(method_name)

        def sync(
            parent: object,
            states: Sequence[MountState],
            *,
            _method_name: str = method_name,
            _detach_name: str | None = detach_name,
        ) -> None:
            _sync_child_geometry_mount(parent, states, _method_name, _detach_name)
    elif mount_point.sync_method_name and hasattr(parent_type, mount_point.sync_method_name):
        method_name = mount_point.sync_method_name

        def sync(parent: object, states: Sequence[MountState], *, _method_name: str = method_name) -> None:
            for state in states:
                values = [ref.value for ref in state.objects]
                getattr(parent, _method_name)(values)

    place = None
    place_before = None
    append = None
    detach = None
    place_name, detach_name = _ordered_fallback_method_names(mount_point)
    if detach_name is None and mount_point.max_children == 1:
        detach_name = _single_mount_detach_method_name(mount_point)
    if place_name is None and mount_point.name == "standard":
        place_name = "place_child" if hasattr(parent_type, "place_child") else None
    if detach_name is None and mount_point.name == "standard":
        detach_name = "detach_child" if hasattr(parent_type, "detach_child") else None
    append_name = mount_point.append_method_name
    if append_name is None and place_name is not None:
        append_name = _ordered_append_method_name(place_name)
    if append_name and hasattr(parent_type, append_name):

        def append(parent: object, value: object, *, _method_name: str = append_name) -> None:
            getattr(parent, _method_name)(value)

    if place_name and hasattr(parent_type, place_name):
        call_shape = _ordered_place_call_shape(parent_type, place_name)
        if call_shape == "anchor_before":
            append_method_name = append_name

            def place_before(
                parent: object,
                value: object,
                before: object | None,
                *,
                _method_name: str = place_name,
                _append_method_name: str | None = append_method_name,
            ) -> None:
                if before is None and _append_method_name and hasattr(parent, _append_method_name):
                    getattr(parent, _append_method_name)(value)
                    return
                getattr(parent, _method_name)(before, value)

        else:

            def place(
                parent: object,
                value: object,
                index: int,
                *,
                _method_name: str = place_name,
                _call_shape: Literal["index_first", "value_first"] = call_shape,
            ) -> None:
                if _call_shape == "index_first":
                    getattr(parent, _method_name)(index, value)
                    return
                getattr(parent, _method_name)(value, index)

    if detach_name in _CHILD_GEOMETRY_FORGET_METHODS:

        def detach(parent: object, value: object, *, _method_name: str = detach_name) -> None:
            getattr(value, _method_name)()
    elif detach_name and hasattr(parent_type, detach_name):

        def detach(parent: object, value: object, *, _method_name: str = detach_name) -> None:
            getattr(parent, _method_name)(value)

    return ResolvedMountOps(
        apply=apply,
        sync=sync,
        place=place,
        place_before=place_before,
        append=append,
        detach=detach,
    )


def choose_mount_applier(
    *,
    mount_point: MountPointSpec,
    old_state: ImmutableOrderedMountState[Any] | None,
    new_state: ImmutableOrderedMountState[Any],
    resolved_ops: ResolvedMountOps,
) -> MountApplierPlan:
    if old_state is not None and old_state == new_state:
        return MountApplierPlan(kind="skip")

    is_ordered = mount_point.max_children is None or mount_point.max_children > 1
    has_replay = (
        (resolved_ops.place is not None or resolved_ops.place_before is not None)
        and resolved_ops.detach is not None
    )
    has_sync = resolved_ops.sync is not None
    has_apply = resolved_ops.apply is not None

    if not is_ordered:
        if has_apply:
            return MountApplierPlan(kind="per_instance_apply")
        if has_sync:
            return MountApplierPlan(kind="direct_sync")
        return MountApplierPlan(kind="full_rebuild_fallback")

    if old_state is None:
        if has_sync:
            return MountApplierPlan(kind="direct_sync")
        return MountApplierPlan(kind="full_rebuild_fallback")

    if has_replay and _is_small_replay_delta(old_state, new_state):
        return MountApplierPlan(kind="incremental_ordered_replay")
    if has_sync:
        return MountApplierPlan(kind="direct_sync")
    if has_replay:
        return MountApplierPlan(kind="full_rebuild_fallback")
    return MountApplierPlan(kind="full_rebuild_fallback")


def apply_mount_state(
    parent: object,
    *,
    old_state: MountState | None,
    new_state: MountState,
    ordered_state: ImmutableOrderedMountState[Any] | None = None,
) -> None:
    _validate_mount_state(new_state)
    resolved = resolve_mount_ops(type(parent), new_state.mount_point)

    if new_state.mount_point.max_children == 1:
        old_value = None if old_state is None or not old_state.objects else old_state.objects[0].value
        new_value = None if not new_state.objects else new_state.objects[0].value
        if new_value is None:
            if old_value is None:
                return
            if resolved.detach is not None:
                resolved.detach(parent, old_value)
                return
        if resolved.apply is not None:
            if old_value is not None and old_value is not new_value and resolved.detach is not None:
                resolved.detach(parent, old_value)
            resolved.apply(parent, new_state)
            return
        if resolved.sync is not None:
            resolved.sync(parent, (new_state,))
            return
        raise ValueError(f"mount point {new_state.mount_point.name!r} has no applicable ops")

    next_ordered = ordered_state or ImmutableOrderedMountState(
        revision=(1 if old_state is None else 0),
        objects=tuple(new_state.objects),
        ops=(),
    )
    previous_ordered = (
        None
        if old_state is None
        else ImmutableOrderedMountState(revision=0, objects=tuple(old_state.objects), ops=())
    )
    plan = choose_mount_applier(
        mount_point=new_state.mount_point,
        old_state=previous_ordered,
        new_state=next_ordered,
        resolved_ops=resolved,
    )

    if plan.kind == "skip":
        return
    if plan.kind == "incremental_ordered_replay":
        _replay_mount_ops(parent, previous_ordered, next_ordered, resolved)
        return
    if plan.kind == "direct_sync":
        if resolved.sync is None:
            raise ValueError("direct sync selected without sync op")
        resolved.sync(parent, (new_state,))
        return
    if plan.kind == "full_rebuild_fallback":
        _full_rebuild_ordered_mount(parent, old_state, new_state, resolved)
        return
    raise ValueError(f"unexpected mount applier plan {plan.kind!r}")


def _validate_mount_state(state: MountState) -> None:
    max_children = state.mount_point.max_children
    if max_children is not None and len(state.objects) > max_children:
        raise ValueError(
            f"mount point {state.mount_point.name!r} exceeds max_children={max_children}"
        )


def _apply_single_mount(parent: object, state: MountState, method_name: str) -> None:
    args, kwargs = _mount_call_args(state)
    all_args = _mount_all_args(state)
    if len(state.objects) > 1:
        raise ValueError(f"single mount point {state.mount_point.name!r} requires at most one object")
    value = None if not state.objects else state.objects[0].value
    method = getattr(parent, method_name)
    attempts = [
        (lambda: method(*args, value, **kwargs)),
        (lambda: method(value, *args, **kwargs)),
    ]
    if kwargs:
        attempts.extend(
            [
                (lambda: method(*all_args, value)),
                (lambda: method(value, *all_args)),
            ]
        )
    last_error: Exception | None = None
    for attempt in attempts:
        try:
            attempt()
            return
        except (TypeError, AttributeError) as exc:
            last_error = exc
    if last_error is not None:
        raise last_error


def _apply_child_single_mount(parent: object, state: MountState, method_name: str) -> None:
    if len(state.objects) > 1:
        raise ValueError(f"single mount point {state.mount_point.name!r} requires at most one object")
    if not state.objects:
        return
    value = state.objects[0].value
    resolved_values = _mount_resolved_values(state)
    if "in" not in resolved_values and "in_" not in resolved_values:
        resolved_values["in_"] = parent
    getattr(value, method_name)(**resolved_values)


def _mount_call_args(state: MountState) -> tuple[tuple[Any, ...], dict[str, Any]]:
    keyed_values = iter(state.instance_key[1:])
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    for param in state.mount_point.params:
        if param.keyed:
            value = next(keyed_values)
        else:
            if param.name not in state.values:
                continue
            value = state.values[param.name]
        if param.keyed:
            args.append(value)
        else:
            kwargs[param.name] = value
    return tuple(args), kwargs


def _mount_all_args(state: MountState) -> tuple[Any, ...]:
    keyed_values = iter(state.instance_key[1:])
    args: list[Any] = []
    for param in state.mount_point.params:
        if param.keyed:
            args.append(next(keyed_values))
            continue
        if param.name not in state.values:
            continue
        args.append(state.values[param.name])
    return tuple(args)


def _mount_resolved_values(state: MountState) -> dict[str, Any]:
    keyed_values = iter(state.instance_key[1:])
    resolved: dict[str, Any] = {}
    for param in state.mount_point.params:
        if param.keyed:
            resolved[param.name] = next(keyed_values)
            continue
        if param.name not in state.values:
            continue
        resolved[param.name] = state.values[param.name]
    return resolved


def _sync_child_geometry_mount(
    parent: object,
    states: Sequence[MountState],
    method_name: str,
    detach_name: str | None,
) -> None:
    if method_name == "pack":
        _sync_child_pack_mount(parent, states, detach_name)
        return
    if method_name == "grid":
        _sync_child_grid_mount(parent, states, detach_name)
        return
    if detach_name is not None:
        manager_query_name = f"{method_name}_slaves"
        manager_query = getattr(parent, manager_query_name, None)
        if callable(manager_query):
            for child in tuple(manager_query()):
                getattr(child, detach_name)()
    for state in states:
        resolved_values = _mount_resolved_values(state)
        if "in" not in resolved_values and "in_" not in resolved_values:
            resolved_values["in_"] = parent
        for ref in state.objects:
            getattr(ref.value, method_name)(**resolved_values)


def _sync_child_pack_mount(
    parent: object,
    states: Sequence[MountState],
    detach_name: str | None,
) -> None:
    desired = _flatten_child_geometry_entries(parent, states)
    desired_ids = {id(widget) for widget, _values in desired}
    manager_query = getattr(parent, "pack_slaves", None)
    current_children = tuple(manager_query()) if callable(manager_query) else ()
    if detach_name is not None:
        for child in current_children:
            if id(child) in desired_ids:
                continue
            if getattr(child, "winfo_manager", lambda: "")() != "pack":
                continue
            getattr(child, detach_name)()

    anchor: object | None = None
    for child, values in reversed(desired):
        if getattr(child, "winfo_manager", lambda: "")() == "pack":
            if _pack_geometry_matches(parent, child, before=anchor, values=values):
                anchor = child
                continue
            configure_values = {
                key: value
                for key, value in values.items()
                if key not in {"in", "in_"}
            }
            if anchor is not None:
                configure_values["before"] = anchor
            getattr(child, "pack_configure")(**configure_values)
        else:
            place_values = dict(values)
            if anchor is not None:
                place_values["before"] = anchor
            getattr(child, "pack")(**place_values)
        anchor = child


def _sync_child_grid_mount(
    parent: object,
    states: Sequence[MountState],
    detach_name: str | None,
) -> None:
    desired = _flatten_child_geometry_entries(parent, states)
    desired_ids = {id(widget) for widget, _values in desired}
    manager_query = getattr(parent, "grid_slaves", None)
    current_children = tuple(manager_query()) if callable(manager_query) else ()
    if detach_name is not None:
        for child in current_children:
            if id(child) in desired_ids:
                continue
            if getattr(child, "winfo_manager", lambda: "")() != "grid":
                continue
            getattr(child, detach_name)()

    for child, values in desired:
        if getattr(child, "winfo_manager", lambda: "")() == "grid":
            configure_values = {
                key: value
                for key, value in values.items()
                if key not in {"in", "in_"}
            }
            getattr(child, "grid_configure")(**configure_values)
            continue
        getattr(child, "grid")(**values)


def _flatten_child_geometry_entries(
    parent: object,
    states: Sequence[MountState],
) -> list[tuple[object, dict[str, Any]]]:
    entries: list[tuple[object, dict[str, Any]]] = []
    for state in states:
        resolved_values = _mount_resolved_values(state)
        if "in" not in resolved_values and "in_" not in resolved_values:
            resolved_values["in_"] = parent
        for ref in state.objects:
            entries.append((ref.value, dict(resolved_values)))
    return entries


def _pack_geometry_matches(
    parent: object,
    child: object,
    *,
    before: object | None,
    values: Mapping[str, Any],
) -> bool:
    manager_query = getattr(parent, "pack_slaves", None)
    current_children = tuple(manager_query()) if callable(manager_query) else ()
    try:
        index = current_children.index(child)
    except ValueError:
        return False
    current_before = current_children[index + 1] if index + 1 < len(current_children) else None
    if current_before is not before:
        return False
    pack_info = getattr(child, "pack_info", None)
    if not callable(pack_info):
        return False
    current_values = pack_info()
    for key, desired in values.items():
        if key in {"in", "in_"}:
            continue
        actual = current_values.get(key)
        if str(actual) != str(desired):
            return False
    return True


def _child_geometry_forget_method_name(method_name: str) -> str | None:
    if method_name == "pack":
        return "pack_forget"
    if method_name == "grid":
        return "grid_forget"
    if method_name == "place":
        return "place_forget"
    return None


def _ordered_fallback_method_names(mount_point: MountPointSpec) -> tuple[str | None, str | None]:
    if mount_point.place_method_name is not None or mount_point.detach_method_name is not None:
        return mount_point.place_method_name, mount_point.detach_method_name
    if mount_point.sync_method_name is None or not mount_point.sync_method_name.startswith("sync_"):
        return None, None
    plural = mount_point.sync_method_name.removeprefix("sync_")
    singular = _singularize(plural)
    return f"place_{singular}", f"detach_{singular}"


def _single_mount_detach_method_name(mount_point: MountPointSpec) -> str | None:
    apply_name = mount_point.apply_method_name
    if apply_name == "addWidget":
        return "removeWidget"
    if apply_name == "addLayout":
        return "removeItem"
    return None


def _singularize(name: str) -> str:
    if name.endswith("ies"):
        return f"{name[:-3]}y"
    if name.endswith("ren"):
        return "child"
    if name.endswith("s"):
        return name[:-1]
    return name


def _ordered_place_call_shape(
    parent_type: type[object],
    method_name: str,
) -> Literal["index_first", "value_first", "anchor_before"]:
    method = getattr(parent_type, method_name)
    try:
        parameters = tuple(signature(method).parameters.values())
    except (TypeError, ValueError):
        if method_name in {"insertAction", "insertMenu"}:
            return "anchor_before"
        return "index_first"
    non_self = [parameter for parameter in parameters if parameter.name != "self"]
    if not non_self:
        return "index_first"
    first_name = non_self[0].name
    if first_name in {"index", "position", "pos"}:
        return "index_first"
    if first_name in {"before", "before_action", "before_action_ref", "anchor"}:
        return "anchor_before"
    return "value_first"


def _ordered_append_method_name(place_method_name: str) -> str | None:
    if place_method_name.startswith("insert") and len(place_method_name) > len("insert"):
        return f"add{place_method_name[len('insert'):]}"
    return None


def _is_small_replay_delta(
    old_state: ImmutableOrderedMountState[Any] | None,
    new_state: ImmutableOrderedMountState[Any],
) -> bool:
    op_count = len(new_state.ops)
    if op_count == 0 and old_state is not None and old_state.objects != new_state.objects:
        return False
    return op_count <= 8


def _replay_mount_ops(
    parent: object,
    old_state: ImmutableOrderedMountState[Any] | None,
    state: ImmutableOrderedMountState[Any],
    resolved: ResolvedMountOps,
) -> None:
    if (resolved.place is None and resolved.place_before is None) or resolved.detach is None:
        raise ValueError("replay selected without placement/detach ops")
    current = list(old_state.objects if old_state is not None else ())
    for op in state.ops:
        if op.kind == "clear":
            for ref in tuple(current):
                resolved.detach(parent, ref.value)
            current.clear()
            continue
        if op.kind == "detach":
            if op.ref is not None:
                current = [existing for existing in current if existing.node_id != op.ref.node_id]
                resolved.detach(parent, op.ref.value)
            continue
        if op.kind == "place":
            if op.ref is not None and op.index is not None:
                current = [existing for existing in current if existing.node_id != op.ref.node_id]
                index = max(0, min(op.index, len(current)))
                if resolved.place_before is not None:
                    anchor = current[index].value if index < len(current) else None
                    resolved.place_before(parent, op.ref.value, anchor)
                elif resolved.place is not None:
                    resolved.place(parent, op.ref.value, index)
                current.insert(index, op.ref)


def _full_rebuild_ordered_mount(
    parent: object,
    old_state: MountState | None,
    new_state: MountState,
    resolved: ResolvedMountOps,
) -> None:
    if resolved.sync is not None:
        resolved.sync(parent, (new_state,))
        return
    if (
        resolved.place is None
        and resolved.place_before is None
        and resolved.append is None
    ) or resolved.detach is None:
        raise ValueError("ordered mount has no sync or replay ops")

    if old_state is not None:
        for ref in old_state.objects:
            resolved.detach(parent, ref.value)
    if resolved.place_before is not None:
        for ref in new_state.objects:
            resolved.place_before(parent, ref.value, None)
        return
    if resolved.append is not None and resolved.place is None:
        for ref in new_state.objects:
            resolved.append(parent, ref.value)
        return
    if resolved.place is None:
        raise ValueError("ordered mount has no index placement op")
    for index, ref in enumerate(new_state.objects):
        resolved.place(parent, ref.value, index)


__all__ = [
    "ImmutableOrderedMountState",
    "MountedRef",
    "MountApplierPlan",
    "MountOp",
    "OrderedMountStateBuilder",
    "ResolvedMountOps",
    "apply_mount_state",
    "choose_mount_applier",
    "resolve_mount_ops",
]
