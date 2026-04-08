from __future__ import annotations

from dataclasses import dataclass

import pytest

from pyrolyze.lifecycle import (
    LifecycleContext,
    TransactionManager,
    const,
    managed,
    managed_binding,
    managed_context,
)


@dataclass(eq=False, slots=True)
class TrackingBinding:
    name: str
    events: list[tuple[str, str, bool | None]]

    def accepted(self) -> None:
        self.events.append(("accepted", self.name, None))

    def close(self, *, was_committed: bool) -> None:
        self.events.append(("closed", self.name, was_committed))


@managed_context
class ManagedSlotContext(LifecycleContext):
    invoke_dirty: bool = managed(default=True)
    seen_in_pass: bool = managed(default=False)


@managed_context
class ManagedRerunnableSlotContext(ManagedSlotContext):
    slot_id: str = managed(default="")


@managed_context
class ManagedSlotCallContext(ManagedRerunnableSlotContext):
    function_identity: object | None = managed(default=None)
    schema: tuple[int, tuple[str, ...]] = managed(default=(0, ()))
    last_args: tuple[object, ...] = managed(default_factory=tuple)
    last_kwargs: tuple[tuple[str, object], ...] = managed(default_factory=tuple)
    binding: TrackingBinding | None = managed_binding(default=None)
    site_bindings: dict[str, TrackingBinding] = managed_binding(default_factory=dict)


@managed_context
class ManagedContainerContext(ManagedRerunnableSlotContext):
    native_root: bool = managed(default=False)
    site_bindings: dict[str, TrackingBinding] = managed_binding(default_factory=dict)


@managed_context
class ManagedChildContext(LifecycleContext):
    label: str = managed(default="child")


@managed_context
class ManagedComponentCallContext(ManagedRerunnableSlotContext):
    component_identity: object | None = managed(default=None)
    schema: tuple[int, tuple[str, ...]] = managed(default=(0, ()))
    child_context: ManagedChildContext | None = managed_binding(default=None)
    owned_handlers: dict[str, TrackingBinding] = managed_binding(default_factory=dict)


@managed_context
class ManagedOverrideContext(ManagedRerunnableSlotContext):
    declared_keys: tuple[str, ...] = managed(default_factory=tuple)
    values: tuple[object, ...] = managed(default_factory=tuple)

    def before_commit(self, current_state: object, working_state: object) -> None:
        current = current_state
        working = working_state
        if len(working.declared_keys) != len(working.values):
            raise ValueError("override key/value arity must match")
        if current.declared_keys and working.declared_keys != current.declared_keys:
            raise ValueError("override keys are fixed after first commit")


@managed_context
class ManagedTrackedContext(LifecycleContext):
    value: int = managed(default=0)

    def after_commit(self, previous_state: object, current_state: object) -> None:
        self.events.append(("commit", previous_state.value, current_state.value))

    def after_rollback(self, current_state: object) -> None:
        self.events.append(("rollback", current_state.value))


@managed_context
class ManagedConstBase(LifecycleContext):
    slot_id: str = const()
    label: str = managed(default="base")


@managed_context
class ManagedConstChild(ManagedConstBase):
    module_id: str = const(default="default-module")
    count: int = managed(default=0)


def test_slot_call_context_binding_and_binding_map_use_commit_and_rollback_lifecycle() -> None:
    events: list[tuple[str, str, bool | None]] = []
    context = ManagedSlotCallContext(slot_id="slot-call")

    binding_one = TrackingBinding("binding-1", events)
    metadata_one = TrackingBinding("metadata-1", events)

    context.function_identity = "fn"
    context.binding = binding_one
    context.site_bindings["site"] = metadata_one
    context.commit()

    assert context.current_state.binding is binding_one
    assert context.current_state.site_bindings["site"] is metadata_one
    assert events == [
        ("accepted", "binding-1", None),
        ("accepted", "metadata-1", None),
    ]

    binding_two = TrackingBinding("binding-2", events)
    metadata_two = TrackingBinding("metadata-2", events)

    context.binding = binding_two
    context.site_bindings["site"] = metadata_two
    context.rollback()

    assert context.current_state.binding is binding_one
    assert context.current_state.site_bindings["site"] is metadata_one
    assert events == [
        ("accepted", "binding-1", None),
        ("accepted", "metadata-1", None),
        ("closed", "binding-2", False),
        ("closed", "metadata-2", False),
    ]

    context.binding = None
    del context.site_bindings["site"]
    context.commit()

    assert context.current_state.binding is None
    assert dict(context.current_state.site_bindings) == {}
    assert events == [
        ("accepted", "binding-1", None),
        ("accepted", "metadata-1", None),
        ("closed", "binding-2", False),
        ("closed", "metadata-2", False),
        ("closed", "binding-1", True),
        ("closed", "metadata-1", True),
    ]


def test_container_context_inherits_state_shape_and_no_op_commit_is_quiet() -> None:
    events: list[tuple[str, str, bool | None]] = []
    context = ManagedContainerContext(slot_id="container")
    metadata = TrackingBinding("container-meta", events)

    context.invoke_dirty = False
    context.native_root = True
    context.site_bindings["container"] = metadata
    context.commit()

    assert context.current_state.slot_id == "container"
    assert context.current_state.invoke_dirty is False
    assert context.current_state.native_root is True
    assert events == [("accepted", "container-meta", None)]

    context.commit()

    assert context.current_state.native_root is True
    assert events == [("accepted", "container-meta", None)]


def test_component_context_can_manage_nested_child_contexts_and_handler_maps() -> None:
    events: list[tuple[str, str, bool | None]] = []
    context = ManagedComponentCallContext(slot_id="component")

    first_child = ManagedChildContext(label="first")
    first_handler = TrackingBinding("first-handler", events)

    context.child_context = first_child
    context.owned_handlers["click"] = first_handler
    context.commit()

    assert context.current_state.child_context is first_child
    assert events == [("accepted", "first-handler", None)]
    assert first_child.is_closed is False

    second_child = ManagedChildContext(label="second")
    second_handler = TrackingBinding("second-handler", events)

    context.child_context = second_child
    context.owned_handlers["click"] = second_handler
    context.commit()

    assert first_child.is_closed is True
    assert second_child.is_closed is False
    assert events == [
        ("accepted", "first-handler", None),
        ("accepted", "second-handler", None),
        ("closed", "first-handler", True),
    ]

    context.close()

    assert second_child.is_closed is True
    assert events == [
        ("accepted", "first-handler", None),
        ("accepted", "second-handler", None),
        ("closed", "first-handler", True),
        ("closed", "second-handler", True),
    ]


def test_override_context_uses_custom_commit_validation_for_fixed_structure() -> None:
    context = ManagedOverrideContext(slot_id="override")

    context.declared_keys = ("theme", "locale")
    context.values = ("dark", "en")
    context.commit()

    context.values = ("light", "fr")
    context.commit()
    assert context.current_state.values == ("light", "fr")

    context.declared_keys = ("theme",)
    context.values = ("light",)

    with pytest.raises(ValueError, match="fixed"):
        context.commit()

    assert context.working_state is not None
    context.rollback()
    assert context.current_state.declared_keys == ("theme", "locale")
    assert context.current_state.values == ("light", "fr")


def test_transaction_manager_commits_only_dirty_contexts() -> None:
    manager = TransactionManager()
    left = ManagedTrackedContext(transaction_manager=manager)
    right = ManagedTrackedContext(transaction_manager=manager)
    left.events = []
    right.events = []

    manager.begin()
    left.value = 10
    manager.commit()

    assert left.current_state.value == 10
    assert right.current_state.value == 0
    assert left.events == [("commit", 0, 10)]
    assert right.events == []
    assert manager.active_transaction is None


def test_transaction_manager_rolls_back_only_dirty_contexts() -> None:
    manager = TransactionManager()
    left = ManagedTrackedContext(transaction_manager=manager)
    right = ManagedTrackedContext(transaction_manager=manager)
    left.events = []
    right.events = []

    manager.begin()
    left.value = 20
    manager.rollback()

    assert left.current_state.value == 0
    assert right.current_state.value == 0
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


def test_const_fields_are_set_at_construction_and_not_part_of_managed_state() -> None:
    context = ManagedConstChild(slot_id="slot-a", count=3)

    assert context.slot_id == "slot-a"
    assert context.module_id == "default-module"
    assert context.current_state.count == 3
    assert not hasattr(context.current_state, "slot_id")
    assert not hasattr(context.current_state, "module_id")


def test_const_fields_cannot_be_mutated_after_construction() -> None:
    context = ManagedConstChild(slot_id="slot-a")

    with pytest.raises(AttributeError, match="slot_id is const"):
        context.slot_id = "slot-b"

    with pytest.raises(AttributeError, match="module_id is const"):
        context.module_id = "other-module"


def test_const_fields_are_inherited() -> None:
    context = ManagedConstChild(slot_id="slot-a", module_id="module-a", count=5)

    assert context.slot_id == "slot-a"
    assert context.module_id == "module-a"
    assert context.current_state.count == 5
