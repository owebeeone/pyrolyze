from __future__ import annotations

import pytest

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_state_lcm.pass_state_render import _enable_pass_state_render
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from pyrolyze.runtime.pyro_call import PyrolyzeWrap


@pytest.mark.parametrize("callback_failure", (False, True))
def test_caught_preparation_failure_discards_candidates_and_allows_retry(
    callback_failure: bool,
) -> None:
    namespace = load_transformed_namespace(
        'from pyrolyze.api import pyrolyze, UIElement, call_native\n'
        '@pyrolyze\n'
        'def child(kind):\n'
        '    call_native(UIElement)(kind=kind, props={})\n',
        module_name="preparation_failure_boundary",
    )
    failure = ValueError("preparation failed")

    class FailingComponent(PyrolyzeWrap):
        def resolve(self, *, args: object, kwargs: object) -> object:
            raise failure

    class FailingCallback:
        def __call__(self) -> None:
            pass

        @property
        def __self__(self) -> object:
            raise failure

    root = runtime.RenderContext()
    _enable_pass_state_render(root._state_mgr)
    slot_id = runtime.SlotId(runtime.ModuleId("preparation-failure"), 1)
    failure_id = runtime.SlotId(runtime.ModuleId("preparation-failure"), 2)

    def select(kind: str) -> None:
        root.component_call(slot_id, namespace["child"], kind, dirty_state=runtime.dirtyof())

    with root.pass_scope():
        select("accepted")
    accepted = root._state_mgr.current.children_state
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            select("candidate")
            with pytest.raises(ValueError) as caught:
                if callback_failure:
                    root._state_mgr.event_handler(
                        failure_id, dirty=True, callback=FailingCallback()
                    )
                else:
                    root.component_call(
                        failure_id, FailingComponent(namespace["child"]),
                        dirty_state=runtime.dirtyof(),
                    )
            assert caught.value is failure
    assert root._state_mgr.current.children_state is accepted
    assert [node.kind for node in root.debug_ui()] == ["accepted"]
    assert root._state_mgr._field_only_completion.last.first_failure is failure
    with root.pass_scope():
        select("retry")
    assert [node.kind for node in root.debug_ui()] == ["retry"]
