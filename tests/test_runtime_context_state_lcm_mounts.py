from __future__ import annotations

from typing import Any

import pytest

from pyrolyze.api import UIElement, advertise_mount
from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.context_bare_refactor_lcm import ContextBase
from pyrolyze.runtime.context_state_lcm.context_base import PASS_TX_KEY
from pyrolyze.runtime.context_state_lcm.mount_render import _enable_mount_render
from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted
from pyrolyze.runtime.context_state_lcm._support import (
    DuplicateMountAdvertisementError,
    MountAdvertisementContextError,
)
from pyrolyze.runtime.slot_call_semantics import UseEffectRequest


def _root() -> Any:
    root = runtime.RenderContext()
    _enable_mount_render(root._state_mgr)
    return root


def _id(index: int) -> Any:
    return runtime.SlotId(runtime.ModuleId("tests.mount_faults"), index)


def _native(ctx: ContextBase) -> None:
    ctx._state_mgr.own_ui_state = (UIElement(kind="section", props={}),)


def _select(
    container: Any, key: object, index: int = 2, *, default: bool = False
) -> Any:
    slot = container._ensure_slot(_id(index), runtime.SlotCallSlotContext)
    slot.evaluate(advertise_mount, (key,), {"default": default})
    return slot


@pytest.mark.parametrize("collision", ("key", "default"))
def test_duplicate_candidate_surface_is_discarded_before_effect_delivery(
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
                _select(container, "new", default=collision == "default")
                _select(
                    container,
                    "new" if collision == "key" else "other",
                    3,
                    default=collision == "default",
                )
                effect = container._ensure_slot(_id(4), runtime.SlotCallSlotContext)
                effect.evaluate(
                    lambda: UseEffectRequest(lambda: events.append("setup")), (), {}
                )
    assert [advert.key for advert in root.debug_mount_advertisements()] == ["accepted"]
    assert root.debug_ui()[0].children[0].key == "accepted"
    assert events == []
    assert root._state_mgr._field_only_completion.last.published is False
    with root.pass_scope():
        with root.container_call(_id(1), _native) as container:
            _select(container, "retry")
    assert [advert.key for advert in root.debug_mount_advertisements()] == ["retry"]


def test_root_owner_rejection_is_still_transactional() -> None:
    root = _root()
    with pytest.raises(MountAdvertisementContextError, match="native container owner"):
        with root.pass_scope():
            _select(root, "invalid")
    assert root.debug_mount_advertisements() == ()
    assert root._state_mgr.current.children_state == {}


def test_duplicate_key_comparison_cannot_publish_under_replacement_token() -> None:
    root = _root()
    manager = root._state_mgr._transaction_manager
    replacement: Any = None

    class Key:
        def __eq__(self, other: object) -> bool:
            nonlocal replacement
            manager.rollback(PASS_TX_KEY)
            replacement = manager.begin(PASS_TX_KEY)
            return False

    with pytest.raises(BaseException):
        with root.pass_scope():
            with root.container_call(_id(1), _native) as container:
                _select(container, "first")
                _select(container, Key(), 3)
    assert manager.active_transaction_for(PASS_TX_KEY) is replacement
    assert root.debug_mount_advertisements() == ()
    manager.rollback(PASS_TX_KEY)


def test_opaque_container_factory_is_rejected_before_external_work() -> None:
    root = _root()
    events: list[str] = []

    def factory() -> None:
        events.append("called")

    with pytest.raises(RuntimeError, match="opaque container"):
        with root.pass_scope():
            with root.container_call(_id(1), factory):
                pass
    assert events == []
    assert root._state_mgr.current.children_state == {}


def test_caught_native_helper_failure_preserves_the_original_abort_cause() -> None:
    root = _root()
    cause = ValueError("native helper failed")

    def failing(ctx: ContextBase) -> None:
        raise cause

    with pytest.raises(RenderAttemptAborted) as caught:
        with root.pass_scope():
            try:
                with root.container_call(_id(1), failing):
                    pass
            except ValueError as error:
                assert error is cause
    assert caught.value.__cause__ is cause
    assert root._state_mgr.current.children_state == {}


def test_surface_validation_is_closed_to_render_reentry() -> None:
    root = _root()
    events: list[str] = []

    class Key:
        def __eq__(self, other: object) -> bool:
            try:
                root.begin_pass()
            except RuntimeError as error:
                assert "completion is in progress" in str(error)
                events.append("blocked")
            else:
                events.append("entered")
                root.rollback_pass()
            return False

    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with root.container_call(_id(1), _native) as container:
                _select(container, "first")
                _select(container, Key(), 3)
    assert events == ["blocked"]
    assert root.debug_mount_advertisements() == ()
