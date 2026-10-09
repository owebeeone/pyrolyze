"""Desired selection outcomes, independently of the eventual admission fix."""

from typing import Any

import pytest

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.context_base import ContextBaseStateMgr
from pyrolyze.runtime.context_state_lcm.pass_state_render import (
    _enable_pass_state_render,
)
from pyrolyze.runtime.pyro_call import PyrolyzeComponentWrap


def _scenario(container: bool) -> tuple[Any, dict[str, Any], Any]:
    namespace = load_transformed_namespace(
        """
from pyrolyze.api import ComponentRef, UIElement, call_native, pyrolyze, pyrolyze_slotted
from pyrolyze.runtime.slot_call_semantics import ExternalStoreRef
calls = []
resource_calls = []
def subscribe(callback):
    resource_calls.append('subscribe')
    return lambda: resource_calls.append('unsubscribe')
@pyrolyze_slotted
def observe():
    return ExternalStoreRef('selection-resource', subscribe, lambda: 1)
@pyrolyze
def first():
    calls.append('first')
    observe()
    call_native(UIElement)(kind='first', props={})
@pyrolyze
def second():
    calls.append('second')
    call_native(UIElement)(kind='second', props={})
@pyrolyze
def panel(target: ComponentRef):
""" + ("    with target():\n        pass\n" if container else "    target()\n"),
        module_name="slot_selection_outcomes",
    )
    root = runtime.RenderContext()
    _enable_pass_state_render(root._state_mgr)
    slot_id = runtime.SlotId(runtime.ModuleId("selection-outcomes"), 1)

    def render(target: Any, *, dirty: bool = True) -> None:
        root.component_call(
            slot_id,
            namespace["panel"],
            target,
            dirty_state=runtime.dirtyof(target=dirty),
        )

    with root.pass_scope():
        render(namespace["first"])
    assert [node.kind for node in root.debug_ui()] == ["first"]
    return root, namespace, render


@pytest.mark.parametrize("container", [False, True], ids=["component", "container"])
def test_clean_skip_retains_output_without_execution(container: bool) -> None:
    root, namespace, render = _scenario(container)
    with root.pass_scope():
        render(namespace["first"], dirty=False)
    assert [node.kind for node in root.debug_ui()] == ["first"]
    assert namespace["calls"] == ["first"]
    assert namespace["resource_calls"] == ["subscribe"]


@pytest.mark.parametrize("container", [False, True], ids=["component", "container"])
def test_dirty_replacement_publishes_new_output(container: bool) -> None:
    root, namespace, render = _scenario(container)
    with root.pass_scope():
        render(namespace["second"])
    assert [node.kind for node in root.debug_ui()] == ["second"]
    assert namespace["calls"] == ["first", "second"]
    assert namespace["resource_calls"] == ["subscribe", "unsubscribe"]


@pytest.mark.parametrize("container", [False, True], ids=["component", "container"])
def test_dirty_null_selection_removes_previous_output(container: bool) -> None:
    root, namespace, render = _scenario(container)
    with root.pass_scope():
        render(PyrolyzeComponentWrap(None))
        assert namespace["resource_calls"] == ["subscribe"]
    assert root.debug_ui() == ()
    assert namespace["calls"] == ["first"]
    assert namespace["resource_calls"] == ["subscribe", "unsubscribe"]


@pytest.mark.parametrize("remove", [False, True], ids=["replace", "remove"])
@pytest.mark.parametrize("container", [False, True], ids=["component", "container"])
def test_outer_rollback_preserves_previous_selection(
    remove: bool, container: bool
) -> None:
    root, namespace, render = _scenario(container)
    target = PyrolyzeComponentWrap(None) if remove else namespace["second"]
    with pytest.raises(ValueError, match="abort outer render"):
        with root.pass_scope():
            render(target)
            raise ValueError("abort outer render")
    assert [node.kind for node in root.debug_ui()] == ["first"]
    assert namespace["resource_calls"] == ["subscribe"]


def test_clean_retention_cannot_acknowledge_a_new_invalidation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, namespace, render = _scenario(False)
    original = ContextBaseStateMgr.retain_slot
    notified: list[Any] = []

    def retain(self: Any, slot_id: Any, **kwargs: Any) -> None:
        slot = self.root_context_state_mgr().get_registered_slot(
            self.resolve_slot_id(slot_id)
        )
        self.queue_invalidation_from(slot)
        notified.append(slot)
        original(self, slot_id, **kwargs)

    monkeypatch.setattr(ContextBaseStateMgr, "retain_slot", retain)
    with root.pass_scope():
        render(namespace["first"], dirty=False)
    assert len(notified) == 1
    assert notified[0].invoke_dirty
    assert namespace["calls"] == ["first"]
