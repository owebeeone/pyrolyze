from __future__ import annotations

import pytest

from pyrolyze.api import UIElement
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_bare_refactor_lcm import (
    ContextBase,
    ContainerCallRuntimeContext,
)
from pyrolyze.runtime.context_state_lcm.container_render import _enable_container_render
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from pyrolyze.runtime.pyro_call import PyrolyzeWrap, ResolvedPyrolyzeCall


def root_and_id():
    root = runtime.RenderContext()
    _enable_container_render(root._state_mgr)
    return root, runtime.SlotId(runtime.ModuleId("container-faults"), 1)


def test_opaque_container_is_rejected_before_construction_or_invocation() -> None:
    root, slot_id = root_and_id()
    calls = []

    def opaque():
        calls.append("called")

    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with pytest.raises(RuntimeError, match="opaque container"):
                root.container_call(slot_id, opaque)
            assert slot_id not in root._state_mgr._slots_by_id
            assert slot_id not in root._state_mgr.children_state
    assert calls == []


def test_annotated_mount_helper_cannot_enter_an_external_context_manager() -> None:
    root, slot_id = root_and_id()
    calls = []

    class ExternalHost:
        def __enter__(self):
            calls.append("enter")

        def __exit__(self, *args):
            calls.append("exit")

    def helper(*, runtime: ContainerCallRuntimeContext):
        return ExternalHost()

    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with pytest.raises(RuntimeError, match="directive scope"):
                with root.container_call(slot_id, helper):
                    pass
    assert calls == []


@pytest.mark.parametrize("compiled", [False, True])
def test_caught_container_evaluation_failure_preserves_cause(compiled) -> None:
    root, slot_id = root_and_id()
    error = ValueError("container evaluation")

    def fail(ctx: ContextBase):
        raise error

    if compiled:
        namespace = load_transformed_namespace(
            """
from pyrolyze.api import pyrolyze

def fail():
    raise ValueError("container evaluation")

@pyrolyze
def frame():
    fail()
""",
            module_name="container_evaluation_fault",
        )
        fail = namespace["frame"]
    with pytest.raises(RenderAttemptAborted) as caught:
        with root.pass_scope():
            with pytest.raises(ValueError) as original:
                with root.container_call(slot_id, fail):
                    pass
    assert caught.value.__cause__ is original.value
    assert root.debug_ui() == ()


@pytest.mark.parametrize("roots", [0, 2])
def test_invalid_native_root_aborts_attempt(roots) -> None:
    root, slot_id = root_and_id()

    def native(ctx: ContextBase):
        for _ in range(roots):
            ctx.call_native(UIElement, kind="root", props={})

    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with pytest.raises(RuntimeError, match="exactly one root"):
                with root.container_call(slot_id, native):
                    pass
    assert root.debug_ui() == ()


def test_resolution_cannot_construct_into_replacement_transaction() -> None:
    root, slot_id = root_and_id()
    manager = root._state_mgr._transaction_manager

    def native(ctx: ContextBase):
        ctx.call_native(UIElement, kind="root", props={})

    class ReplacingWrap(PyrolyzeWrap):
        def resolve(self, *, args, kwargs):
            manager.rollback(PASS_TX_KEY)
            manager.begin(PASS_TX_KEY)
            return ResolvedPyrolyzeCall(self.func, args, kwargs)

    with pytest.raises((RuntimeError, BaseExceptionGroup)):
        with root.pass_scope():
            root.container_call(slot_id, ReplacingWrap(native))
    assert slot_id not in root._state_mgr._slots_by_id
    assert root._state_mgr.children_state == {}
    assert manager.active_transaction_for(PASS_TX_KEY) is not None
    manager.rollback(PASS_TX_KEY)


def test_container_entry_cannot_publish_after_transaction_replacement() -> None:
    root, slot_id = root_and_id()
    manager = root._state_mgr._transaction_manager

    def native(ctx: ContextBase):
        ctx.call_native(UIElement, kind="never published", props={})
        manager.rollback(PASS_TX_KEY)
        manager.begin(PASS_TX_KEY)

    with pytest.raises((RuntimeError, BaseExceptionGroup)):
        with root.pass_scope():
            with root.container_call(slot_id, native):
                pass
    assert root.debug_ui() == ()
    assert manager.active_transaction_for(PASS_TX_KEY) is not None
    manager.rollback(PASS_TX_KEY)


def test_stale_handle_cannot_join_a_new_attempt() -> None:
    root, slot_id = root_and_id()

    def native(ctx: ContextBase):
        ctx.call_native(UIElement, kind="root", props={})

    with root.pass_scope():
        handle = root.container_call(slot_id, native)
    with root.pass_scope():
        with pytest.raises(RuntimeError, match="finished"):
            with handle:
                pass
    assert root._state_mgr._field_only_completion.last.published
