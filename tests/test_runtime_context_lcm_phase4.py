from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import pytest

from pyrolyze.api import (
    MountDirective,
    MountSelector,
    PyrolyzeMountAdvertisement,
    PyrolyzeMountAdvertisementRequest,
    UIElement,
    no_emit,
    validate_mount_selectors,
)
from pyrolyze.runtime.call_site_context import CallSiteArgs, CallSiteContext
from pyrolyze.runtime import context_lcm as runtime
from pyrolyze.runtime.slot_call_semantics import PyrolyzeMountAdvertisementBinding, SlotCallBinding, SlotCallBindingHost
from pyrolyze.runtime.slot_expr import _SlotExprCallSiteBinding


module_registry = runtime.ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.test_runtime_context_lcm_phase4")


def _slot(index: int) -> runtime.SlotId:
    return runtime.SlotId(_MODULE_ID, index, line_no=20 + index)


def _root() -> runtime.RenderContext:
    root = runtime.RenderContext()
    root.begin_pass()
    return root


@dataclass(slots=True)
class SpySlotBinding(SlotCallBinding):
    value: Any
    commit_count: int = 0
    rollback_count: int = 0
    deactivate_count: int = 0

    def exposed_value(self) -> Any:
        return self.value

    def commit(self) -> None:
        self.commit_count += 1

    def rollback(self) -> None:
        self.rollback_count += 1

    def deactivate(self) -> None:
        self.deactivate_count += 1


@dataclass(slots=True)
class _AdvertHost(SlotCallBindingHost):
    published: list[PyrolyzeMountAdvertisementRequest]
    source_slot_id: Any
    surface_owner_id: Any
    withdrawn: int = 0

    def queue_slot_call_invalidation(self) -> None:
        return None

    def mark_slot_call_refresh_only(self) -> None:
        return None

    def enqueue_slot_call_post_commit(self, callback: Callable[[], None]) -> None:
        callback()

    def publish_slot_call_mount_advertisement(
        self,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> PyrolyzeMountAdvertisement:
        self.published.append(request)
        return PyrolyzeMountAdvertisement(
            key=request.key,
            selectors=request.selectors,
            default=request.default,
            source_slot_id=self.source_slot_id,
            surface_owner_id=self.surface_owner_id,
        )

    def withdraw_slot_call_mount_advertisement(self) -> None:
        self.withdrawn += 1


def test_slot_call_slot_context_evaluate_tracks_inputs_and_returns_value() -> None:
    root = _root()
    slot = runtime.SlotCallSlotContext(render_context=root, parent=root, slot_id=_slot(1))

    result = slot.evaluate(lambda value, *, flag: value + (1 if flag else 0), (2,), {"flag": True})

    assert result.value == 3
    assert slot.last_args == (2,)
    assert slot.last_kwargs == (("flag", True),)
    assert slot.binding is not None

    root.rollback_pass()


def test_slot_call_slot_context_binding_hooks_delegate_to_binding() -> None:
    root = _root()
    slot = runtime.SlotCallSlotContext(render_context=root, parent=root, slot_id=_slot(2))
    binding = SpySlotBinding("value")
    slot.binding = binding

    slot.commit_binding()
    slot.rollback_binding()
    slot.deactivate()

    assert binding.commit_count == 1
    assert binding.rollback_count == 1
    assert binding.deactivate_count == 1
    assert slot.binding is None

    root.rollback_pass()


def test_slot_expr_slot_context_stages_merges_and_commits_callbacks() -> None:
    root = _root()
    slot = runtime.SlotExprSlotContext(render_context=root, parent=root, slot_id=_slot(3))
    call_slot = _slot(30)
    binding = SpySlotBinding("value")
    wrapped = _SlotExprCallSiteBinding(binding=binding)
    callback_calls: list[str] = []

    slot.call_site_context_manager.begin_pass()
    slot.call_site_context_manager.mark_visited(call_slot)
    slot.call_site_context_manager.stage(
            call_slot,
            CallSiteContext(
                binding=wrapped,
                function_identity="fn",
                last_args=CallSiteArgs.capture(),
            ),
    )

    slot.stage_slot_expr_pass(
        visited_call_site_ids=(call_slot,),
        post_commit_callbacks=(lambda: callback_calls.append("first"),),
    )
    slot.append_slot_expr_post_commit_callback(lambda: callback_calls.append("second"))
    slot.commit_binding()

    assert binding.commit_count == 1
    assert callback_calls == ["first", "second"]
    assert slot.call_site_context_manager.get_current(call_slot) is not None
    assert slot._staged_call_site_ids == ()
    assert slot._staged_post_commit_callbacks == ()

    root.rollback_pass()


def test_slot_expr_slot_context_rolls_back_visible_binding_and_clears_stage() -> None:
    root = _root()
    slot = runtime.SlotExprSlotContext(render_context=root, parent=root, slot_id=_slot(4))
    call_slot = _slot(40)
    binding = SpySlotBinding("value")
    wrapped = _SlotExprCallSiteBinding(binding=binding)

    slot.call_site_context_manager.begin_pass()
    slot.call_site_context_manager.mark_visited(call_slot)
    slot.call_site_context_manager.stage(
            call_slot,
            CallSiteContext(
                binding=wrapped,
                function_identity="fn",
                last_args=CallSiteArgs.capture(),
            ),
    )
    slot.stage_slot_expr_pass(visited_call_site_ids=(call_slot,), post_commit_callbacks=())
    slot.rollback_binding()

    assert binding.rollback_count == 1
    assert slot.call_site_context_manager.get_current(call_slot) is None
    assert slot._staged_call_site_ids == ()
    assert slot._staged_post_commit_callbacks == ()

    root.rollback_pass()


def test_slot_expr_slot_context_runtime_locals_and_deactivate() -> None:
    root = _root()
    slot = runtime.SlotExprSlotContext(render_context=root, parent=root, slot_id=_slot(5))
    call_slot = _slot(50)
    binding = SpySlotBinding("value")
    wrapped = _SlotExprCallSiteBinding(binding=binding)

    locals_a = slot.runtime_locals(call_slot)
    locals_a["count"] = 1
    assert slot.runtime_locals(call_slot) is locals_a

    slot.call_site_context_manager.begin_pass()
    slot.call_site_context_manager.mark_visited(call_slot)
    slot.call_site_context_manager.stage(
            call_slot,
            CallSiteContext(
                binding=wrapped,
                function_identity="fn",
                last_args=CallSiteArgs.capture(),
            ),
    )
    slot.call_site_context_manager.commit_pass()

    slot.deactivate()

    assert binding.deactivate_count == 1
    assert slot.runtime_locals(call_slot) == {}
    assert slot._committed_ui == ()

    root.rollback_pass()


def test_slot_expr_slot_context_syncs_committed_ui_from_current_call_sites() -> None:
    root = _root()
    slot = runtime.SlotExprSlotContext(render_context=root, parent=root, slot_id=_slot(6))
    call_slot = _slot(60)
    request = PyrolyzeMountAdvertisementRequest(
        key="anchor",
        selectors=(MountSelector.named("a"),),
        default=False,
    )
    host = _AdvertHost(published=[], source_slot_id=call_slot, surface_owner_id=slot.slot_id)
    binding = PyrolyzeMountAdvertisementBinding.bind(host, request)
    binding.commit()
    wrapped = _SlotExprCallSiteBinding(binding=binding)

    slot.call_site_context_manager.begin_pass()
    slot.call_site_context_manager.mark_visited(call_slot)
    slot.call_site_context_manager.stage(
            call_slot,
            CallSiteContext(
                binding=wrapped,
                function_identity="fn",
                last_args=CallSiteArgs.capture(),
            ),
    )
    slot.call_site_context_manager.commit_pass()
    slot.sync_committed_ui()

    assert len(slot._committed_ui) == 1
    assert slot._committed_ui[0].key == "anchor"

    root.rollback_pass()


def test_directive_slot_context_rolls_back_no_emit_children_without_super_type_error() -> None:
    root = runtime.RenderContext()

    with pytest.raises(RuntimeError, match="no_emit"):
        with root.pass_scope():
            with root.open_directive(_slot(61), validate_mount_selectors, no_emit) as mount_ctx:
                mount_ctx.call_native(UIElement, kind="badge", props={"text": "Hidden"})

    assert root.debug_ui() == ()


def test_directive_slot_context_commits_mount_directive_tree() -> None:
    root = runtime.RenderContext()
    selector = MountSelector.named("menu")

    with root.pass_scope():
        with root.open_directive(_slot(62), validate_mount_selectors, selector) as mount_ctx:
            mount_ctx.call_native(UIElement, kind="badge", props={"text": "File"})

    assert root.debug_ui() == (
        MountDirective(
            selectors=(selector,),
            children=(UIElement(kind="badge", props={"text": "File"}),),
        ),
    )
