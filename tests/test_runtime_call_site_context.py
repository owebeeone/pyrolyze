from __future__ import annotations

from dataclasses import dataclass

from pyrolyze.runtime.call_site_context import (
    CallSiteArgs,
    CallSiteBindingBase,
    CallSiteContext,
    CallSiteContextManager,
    CallSiteInvokeState,
)
from pyrolyze.runtime.context import ModuleRegistry, SlotId


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.test_runtime_call_site_context")
_SLOT_1 = SlotId(_MODULE_ID, 1, line_no=10)
_SLOT_2 = SlotId(_MODULE_ID, 2, line_no=11)


@dataclass(slots=True, eq=False)
class _FakeBinding(CallSiteBindingBase):
    cleanup_count: int = 0

    def _close(self) -> None:
        self.cleanup_count += 1


def test_call_site_args_capture_normalizes_kwargs() -> None:
    args = CallSiteArgs.capture(1, 2, z=3, a=4)

    assert args.args == (1, 2)
    assert args.kwargs == (("a", 4), ("z", 3))


def test_call_site_args_call_invokes_target() -> None:
    args = CallSiteArgs.capture(1, 2, z=3)

    result = args.call(lambda x, y, *, z: x + y + z)

    assert result == 6


def test_manager_returns_none_before_stage_and_current_after_commit() -> None:
    manager = CallSiteContextManager()
    binding = _FakeBinding()

    assert manager.get_current(_SLOT_1) is None

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    context = CallSiteContext(
        binding=binding,
        function_identity="fn",
        last_args=CallSiteArgs.capture(1, flag=True),
    )
    manager.stage(_SLOT_1, context)
    manager.commit_pass()

    assert manager.get_current(_SLOT_1) is context
    assert binding.ref_count == 1
    assert binding.cleanup_count == 0


def test_rollback_closes_staged_new_context_and_preserves_old_current() -> None:
    manager = CallSiteContextManager()
    binding_old = _FakeBinding()
    binding_new = _FakeBinding()

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    current = CallSiteContext(binding=binding_old, function_identity="old", last_args=CallSiteArgs.capture(1))
    manager.stage(_SLOT_1, current)
    manager.commit_pass()

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    staged = CallSiteContext(binding=binding_new, function_identity="new", last_args=CallSiteArgs.capture(2))
    manager.stage(_SLOT_1, staged)
    manager.rollback_pass()

    assert manager.get_current(_SLOT_1) is current
    assert binding_old.ref_count == 1
    assert binding_old.cleanup_count == 0
    assert binding_new.ref_count == 0
    assert binding_new.cleanup_count == 1


def test_commit_closes_old_current_and_promotes_staged_new() -> None:
    manager = CallSiteContextManager()
    binding_old = _FakeBinding()
    binding_new = _FakeBinding()

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    current = CallSiteContext(binding=binding_old, function_identity="old", last_args=CallSiteArgs.capture(1))
    manager.stage(_SLOT_1, current)
    manager.commit_pass()

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    staged = CallSiteContext(binding=binding_new, function_identity="new", last_args=CallSiteArgs.capture(2))
    manager.stage(_SLOT_1, staged)
    manager.commit_pass()

    assert manager.get_current(_SLOT_1) is staged
    assert binding_old.ref_count == 0
    assert binding_old.cleanup_count == 1
    assert binding_new.ref_count == 1
    assert binding_new.cleanup_count == 0


def test_unvisited_current_context_closes_on_commit() -> None:
    manager = CallSiteContextManager()
    binding = _FakeBinding()

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    context = CallSiteContext(binding=binding, function_identity="fn", last_args=CallSiteArgs.capture())
    manager.stage(_SLOT_1, context)
    manager.commit_pass()

    manager.begin_pass()
    manager.commit_pass()

    assert manager.get_current(_SLOT_1) is None
    assert binding.ref_count == 0
    assert binding.cleanup_count == 1


def test_close_all_closes_current_and_staged_contexts() -> None:
    manager = CallSiteContextManager()
    binding_current = _FakeBinding()
    binding_staged = _FakeBinding()

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    current = CallSiteContext(binding=binding_current, function_identity="fn", last_args=CallSiteArgs.capture())
    manager.stage(_SLOT_1, current)
    manager.commit_pass()

    manager.begin_pass()
    manager.mark_visited(_SLOT_2)
    staged = CallSiteContext(binding=binding_staged, function_identity="next", last_args=CallSiteArgs.capture())
    manager.stage(_SLOT_2, staged)

    manager.close_all()

    assert manager.get_current(_SLOT_1) is None
    assert manager.get_current(_SLOT_2) is None
    assert binding_current.ref_count == 0
    assert binding_current.cleanup_count == 1
    assert binding_staged.ref_count == 0
    assert binding_staged.cleanup_count == 1


def test_context_close_is_idempotent() -> None:
    binding = _FakeBinding()
    context = CallSiteContext(binding=binding, function_identity="fn", last_args=CallSiteArgs.capture())

    assert binding.ref_count == 1

    context.close()
    context.close()

    assert binding.ref_count == 0
    assert binding.cleanup_count == 1


def test_call_site_binding_base_tracks_accepted_state() -> None:
    binding = _FakeBinding()

    assert binding.is_accepted is False
    binding.accepted()
    assert binding.is_accepted is True

    binding.dec_ref()

    assert binding.cleanup_count == 1


def test_multiple_call_sites_are_isolated_by_slot_id() -> None:
    manager = CallSiteContextManager()
    binding_1 = _FakeBinding()
    binding_2 = _FakeBinding()

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    manager.mark_visited(_SLOT_2)
    context_1 = CallSiteContext(binding=binding_1, function_identity="one", last_args=CallSiteArgs.capture(1))
    context_2 = CallSiteContext(binding=binding_2, function_identity="two", last_args=CallSiteArgs.capture(2))
    manager.stage(_SLOT_1, context_1)
    manager.stage(_SLOT_2, context_2)
    manager.commit_pass()

    assert manager.get_current(_SLOT_1) is context_1
    assert manager.get_current(_SLOT_2) is context_2

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    manager.commit_pass()

    assert manager.get_current(_SLOT_1) is context_1
    assert manager.get_current(_SLOT_2) is None
    assert binding_1.ref_count == 1
    assert binding_1.cleanup_count == 0
    assert binding_2.ref_count == 0
    assert binding_2.cleanup_count == 1


def test_reusing_binding_across_immutable_contexts_refcounts_correctly() -> None:
    manager = CallSiteContextManager()
    binding = _FakeBinding()

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    current = CallSiteContext(
        binding=binding,
        function_identity="fn",
        last_args=CallSiteArgs.capture(1, value="a"),
        invoke_state_value=CallSiteInvokeState.NOT_SET,
    )
    manager.stage(_SLOT_1, current)
    manager.commit_pass()

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    replacement = current.replace(
        last_args=CallSiteArgs.capture(2, value="b"),
        invoke_state_value=CallSiteInvokeState.DIRTY_SET,
    )
    manager.stage(_SLOT_1, replacement)

    assert binding.ref_count == 2
    assert binding.cleanup_count == 0

    manager.commit_pass()

    assert manager.get_current(_SLOT_1) is replacement
    assert binding.ref_count == 1
    assert binding.cleanup_count == 0

    manager.close_all()

    assert binding.ref_count == 0
    assert binding.cleanup_count == 1


def test_rollback_with_reused_binding_keeps_binding_alive() -> None:
    manager = CallSiteContextManager()
    binding = _FakeBinding()

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    current = CallSiteContext(binding=binding, function_identity="fn", last_args=CallSiteArgs.capture(1))
    manager.stage(_SLOT_1, current)
    manager.commit_pass()

    manager.begin_pass()
    manager.mark_visited(_SLOT_1)
    staged = current.replace(last_args=CallSiteArgs.capture(2))
    manager.stage(_SLOT_1, staged)

    assert binding.ref_count == 2
    assert binding.cleanup_count == 0

    manager.rollback_pass()

    assert manager.get_current(_SLOT_1) is current
    assert binding.ref_count == 1
    assert binding.cleanup_count == 0


def test_replace_creates_fresh_close_state() -> None:
    binding = _FakeBinding()
    current = CallSiteContext(binding=binding, function_identity="fn", last_args=CallSiteArgs.capture(1))
    replacement = current.replace(last_args=CallSiteArgs.capture(2))

    assert current._close_state is not replacement._close_state
    assert current.invoke_state is not replacement.invoke_state


def test_replace_preserves_and_overrides_mutable_state_values() -> None:
    current = CallSiteContext(
        binding=None,
        function_identity="fn",
        last_args=CallSiteArgs.capture(1),
        invoke_state_value=CallSiteInvokeState.DIRTY_SET,
    )

    preserved = current.replace(last_args=CallSiteArgs.capture(2))
    overridden = current.replace(invoke_state_value=CallSiteInvokeState.GET_SET)

    assert preserved.invoke_state.value is CallSiteInvokeState.DIRTY_SET
    assert overridden.invoke_state.value is CallSiteInvokeState.GET_SET


def test_invoke_state_upgrades_get_to_dirty_and_dirty_dominates_get() -> None:
    context = CallSiteContext(
        binding=None,
        function_identity="fn",
        last_args=CallSiteArgs.capture(1),
        invoke_state_value=CallSiteInvokeState.NOT_SET,
    )

    context.mark_invoke_get()
    assert context.invoke_state.value is CallSiteInvokeState.GET_SET

    context.mark_invoke_dirty()
    assert context.invoke_state.value is CallSiteInvokeState.DIRTY_SET

    context.mark_invoke_get()
    assert context.invoke_state.value is CallSiteInvokeState.DIRTY_SET
