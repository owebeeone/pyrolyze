from __future__ import annotations

from dataclasses import dataclass

import pytest

from pyrolyze.runtime import context_lcm as runtime
from pyrolyze.runtime import context_original


module_registry = runtime.ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.test_runtime_context_lcm_phase3")


def _slot(index: int) -> runtime.SlotId:
    return runtime.SlotId(_MODULE_ID, index, line_no=10 + index)


def _root() -> runtime.RenderContext:
    root = runtime.RenderContext()
    root.begin_pass()
    return root


def test_event_handler_slot_context_stages_commits_and_rolls_back_callbacks() -> None:
    root = _root()
    slot = runtime.EventHandlerSlotContext(render_context=root, parent=root, slot_id=_slot(1))

    calls: list[str] = []
    dispatch = slot.stage_callback(callback=lambda: calls.append("first"), dirty=True)
    slot.commit_handler()
    root.rollback_pass()

    dispatch()
    assert calls == ["first"]

    root.begin_pass()
    slot.stage_callback(callback=lambda: calls.append("second"), dirty=True)
    slot.rollback_handler()
    root.rollback_pass()

    dispatch()
    assert calls == ["first", "first"]


def test_event_handler_slot_context_deactivate_clears_committed_handler() -> None:
    root = _root()
    slot = runtime.EventHandlerSlotContext(render_context=root, parent=root, slot_id=_slot(2))

    dispatch = slot.stage_callback(callback=lambda: None, dirty=True)
    slot.commit_handler()
    root.rollback_pass()

    slot.deactivate()

    with pytest.raises(RuntimeError, match="event handler is inactive"):
        dispatch()


def test_leaf_slot_context_tracks_last_call_arguments() -> None:
    root = _root()
    slot = runtime.LeafSlotContext(render_context=root, parent=root, slot_id=_slot(3))

    result = slot.invoke(lambda a, *, flag: (a, flag), (1,), {"flag": True})

    assert result == (1, True)
    assert slot.last_args == (1,)
    assert slot.last_kwargs == (("flag", True),)

    root.rollback_pass()


def test_leaf_slot_context_invoke_native_rolls_back_scope_but_keeps_last_args() -> None:
    root = _root()
    slot = runtime.LeafSlotContext(render_context=root, parent=root, slot_id=_slot(4))

    with pytest.raises(TypeError, match="@pyrolyze functions must return None"):
        slot.invoke_native(
            lambda _ctx, value: value,
            (7,),
            {},
            context_param="ctx",
        )

    assert slot.last_args == (7,)
    assert slot.last_kwargs == ()
    assert slot._scope_active is False

    root.rollback_pass()


def test_container_slot_context_commits_native_root_through_scope_pass() -> None:
    root = _root()
    slot = runtime.ContainerSlotContext(render_context=root, parent=root, slot_id=_slot(5))
    slot._staged_ui = [runtime.UIElement(kind="div", props={}, children=(), call_site_id=None, slot_id=None)]
    slot._staged_ui_entries = [
        context_original._CommittedUiEntry(generation_id=slot.current_generation_id(), element=slot._staged_ui[0])
    ]

    assert slot.committed_native_root is False

    slot._begin_scope_pass()
    slot.expects_native_root = True
    slot._staged_ui = [runtime.UIElement(kind="div", props={}, children=(), call_site_id=None, slot_id=None)]
    slot._staged_ui_entries = [
        context_original._CommittedUiEntry(generation_id=slot.current_generation_id(), element=slot._staged_ui[0])
    ]
    slot._commit_scope_pass()

    assert slot.committed_native_root is True

    root.rollback_pass()


def test_container_slot_context_rolls_back_committed_native_root() -> None:
    root = _root()
    slot = runtime.ContainerSlotContext(render_context=root, parent=root, slot_id=_slot(6))

    slot._begin_scope_pass()
    slot.expects_native_root = True
    slot._staged_ui = [runtime.UIElement(kind="div", props={}, children=(), call_site_id=None, slot_id=None)]
    slot._staged_ui_entries = [
        context_original._CommittedUiEntry(generation_id=slot.current_generation_id(), element=slot._staged_ui[0])
    ]
    slot._commit_scope_pass()

    assert slot.committed_native_root is True

    slot._begin_scope_pass()
    slot.expects_native_root = False
    slot._rollback_scope_pass()

    assert slot.committed_native_root is True

    root.rollback_pass()


def test_context_lcm_exports_lifecycle_backed_phase3_classes() -> None:
    assert runtime.__PYROLYZE_CONTEXT_IMPLEMENTATION__ == "lcm"
    assert runtime.EventHandlerSlotContext.__module__ == "pyrolyze.runtime.context_lcm"
    assert runtime.ContainerSlotContext.__module__ == "pyrolyze.runtime.context_lcm"
    assert runtime.LeafSlotContext.__module__ == "pyrolyze.runtime.context_lcm"
