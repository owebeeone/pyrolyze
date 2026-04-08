from __future__ import annotations

import pytest

from pyrolyze.lifecycle import (
    BindingBase,
    TransactionManager,
    binding,
    const,
    derived,
    lifecycle_field,
    local_store,
    managed,
    managed_context,
    owned,
    static,
    transient,
)


class AlwaysEqual:
    def __init__(self, label: str) -> None:
        self.label = label

    def __eq__(self, other: object) -> bool:
        del other
        return True


class GeoPoint:
    pass


class Point(GeoPoint):
    pass


class SpyBinding(BindingBase):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.label = label
        self.closed_states: list[bool] = []

    def _close(self) -> None:
        self.closed_states.append(self.is_accepted)


@managed_context
class MatrixContext:
    value: int = lifecycle_field(default=0, compare="value")
    ref: object | None = lifecycle_field(default=None, compare="identity")
    tracked: int = lifecycle_field(default=1, compare="value", state_factory=dict)

    def total(self) -> int:
        return self.value + self.tracked

    @property
    def doubled(self) -> int:
        return self.value * 2

    @staticmethod
    def static_total(left: int, right: int) -> int:
        return left + right

    @classmethod
    def class_name(cls) -> str:
        return cls.__name__


@managed_context
class ConstContext:
    slot_id: int = const(default=7)


@managed_context
class StaticContext:
    declared: tuple[str, ...] = static()


@managed_context
class ManagedAliasContext:
    value: int = managed(default=1)


@managed_context
class BindingContext:
    handle: SpyBinding | None = binding(default=None)
    handles: dict[str, SpyBinding] = binding(default_factory=dict)


@managed_context
class OwnedContext:
    child: SpyBinding | None = owned(default=None)
    children: dict[str, SpyBinding] = owned(default_factory=dict)


@managed_context
class TransientContext:
    seen_in_pass: bool = transient(default=False)


@managed_context
class LocalStoreContext:
    cache: dict[str, int] = local_store(default_factory=dict)


@managed_context
class DerivedCacheContext:
    value: int = managed(default=1)
    cache: dict[str, int] = derived(default_factory=dict)

    def refresh_cache(self) -> None:
        self.cache = {"value": self.value}


@managed_context
class TrackedContext:
    value: int = lifecycle_field(default=0, compare="value")

    def after_commit(self, previous: object, current: object) -> None:
        self.events.append(("commit", previous.value, current.value))

    def after_rollback(self, current: object) -> None:
        self.events.append(("rollback", current.value))


@managed_context
class BaseManaged:
    base_value: int = lifecycle_field(default=10)

    def base_total(self) -> int:
        return self.base_value


@managed_context
class DerivedManaged(BaseManaged):
    child_value: int = lifecycle_field(default=5)

    def child_total(self) -> int:
        return super().base_total() + self.child_value


@managed_context
class BasePoints:
    points: list[GeoPoint | None] | None = lifecycle_field(default=None)


@managed_context
class DerivedPoints(BasePoints):
    points: list[Point | None] | None = lifecycle_field(default_factory=list)


with pytest.raises(TypeError, match="incompatible lifecycle field override"):

    @managed_context
    class CompareBase:
        points: list[GeoPoint | None] | None = lifecycle_field(default=None, compare="value")

    @managed_context
    class CompareMismatch(CompareBase):
        points: list[Point | None] | None = lifecycle_field(default=None, compare="identity")


def test_field_specs_bind_handler_matrix_at_decoration_time() -> None:
    state_cls = MatrixContext.__state_cls__
    value_name = "value"
    ref_name = "ref"
    tracked_name = "tracked"

    assert state_cls.__name__ == "MatrixContext_State"
    assert state_cls.__field_names__ == ("value", "ref", "tracked")

    assert (
        state_cls.__class_ftable_set_default__[value_name]
        is state_cls.__class_ftable_set_default__[tracked_name]
    )
    assert (
        state_cls.__class_ftable_set_default__[value_name]
        is not state_cls.__class_ftable_set_default__[ref_name]
    )

    assert (
        state_cls.__class_ftable_get_default__[value_name]
        is state_cls.__class_ftable_get_default__[ref_name]
        is state_cls.__class_ftable_get_default__[tracked_name]
    )
    assert (
        state_cls.__class_ftable_get_current__[value_name]
        is state_cls.__class_ftable_get_current__[ref_name]
        is state_cls.__class_ftable_get_current__[tracked_name]
    )
    assert (
        state_cls.__class_ftable_get_working__[value_name]
        is state_cls.__class_ftable_get_working__[ref_name]
        is state_cls.__class_ftable_get_working__[tracked_name]
    )
    assert (
        state_cls.__class_ftable_commit_field__[value_name]
        is state_cls.__class_ftable_commit_field__[ref_name]
        is state_cls.__class_ftable_commit_field__[tracked_name]
    )
    assert (
        state_cls.__class_ftable_rollback_field__[value_name]
        is state_cls.__class_ftable_rollback_field__[ref_name]
        is state_cls.__class_ftable_rollback_field__[tracked_name]
    )


def test_managed_context_wraps_plain_class_onto_internal_base() -> None:
    context = MatrixContext()

    assert hasattr(MatrixContext, "__state_cls__")
    assert MatrixContext.__bases__[0].__name__ == "MatrixContext"
    assert hasattr(context, "state")
    assert context.value == 0


def test_const_fields_are_constructor_only_and_read_only_everywhere() -> None:
    context = ConstContext()

    assert context.slot_id == 7
    assert context.current.slot_id == 7
    assert context.working.slot_id == 7

    with pytest.raises(AttributeError, match="const"):
        context.slot_id = 8

    with pytest.raises(AttributeError, match="const"):
        context.working.slot_id = 8


def test_static_fields_allow_one_assignment_and_ignore_commit_rollback() -> None:
    manager = TransactionManager()
    context = StaticContext(transaction_manager=manager)

    with pytest.raises(AttributeError, match="initialized"):
        _ = context.declared

    context.declared = ("a", "b")
    assert context.declared == ("a", "b")
    assert context.current.declared == ("a", "b")
    assert context.working.declared == ("a", "b")

    manager.begin()
    manager.rollback()

    assert context.declared == ("a", "b")

    with pytest.raises(AttributeError, match="already initialized"):
        context.declared = ("x",)


def test_managed_alias_behaves_like_managed_field() -> None:
    manager = TransactionManager()
    context = ManagedAliasContext(transaction_manager=manager)

    assert context.value == 1
    manager.begin()
    context.value = 4
    assert context.value == 4
    assert context.current.value == 1


def test_binding_base_closes_once_and_uses_accepted_state() -> None:
    provisional = SpyBinding("provisional")

    assert provisional.ref_count == 1
    assert provisional.is_accepted is False
    assert provisional.is_closed is False

    provisional.dec_ref()

    assert provisional.is_closed is True
    assert provisional.closed_states == [False]

    committed = SpyBinding("committed")
    committed.inc_ref()
    committed.accepted()
    committed.dec_ref()

    assert committed.is_closed is False
    assert committed.ref_count == 1

    committed.dec_ref()

    assert committed.is_closed is True
    assert committed.closed_states == [True]


def test_binding_field_rolls_back_provisional_binding() -> None:
    manager = TransactionManager()
    context = BindingContext(transaction_manager=manager)
    binding_value = SpyBinding("new")

    manager.begin()
    context.handle = binding_value
    manager.rollback()

    assert context.current.handle is None
    assert binding_value.closed_states == [False]


def test_binding_field_commits_new_binding_and_releases_replaced_binding() -> None:
    manager = TransactionManager()
    context = BindingContext(transaction_manager=manager)
    first = SpyBinding("first")
    second = SpyBinding("second")

    manager.begin()
    context.handle = first
    manager.commit()

    assert context.current.handle is first
    assert first.is_accepted is True
    assert first.closed_states == []

    manager.begin()
    context.handle = second
    manager.commit()

    assert context.current.handle is second
    assert first.closed_states == [True]
    assert second.is_accepted is True


def test_binding_map_reuses_current_bindings_without_premature_close() -> None:
    manager = TransactionManager()
    context = BindingContext(transaction_manager=manager)
    shared = SpyBinding("shared")
    staged = SpyBinding("staged")
    added = SpyBinding("added")

    manager.begin()
    context.handles = {"shared": shared}
    manager.commit()

    assert shared.ref_count == 1
    assert shared.is_accepted is True

    manager.begin()
    context.handles = {"shared": shared, "staged": staged}
    assert shared.ref_count == 2
    assert staged.ref_count == 1

    context.handles = {"shared": shared, "staged": staged, "added": added}

    assert shared.closed_states == []
    assert staged.closed_states == []
    assert added.closed_states == []

    manager.rollback()

    assert context.current.handles == {"shared": shared}
    assert shared.ref_count == 1
    assert shared.closed_states == []
    assert staged.closed_states == [False]
    assert added.closed_states == [False]


def test_owned_field_closes_committed_child_on_owner_close() -> None:
    manager = TransactionManager()
    context = OwnedContext(transaction_manager=manager)
    child = SpyBinding("child")

    manager.begin()
    context.child = child
    manager.commit()

    assert child.is_accepted is True
    context.close()

    assert child.closed_states == [True]


def test_owned_map_closes_all_committed_children_on_owner_close() -> None:
    manager = TransactionManager()
    context = OwnedContext(transaction_manager=manager)
    left = SpyBinding("left")
    right = SpyBinding("right")

    manager.begin()
    context.children = {"left": left, "right": right}
    manager.commit()

    context.close()

    assert left.closed_states == [True]
    assert right.closed_states == [True]


def test_transient_field_is_visible_during_transaction_and_cleared_on_commit() -> None:
    manager = TransactionManager()
    context = TransientContext(transaction_manager=manager)

    assert context.seen_in_pass is False
    assert context.current.seen_in_pass is False

    manager.begin()
    context.seen_in_pass = True

    assert context.seen_in_pass is True
    assert context.current.seen_in_pass is False
    assert context.working.seen_in_pass is True

    manager.commit()

    assert context.seen_in_pass is False
    assert context.current.seen_in_pass is False
    assert context.working.seen_in_pass is False


def test_transient_field_is_cleared_on_rollback() -> None:
    manager = TransactionManager()
    context = TransientContext(transaction_manager=manager)

    manager.begin()
    context.seen_in_pass = True
    manager.rollback()

    assert context.seen_in_pass is False
    assert context.current.seen_in_pass is False


def test_local_store_survives_commit_and_is_shared_across_views() -> None:
    manager = TransactionManager()
    context = LocalStoreContext(transaction_manager=manager)

    context.cache["count"] = 1
    assert context.current.cache is context.cache
    assert context.working.cache is context.cache

    manager.begin()
    manager.commit()

    assert context.cache == {"count": 1}
    assert context.current.cache == {"count": 1}
    assert context.working.cache == {"count": 1}


def test_local_store_survives_rollback_and_resets_on_close() -> None:
    manager = TransactionManager()
    context = LocalStoreContext(transaction_manager=manager)

    context.cache = {"count": 2}

    manager.begin()
    manager.rollback()

    assert context.cache == {"count": 2}

    context.close()

    assert context.cache == {}


def test_derived_cache_is_shared_and_invalidated_on_commit() -> None:
    manager = TransactionManager()
    context = DerivedCacheContext(transaction_manager=manager)

    context.refresh_cache()
    assert context.cache == {"value": 1}
    assert context.current.cache == {"value": 1}
    assert context.working.cache == {"value": 1}

    manager.begin()
    context.value = 3
    context.refresh_cache()
    assert context.cache == {"value": 3}

    manager.commit()

    assert context.cache == {}
    assert context.current.cache == {}


def test_derived_cache_is_invalidated_on_rollback_and_close() -> None:
    manager = TransactionManager()
    context = DerivedCacheContext(transaction_manager=manager)

    context.refresh_cache()
    manager.begin()
    context.value = 4
    context.refresh_cache()
    manager.rollback()

    assert context.cache == {}

    context.refresh_cache()
    assert context.cache == {"value": 1}

    context.close()

    assert context.cache == {}

def test_managed_context_inheritance_merges_fields_and_view_methods() -> None:
    manager = TransactionManager()
    context = DerivedManaged(transaction_manager=manager)

    assert DerivedManaged.__state_cls__.__field_names__ == ("base_value", "child_value")
    assert context.base_value == 10
    assert context.child_value == 5
    assert isinstance(context.current, DerivedManaged)
    assert context.current.base_total() == 10
    assert context.current.child_total() == 15

    manager.begin()
    context.child_value = 9

    assert context.working.base_total() == 10
    assert context.working.child_total() == 19


def test_managed_context_field_reappearance_merges_compatibly() -> None:
    context = DerivedPoints()
    spec = DerivedPoints.__state_cls__.__field_specs__["points"]

    assert spec.annotation == list[Point | None] | None
    assert context.points == []


def test_unmanaged_attributes_are_shared_across_stable_views() -> None:
    context = MatrixContext()

    context.events = ["created"]

    assert context.events == ["created"]
    assert context.current.events == ["created"]
    assert context.working.events == ["created"]

    context.current.events.append("current")
    assert context.working.events == ["created", "current"]


def test_view_methods_use_normal_python_resolution() -> None:
    manager = TransactionManager()
    context = MatrixContext(transaction_manager=manager)

    assert isinstance(context.current, MatrixContext)
    assert isinstance(context.working, MatrixContext)
    assert context.current.total() == 1
    assert context.current.doubled == 0
    assert context.current.static_total(2, 3) == 5
    assert context.current.class_name() == "MatrixContext_CurrentView"

    manager.begin()
    context.value = 4

    assert context.working.total() == 5
    assert context.working.doubled == 8
    assert context.working.static_total(3, 4) == 7
    assert context.working.class_name() == "MatrixContext_WorkingView"


def test_default_record_reads_current_until_write_then_reads_working_overlay() -> None:
    manager = TransactionManager()
    context = MatrixContext(transaction_manager=manager)

    assert type(context.state) is MatrixContext.__state_cls__
    assert context.value == 0
    assert context.current.value == 0
    assert context._working_record is None

    manager.begin()

    assert context.value == 0
    assert context.working.value == 0
    context.value = 3

    assert context.value == 3
    assert context.current.value == 0
    assert context.working.value == 3
    assert context._working_record is not None

    manager.rollback()

    assert context.value == 0
    assert context.current.value == 0
    assert context._working_record is None


def test_working_view_reads_current_baseline_until_staged_override_exists() -> None:
    manager = TransactionManager()
    context = MatrixContext(transaction_manager=manager)

    manager.begin()

    assert context._working_record is None
    assert context.working.value == 0

    context.value = 5

    assert context._working_record is not None

    assert context.value == 5
    assert context.current.value == 0
    assert context.working.value == 5


def test_value_and_identity_fields_use_different_setter_semantics() -> None:
    context = MatrixContext()
    assert context._working_record is None

    with pytest.raises(RuntimeError, match="active lifecycle transaction"):
        context.value = 0

    left = AlwaysEqual("left")
    right = AlwaysEqual("right")

    manager = TransactionManager()
    context = MatrixContext(transaction_manager=manager)
    manager.begin()
    context.ref = left
    manager.commit()

    assert context.ref is left
    assert context.current.ref is left

    manager.begin()
    context.ref = right

    assert context.ref is right
    assert context.current.ref is left


def test_managed_writes_require_explicit_transaction() -> None:
    context = MatrixContext()

    with pytest.raises(RuntimeError, match="active lifecycle transaction"):
        context.value = 3

    with pytest.raises(RuntimeError, match="active lifecycle transaction"):
        context.working.value = 3


def test_field_runtime_state_uses_copy_on_write_and_rollback_discards_working_state() -> None:
    manager = TransactionManager()
    context = MatrixContext(transaction_manager=manager)

    committed_state = context.__get_current_field_state__("tracked")
    committed_state["phase"] = "committed"

    manager.begin()
    working_state = context.__ensure_working_field_state__("tracked")
    working_state["phase"] = "working"

    assert working_state is not committed_state
    assert context.__get_field_state__("tracked") == {"phase": "working"}
    assert context.__get_current_field_state__("tracked") == {"phase": "committed"}

    manager.rollback()

    assert context.__get_current_field_state__("tracked") == {"phase": "committed"}
    assert context._working_record is None


def test_field_runtime_state_commits_back_into_current_record() -> None:
    manager = TransactionManager()
    context = MatrixContext(transaction_manager=manager)

    context.__get_current_field_state__("tracked")["phase"] = "committed"

    manager.begin()
    context.__ensure_working_field_state__("tracked")["phase"] = "next"
    manager.commit()

    assert context.__get_current_field_state__("tracked") == {"phase": "next"}
    assert context._working_record is None


def test_transaction_manager_commits_only_dirty_contexts() -> None:
    manager = TransactionManager()
    left = TrackedContext(transaction_manager=manager)
    right = TrackedContext(transaction_manager=manager)
    left.events = []
    right.events = []

    manager.begin()
    left.value = 10
    manager.commit()

    assert left.current.value == 10
    assert right.current.value == 0
    assert left.events == [("commit", 0, 10)]
    assert right.events == []
    assert manager.active_transaction is None


def test_transaction_manager_rolls_back_only_dirty_contexts() -> None:
    manager = TransactionManager()
    left = TrackedContext(transaction_manager=manager)
    right = TrackedContext(transaction_manager=manager)
    left.events = []
    right.events = []

    manager.begin()
    left.value = 20
    manager.rollback()

    assert left.current.value == 0
    assert right.current.value == 0
    assert left.events == [("rollback", 0)]
    assert right.events == []
    assert manager.active_transaction is None


def test_transaction_manager_rejects_nested_transactions() -> None:
    manager = TransactionManager()

    transaction = manager.begin()
    assert transaction.tx_id == 1

    with pytest.raises(RuntimeError, match="nested"):
        manager.begin()

    manager.rollback()
