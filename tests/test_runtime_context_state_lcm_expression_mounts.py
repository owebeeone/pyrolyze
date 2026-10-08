from __future__ import annotations

from typing import Any

import pytest

from pyrolyze.api import UIElement, advertise_mount
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_bare_refactor_lcm import ContextBase
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.mount_expr_render import (
    _enable_mount_expr_render,
)
from pyrolyze.runtime.context_state_lcm._support import (
    DuplicateMountAdvertisementError,
    MountAdvertisementContextError,
)
from pyrolyze.runtime.dirt import DM
from pyrolyze.runtime.slot_call_semantics import UseEffectRequest
from pyrolyze.runtime.slot_expr import (
    LiteralFunctionProvider,
    slot_params,
    slot_params_dirt,
)
from tests.test_runtime_context_state_lcm_expression_effects import _evaluate as _effect


def _id(index: int) -> Any:
    return runtime.SlotId(runtime.ModuleId("tests.expression_mount_faults"), index)


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_mount_expr_render(root._state_mgr)
    return root


def _native(ctx: ContextBase) -> None:
    ctx._state_mgr.own_ui_state = (UIElement(kind="section", props={}),)


def _select(container: Any, key: Any, *, default: bool = False, index: int = 2) -> Any:
    expression = container.slot_expr(
        _id(index), lambda v: v.eval(), lambda v: v.dirty()
    )
    expression.slot_call(
        "v",
        LiteralFunctionProvider(advertise_mount),
        lambda: slot_params(key, default=default),
        lambda: slot_params_dirt(),
        slot_id=_id(9),
    )
    expression.apply_dirt_sink(DM()).evaluate()
    return expression.call_site_context_manager


@pytest.mark.parametrize("collision", ("key", "default"))
def test_surface_validation_combines_expression_and_ordinary_calls(
    collision: str,
) -> None:
    root = _root()
    events: list[str] = []
    with root.pass_scope():
        with root.container_call(_id(1), _native) as container:
            _select(container, "accepted")
    with pytest.raises(DuplicateMountAdvertisementError):
        with root.pass_scope():
            with root.container_call(_id(1), _native) as container:
                _select(container, "candidate", default=collision == "default")
                slot = container._ensure_slot(_id(9), runtime.SlotCallSlotContext)
                slot.evaluate(
                    advertise_mount,
                    ("candidate" if collision == "key" else "other",),
                    {"default": collision == "default"},
                )
                _effect(container, UseEffectRequest(lambda: events.append("setup")))
    assert [item.key for item in root.debug_mount_advertisements()] == ["accepted"]
    assert root.debug_ui()[0].children[0].key == "accepted"
    assert events == []
    assert root._state_mgr._field_only_completion.last.published is False


def test_separate_expression_collections_cannot_overwrite_duplicate_entries() -> None:
    root = _root()
    with pytest.raises(DuplicateMountAdvertisementError):
        with root.pass_scope():
            with root.container_call(_id(1), _native) as container:
                _select(container, "same", index=2)
                _select(container, "same", index=3)
    assert root.debug_mount_advertisements() == ()


def test_missing_native_owner_rejects_expression_before_publication() -> None:
    root = _root()
    with pytest.raises(MountAdvertisementContextError, match="native container owner"):
        with root.pass_scope():
            _select(root, "invalid")
    assert root.debug_mount_advertisements() == ()
    assert root._state_mgr._field_only_completion.last.published is False


def test_key_comparison_replacing_token_cannot_publish_candidate_surface() -> None:
    root = _root()
    manager = root._state_mgr._transaction_manager
    replacement: Any = None
    with root.pass_scope():
        with root.container_call(_id(1), _native) as container:
            collection = _select(container, "accepted")
    accepted = collection.iter_current()[0]

    class Key:
        def __eq__(self, other: object) -> bool:
            nonlocal replacement
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
            return False

    with pytest.raises((RuntimeError, BaseExceptionGroup)):
        with root.pass_scope():
            with root.container_call(_id(1), _native) as container:
                _select(container, "first", index=2)
                _select(container, Key(), index=3)
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert collection.iter_current()[0] is accepted
    assert [item.key for item in root.debug_mount_advertisements()] == ["accepted"]
    manager.rollback(PASS_TX_KEY)
