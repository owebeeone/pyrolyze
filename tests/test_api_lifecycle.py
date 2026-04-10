from __future__ import annotations

import pytest

from pyrolyze.lifecycle import (
    BindingBase,
    DEFAULT_TRANSACTION,
    GroupTransactionManager,
    LifecycleContext,
    LifecycleTransaction,
    LifecycleValidatorReturnedFalse,
    TransactionManager,
    binding,
    commit_order_key,
    commit_validator,
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


def build_triplet(self: LifecycleContext, current: LifecycleContext, working: LifecycleContext) -> tuple[int, int, int]:
    return (self.base, current.base, working.base)


def build_pass_items(
    self: LifecycleContext,
    current: LifecycleContext,
    working: LifecycleContext,
) -> list[int]:
    return [self.base, current.base, working.base]


def build_cycle_left(self: LifecycleContext) -> int:
    return self.right + 1


def build_cycle_right(self: LifecycleContext) -> int:
    return self.left + 1


def build_working_cycle(self: LifecycleContext) -> list[object] | None:
    return self.items


def reject_commit(_ctx: LifecycleContext) -> bool:
    return False


with pytest.raises(TypeError, match="unsupported parameter"):

    def invalid_default_factory(nope: object) -> int:
        del nope
        return 1

    @managed_context
    class InvalidFactoryParamContext:
        value: int = managed(default_factory=invalid_default_factory)


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
class TransientOptionalContext:
    tag: object | None = transient(default=None)


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
class ValueControlContext:
    value: int = managed(default=0)
    first_pass: bool = managed(default=False, initial_working=True)
    items: tuple[int, ...] = managed(default_factory=tuple, freeze=tuple, thaw=list)


GROUP_ALPHA = "group_alpha"
GROUP_BETA = "group_beta"


@managed_context
class GroupedFieldContext:
    value: int = managed(default=0, tx_group=GROUP_ALPHA)
    scratch: bool = transient(default=False, tx_group=GROUP_BETA)
    handle: SpyBinding | None = binding(default=None, tx_group=GROUP_ALPHA)
    child: SpyBinding | None = owned(default=None, tx_group=GROUP_BETA)
    validator: object | None = commit_validator(default=lambda _ctx: True, tx_group=GROUP_ALPHA)
    order_key: tuple[int, ...] = commit_order_key(default=(1,), tx_group=GROUP_BETA)


@managed_context
class GroupedBaseContext:
    value: int = managed(default=0, tx_group=GROUP_ALPHA)


@managed_context
class GroupedDerivedContext(GroupedBaseContext):
    value: int = managed(default=1, tx_group=GROUP_ALPHA)


with pytest.raises(TypeError, match="incompatible lifecycle field override"):

    @managed_context
    class GroupedMismatchContext(GroupedBaseContext):
        value: int = managed(default=1, tx_group=GROUP_BETA)


@managed_context
class DefaultGroupedMetadataContext:
    value: int = managed(default=0)
    validator: object | None = commit_validator(default=lambda _ctx: True)
    order_key: tuple[int, ...] = commit_order_key(default=(2,))


@managed_context
class GroupedScratchFactoryContext:
    value: int = managed(default=0, tx_group=GROUP_ALPHA)
    scratch: list[int] | None = transient(
        default=None,
        working_default_factory=list,
        tx_group=GROUP_BETA,
    )


@managed_context
class GroupedManagedContext:
    left: int = managed(default=0, tx_group=GROUP_ALPHA)
    right: int = managed(default=0, tx_group=GROUP_BETA)


@managed_context
class GroupedIndependentCommitContext:
    left: int = managed(default=0, tx_group=GROUP_ALPHA)
    right: int = managed(default=0, tx_group=GROUP_BETA)
    left_ok: object | None = commit_validator(default=reject_commit, tx_group=GROUP_ALPHA)


@managed_context
class ContextAwareDefaultFactoryContext:
    triplet: tuple[int, int, int] = managed(default_factory=build_triplet)
    base: int = managed(default=7)


@managed_context
class ContextAwareWorkingFactoryContext:
    base: int = managed(default=1)
    items: list[int] | None = transient(default=None, working_default_factory=build_pass_items)


@managed_context
class DefaultFactoryCycleContext:
    left: int = managed(default_factory=build_cycle_left)
    right: int = managed(default_factory=build_cycle_right)


@managed_context
class WorkingFactoryCycleContext:
    items: list[object] | None = transient(default=None, working_default_factory=build_working_cycle)


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


def test_tx_group_defaults_to_default_transaction() -> None:
    specs = MatrixContext.__state_cls__.__field_specs__

    assert specs["value"].tx_group == DEFAULT_TRANSACTION
    assert specs["ref"].tx_group == DEFAULT_TRANSACTION
    assert specs["tracked"].tx_group == DEFAULT_TRANSACTION


def test_validator_and_order_key_default_to_default_transaction() -> None:
    specs = DefaultGroupedMetadataContext.__state_cls__.__field_specs__

    assert specs["validator"].tx_group == DEFAULT_TRANSACTION
    assert specs["order_key"].tx_group == DEFAULT_TRANSACTION


def test_tx_group_metadata_is_recorded_for_grouped_fields() -> None:
    specs = GroupedFieldContext.__state_cls__.__field_specs__

    assert specs["value"].tx_group == GROUP_ALPHA
    assert specs["scratch"].tx_group == GROUP_BETA
    assert specs["handle"].tx_group == GROUP_ALPHA
    assert specs["child"].tx_group == GROUP_BETA
    assert specs["validator"].tx_group == GROUP_ALPHA
    assert specs["order_key"].tx_group == GROUP_BETA


def test_same_name_override_may_keep_same_tx_group() -> None:
    spec = GroupedDerivedContext.__state_cls__.__field_specs__["value"]

    assert spec.tx_group == GROUP_ALPHA
    assert GroupedDerivedContext().value == 1


def test_managed_context_wraps_plain_class_onto_internal_base() -> None:
    context = MatrixContext()

    assert hasattr(MatrixContext, "__state_cls__")
    assert MatrixContext.__bases__[0].__name__ == "MatrixContext"
    assert hasattr(context, "state")
    assert context.value == 0


def test_view_navigation_is_closed_over_current_and_working_views() -> None:
    context = MatrixContext()

    assert context.current.current is context.current
    assert context.current.working is context.working
    assert context.working.current is context.current
    assert context.working.working is context.working


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


def test_context_aware_default_factory_can_resolve_other_fields_and_views() -> None:
    context = ContextAwareDefaultFactoryContext()
    state_cls = ContextAwareDefaultFactoryContext.__state_cls__

    assert context.base == 7
    assert context.triplet == (7, 7, 7)
    assert "triplet" in state_cls.__class_ftable_default_factory_runner__


def test_context_aware_default_factory_cycle_is_detected() -> None:
    with pytest.raises(RuntimeError, match="lifecycle factory cycle detected"):
        DefaultFactoryCycleContext()


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


def test_transient_none_default_requires_active_transaction_to_assign() -> None:
    manager = TransactionManager()
    context = TransientOptionalContext(transaction_manager=manager)

    assert context.tag is None
    assert context.current.tag is None

    with pytest.raises(RuntimeError, match="active lifecycle transaction"):
        context.tag = object()


def test_transient_none_default_reset_after_commit_and_rollback() -> None:
    manager = TransactionManager()
    sentinel = object()

    context = TransientOptionalContext(transaction_manager=manager)
    assert context.tag is None

    manager.begin()
    context.tag = sentinel
    assert context.tag is sentinel
    assert context.current.tag is None

    manager.commit()
    assert context.tag is None
    assert context.current.tag is None
    assert context.working.tag is None

    manager.begin()
    context.tag = sentinel
    manager.rollback()
    assert context.tag is None
    assert context.current.tag is None


def test_transient_working_default_factory_creates_tx_local_scratch_from_views() -> None:
    manager = TransactionManager()
    context = ContextAwareWorkingFactoryContext(transaction_manager=manager)

    assert context.items is None
    assert context.current.items is None

    manager.begin()
    context.base = 9

    assert context.items == [9, 1, 9]
    assert context.current.items is None
    assert context.working.items == [9, 1, 9]
    assert context._working_record is not None

    manager.commit()

    assert context.items is None
    assert context.current.items is None
    assert context.working.items is None


def test_transient_working_default_factory_cycle_is_detected() -> None:
    manager = TransactionManager()
    context = WorkingFactoryCycleContext(transaction_manager=manager)

    manager.begin()
    with pytest.raises(RuntimeError, match="lifecycle factory cycle detected"):
        _ = context.items
    manager.rollback()


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


def test_managed_initial_working_applies_before_first_successful_commit() -> None:
    manager = TransactionManager()
    context = ValueControlContext(transaction_manager=manager)

    manager.begin()
    assert context.first_pass is True
    assert context.current.first_pass is False
    manager.rollback()

    manager.begin()
    assert context.first_pass is True
    context.value = 1
    manager.commit()

    manager.begin()
    assert context.first_pass is False
    manager.rollback()


def test_managed_freeze_and_thaw_support_mutable_working_value() -> None:
    manager = TransactionManager()
    context = ValueControlContext(transaction_manager=manager)

    manager.begin()
    assert context.items == []
    context.items.append(1)
    context.items.append(2)
    assert context.items == [1, 2]
    assert context.current.items == ()

    manager.commit()

    assert context.items == (1, 2)
    assert context.current.items == (1, 2)

    manager.begin()
    assert context.items == [1, 2]
    context.items.append(3)
    manager.rollback()

    assert context.items == (1, 2)


def test_stale_working_record_without_active_transaction_is_rejected() -> None:
    manager = TransactionManager()
    context = ValueControlContext(transaction_manager=manager)

    manager.begin()
    context.value = 1
    manager.active_transaction = None

    with pytest.raises(RuntimeError, match="stale lifecycle working record"):
        context.value = 2


def test_cross_transaction_mutation_is_rejected() -> None:
    manager = TransactionManager()
    context = ValueControlContext(transaction_manager=manager)

    manager.begin()
    context.value = 1
    manager.active_transaction = LifecycleTransaction(tx_id=999)

    with pytest.raises(RuntimeError, match="different lifecycle transaction"):
        context.value = 2

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


def test_transaction_manager_begin_is_nestable_balanced_by_commit() -> None:
    manager = TransactionManager()
    outer = manager.begin()
    inner = manager.begin()
    assert outer is inner is manager.active_transaction
    assert manager.begin_count == 2

    assert manager.commit() is None
    assert manager.begin_count == 1
    assert manager.active_transaction is not None

    tx_id = manager.commit()
    assert tx_id == 1
    assert manager.active_transaction is None
    assert manager.begin_count == 0


def test_group_transaction_manager_preserves_previous_single_group_behavior() -> None:
    manager = GroupTransactionManager()
    outer = manager.begin()
    inner = manager.begin()

    assert outer is inner is manager.active_transaction
    assert manager.begin_count == 2

    assert manager.commit() is None
    assert manager.begin_count == 1
    assert manager.active_transaction is not None

    tx_id = manager.commit_only()
    assert tx_id == 1
    assert manager.active_transaction is None
    assert manager.begin_count == 0


def test_transaction_manager_context_manager_commits_on_clean_exit() -> None:
    manager = TransactionManager()
    context = ManagedAliasContext(transaction_manager=manager)

    with manager.begin():
        context.value = 4
        assert context.value == 4
        assert context.current.value == 1

    assert context.current.value == 4
    assert manager.active_transaction is None
    assert manager.begin_count == 0


def test_transaction_manager_context_manager_rolls_back_on_exception() -> None:
    manager = TransactionManager()
    context = ManagedAliasContext(transaction_manager=manager)

    with pytest.raises(RuntimeError, match="boom"):
        with manager.begin():
            context.value = 7
            raise RuntimeError("boom")

    assert context.current.value == 1
    assert manager.active_transaction is None
    assert manager.begin_count == 0


def test_transaction_manager_rejects_unknown_group() -> None:
    manager = TransactionManager(tx_groups={"known"})

    with pytest.raises(RuntimeError, match="unknown lifecycle transaction group"):
        manager.begin("unknown")


def test_transaction_manager_validate_then_commit_only_skips_second_validation() -> None:
    validations: list[str] = []

    def check(ctx: LifecycleContext) -> bool:
        validations.append(type(ctx).__name__)
        return True

    @managed_context
    class ValidatedContext:
        value: int = managed(default=0)
        on_commit_ok: object | None = commit_validator(default=check)

    manager = TransactionManager()
    ctx = ValidatedContext(transaction_manager=manager)
    manager.begin()
    ctx.value = 5

    manager.validate()
    assert validations == ["ValidatedContext"]

    manager.commit_only()
    assert validations == ["ValidatedContext"]
    assert ctx.current.value == 5


def test_grouped_field_write_requires_its_own_transaction_group() -> None:
    manager = TransactionManager(tx_groups={GROUP_ALPHA, GROUP_BETA})
    context = GroupedFieldContext(transaction_manager=manager)

    manager.begin(GROUP_ALPHA)
    context.value = 3

    assert context.value == 3
    assert context.current.value == 0

    with pytest.raises(RuntimeError, match="active lifecycle transaction"):
        context.scratch = True

    manager.rollback(GROUP_ALPHA)


def test_default_group_field_does_not_use_non_default_transaction_groups() -> None:
    manager = TransactionManager(tx_groups={GROUP_ALPHA})
    context = MatrixContext(transaction_manager=manager)

    manager.begin(GROUP_ALPHA)
    with pytest.raises(RuntimeError, match="active lifecycle transaction"):
        context.value = 9
    manager.rollback(GROUP_ALPHA)

    manager.begin()
    context.value = 9
    manager.commit()

    assert context.current.value == 9


def test_unified_working_view_reflects_all_active_group_working_state() -> None:
    manager = TransactionManager(tx_groups={GROUP_ALPHA, GROUP_BETA})
    context = GroupedFieldContext(transaction_manager=manager)

    manager.begin(GROUP_ALPHA)
    context.value = 5
    manager.begin(GROUP_BETA)
    context.scratch = True

    assert context.working.value == 5
    assert context.working.scratch is True
    assert context.current.value == 0
    assert context.current.scratch is False

    manager.commit(GROUP_ALPHA)

    assert context.current.value == 5
    assert context.value == 5
    assert context.scratch is True
    assert context.current.scratch is False

    manager.rollback(GROUP_BETA)

    assert context.current.value == 5
    assert context.current.scratch is False
    assert context.scratch is False


def test_publish_only_group_does_not_activate_pass_group_working_default() -> None:
    manager = TransactionManager(tx_groups={GROUP_ALPHA, GROUP_BETA})
    context = GroupedScratchFactoryContext(transaction_manager=manager)

    manager.begin(GROUP_ALPHA)
    context.value = 8
    assert context.scratch is None
    manager.rollback(GROUP_ALPHA)

    manager.begin(GROUP_BETA)
    assert context.scratch == []
    context.scratch.append(1)
    assert context.scratch == [1]
    manager.rollback(GROUP_BETA)

    assert context.current.scratch is None
    assert context.scratch is None


def test_group_begin_counts_are_tracked_independently() -> None:
    manager = TransactionManager(tx_groups={GROUP_ALPHA, GROUP_BETA})
    context = GroupedManagedContext(transaction_manager=manager)

    manager.begin(GROUP_ALPHA)
    manager.begin(GROUP_ALPHA)
    manager.begin(GROUP_BETA)
    context.left = 3
    context.right = 4

    assert manager.commit(GROUP_ALPHA) is None
    assert context.current.left == 0
    assert context.left == 3

    manager.commit(GROUP_BETA)
    assert context.current.right == 4

    manager.commit(GROUP_ALPHA)
    assert context.current.left == 3


def test_multi_group_context_manager_commits_each_group() -> None:
    manager = TransactionManager(tx_groups={GROUP_ALPHA, GROUP_BETA})
    context = GroupedManagedContext(transaction_manager=manager)

    with manager.begin(GROUP_ALPHA, GROUP_BETA):
        context.left = 10
        context.right = 11
        assert context.left == 10
        assert context.right == 11
        assert context.current.left == 0
        assert context.current.right == 0

    assert context.current.left == 10
    assert context.current.right == 11


def test_multi_group_commit_is_ordered_independent_not_coupled() -> None:
    manager = TransactionManager(tx_groups={GROUP_ALPHA, GROUP_BETA})
    context = GroupedIndependentCommitContext(transaction_manager=manager)

    manager.begin(GROUP_ALPHA)
    manager.begin(GROUP_BETA)
    context.left = 1
    context.right = 2

    with pytest.raises(ExceptionGroup):
        manager.commit(GROUP_BETA, GROUP_ALPHA)

    assert context.current.right == 2
    assert context.current.left == 0
    assert context.right == 2
    assert context.left == 0


def test_transaction_manager_commit_and_rollback_require_balanced_begin() -> None:
    manager = TransactionManager()
    with pytest.raises(RuntimeError, match="no active lifecycle transaction"):
        manager.commit()
    with pytest.raises(RuntimeError, match="no active lifecycle transaction"):
        manager.rollback()

    manager.begin()
    manager.rollback()
    with pytest.raises(RuntimeError, match="no active lifecycle transaction"):
        manager.rollback()


def test_commit_order_key_fields_control_manager_commit_order() -> None:
    manager = TransactionManager()
    commit_names: list[str] = []

    @managed_context
    class RankedContext:
        name: str = const(default="")
        rank: tuple[int, ...] = commit_order_key(default=(0,))
        value: int = managed(default=0)

        def after_commit(self, previous: object, current: object) -> None:
            del previous, current
            commit_names.append(self.name)

    low = RankedContext(transaction_manager=manager, name="low", rank=(1,))
    high = RankedContext(transaction_manager=manager, name="high", rank=(2,))
    manager.begin()
    low.value = 1
    high.value = 1
    manager.commit()

    assert commit_names == ["high", "low"]


def test_default_commit_order_key_is_empty_tuple() -> None:
    manager = TransactionManager()
    ctx = TrackedContext(transaction_manager=manager)
    assert ctx.commit_order_key() == ()


def test_commit_validator_runs_before_context_commits() -> None:
    manager = TransactionManager()
    validated: list[str] = []

    def check(ctx: LifecycleContext) -> bool:
        validated.append(type(ctx).__name__)
        return True

    @managed_context
    class ValidatedContext:
        value: int = managed(default=0)
        on_commit_ok: object | None = commit_validator(default=check)

    ctx = ValidatedContext(transaction_manager=manager)
    assert ctx.requires_validation() is True
    manager.begin()
    ctx.value = 3
    manager.commit()
    assert validated == ["ValidatedContext"]


def test_commit_validator_failure_aborts_transaction() -> None:
    manager = TransactionManager()
    validation_allowed = {"ok": False}

    def guard(_ctx: LifecycleContext) -> bool:
        return validation_allowed["ok"]

    @managed_context
    class BadContext:
        value: int = managed(default=0)
        must_pass: object | None = commit_validator(default=guard)

    ctx = BadContext(transaction_manager=manager)
    manager.begin()
    ctx.value = 7
    with pytest.raises(ExceptionGroup, match="lifecycle commit validation failed") as failure:
        manager.commit()
    assert len(failure.value.exceptions) == 1
    assert isinstance(failure.value.exceptions[0], LifecycleValidatorReturnedFalse)

    assert ctx.current.value == 0
    assert ctx._working_record is None
    assert manager.active_transaction is None
    assert manager.begin_count == 0

    # Manager must accept a brand-new transaction (would fail if begin_count/active leaked).
    validation_allowed["ok"] = True
    tx2 = manager.begin()
    assert tx2.tx_id == 2
    ctx.value = 5
    manager.commit()
    assert ctx.current.value == 5


def test_commit_validator_failure_on_outermost_nested_begin_rollbacks_and_resets_manager() -> None:
    manager = TransactionManager()

    def reject(_ctx: LifecycleContext) -> bool:
        return False

    @managed_context
    class BadContext:
        value: int = managed(default=0)
        must_pass: object | None = commit_validator(default=reject)

    ctx = BadContext(transaction_manager=manager)
    manager.begin()
    manager.begin()
    ctx.value = 3
    assert manager.commit() is None
    assert manager.begin_count == 1
    assert manager.active_transaction is not None

    with pytest.raises(ExceptionGroup, match="lifecycle commit validation failed") as failure:
        manager.commit()
    assert len(failure.value.exceptions) == 1
    assert isinstance(failure.value.exceptions[0], LifecycleValidatorReturnedFalse)

    assert ctx.current.value == 0
    assert ctx._working_record is None
    assert manager.active_transaction is None
    assert manager.begin_count == 0

    tx2 = manager.begin()
    assert tx2.tx_id == 2


def test_commit_validation_runs_all_validators_and_raises_exception_group() -> None:
    manager = TransactionManager()

    def boom_value(_ctx: LifecycleContext) -> bool:
        raise ValueError("first problem")

    def boom_type(_ctx: LifecycleContext) -> bool:
        raise TypeError("second problem")

    @managed_context
    class First:
        value: int = managed(default=0)
        chk: object | None = commit_validator(default=boom_value)

    @managed_context
    class Second:
        value: int = managed(default=0)
        chk: object | None = commit_validator(default=boom_type)

    first = First(transaction_manager=manager)
    second = Second(transaction_manager=manager)
    manager.begin()
    first.value = 1
    second.value = 1

    with pytest.raises(ExceptionGroup, match="lifecycle commit validation failed") as failure:
        manager.commit()

    excs = failure.value.exceptions
    assert len(excs) == 2
    assert isinstance(excs[0], ValueError) and str(excs[0]) == "first problem"
    assert isinstance(excs[1], TypeError) and str(excs[1]) == "second problem"
    assert first.current.value == 0
    assert second.current.value == 0


def test_commit_validation_collects_false_and_raised_errors_together() -> None:
    manager = TransactionManager()

    def returns_false(_ctx: LifecycleContext) -> bool:
        return False

    def raises_exc(_ctx: LifecycleContext) -> bool:
        raise RuntimeError("validator blew up")

    @managed_context
    class Quiet:
        value: int = managed(default=0)
        chk: object | None = commit_validator(default=returns_false)

    @managed_context
    class Loud:
        value: int = managed(default=0)
        chk: object | None = commit_validator(default=raises_exc)

    quiet = Quiet(transaction_manager=manager)
    loud = Loud(transaction_manager=manager)
    manager.begin()
    quiet.value = 1
    loud.value = 1

    with pytest.raises(ExceptionGroup, match="lifecycle commit validation failed") as failure:
        manager.commit()

    excs = failure.value.exceptions
    assert len(excs) == 2
    assert isinstance(excs[0], LifecycleValidatorReturnedFalse)
    assert excs[0].context is quiet
    assert isinstance(excs[1], RuntimeError) and str(excs[1]) == "validator blew up"
