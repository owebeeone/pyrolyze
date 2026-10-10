from __future__ import annotations

import gc
from typing import Any
import weakref

import pytest

from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.app_context import (
    AppContextKey, EMPTY_APP_CONTEXT_LOOKUP, OverlayAppContextLookup,
)
from pyrolyze.runtime.drip import Drip
from tests.data.lcm_integration.override_read_acknowledgment import read


def _setup() -> tuple[Any, Any, Any, Any]:
    root = runtime.RenderContext()
    key = AppContextKey("theme", lambda host: "unused")
    module = runtime.ModuleId("override-read-faults")
    return root, key, runtime.SlotId(module, 1), runtime.SlotId(module, 2)


def _accepted(root: Any, slot_id: Any, expression: bool) -> Any:
    slot = root._slots_by_id[slot_id]
    if expression:
        return slot.call_site_context_manager.get_current(slot_id).binding.binding
    return slot.binding


@pytest.mark.parametrize("expression", (False, True))
@pytest.mark.parametrize("event_before_read", (False, True))
def test_independent_event_survives_candidate_rollback(
    expression: bool, event_before_read: bool,
) -> None:
    root, key, override_id, reader_id = _setup()
    with root.pass_scope():
        with root.open_app_context_override(override_id, (key,), "old") as scope:
            accepted = read(scope, reader_id, key, expression)
            source = scope.authored_app_context_ref(key).identity
    receipt = accepted.read_receipt
    with pytest.raises(ValueError, match="discard"):
        with root.pass_scope():
            with root.open_app_context_override(override_id, (key,), "candidate") as scope:
                if event_before_read:
                    source.next("independent")
                candidate = read(scope, reader_id, key, expression)
                if not event_before_read:
                    source.next("independent")
                assert candidate.value == "candidate"
            raise ValueError("discard")
    assert _accepted(root, reader_id, expression) is accepted
    assert accepted.read_receipt is receipt
    assert accepted.resource.revision == 1
    source.next("later")
    assert accepted.resource.revision == 2


@pytest.mark.parametrize("expression", (False, True))
def test_reentrant_independent_event_does_not_inherit_publication(
    expression: bool,
) -> None:
    root, key, override_id, reader_id = _setup()
    with root.pass_scope():
        with root.open_app_context_override(override_id, (key,), "old") as scope:
            source = scope.authored_app_context_ref(key).identity

            def reenter(value: object) -> None:
                if value == "new":
                    source.next("independent")

            unsubscribe = source.subscribe_priority(reenter)
            read(scope, reader_id, key, expression)
    try:
        with root.pass_scope():
            with root.open_app_context_override(override_id, (key,), "new") as scope:
                selected = read(scope, reader_id, key, expression)
        assert selected.resource.revision == 1
        assert source.get() == "independent"
        assert source._publication is None
        source.next("later")
        assert selected.resource.revision == 2
    finally:
        unsubscribe()


@pytest.mark.parametrize("expression", (False, True))
def test_plain_parent_change_after_read_still_notifies(expression: bool) -> None:
    root, key, override_id, reader_id = _setup()
    parent = Drip(initial="old")
    root = runtime.RenderContext(
        authored_app_context_lookup=OverlayAppContextLookup(
            EMPTY_APP_CONTEXT_LOOKUP, {key: parent}
        )
    )
    with root.pass_scope():
        with root.open_app_context_override(override_id, (key,), None) as scope:
            selected = read(scope, reader_id, key, expression)
            parent.next("independent")
    assert selected.value == "old"
    assert selected.resource.revision == 1
    assert scope.authored_app_context_ref(key).get() == "independent"


@pytest.mark.parametrize("expression", (False, True))
def test_retained_receipt_does_not_retain_graph(expression: bool) -> None:
    def render() -> tuple[Any, Any]:
        root, key, override_id, reader_id = _setup()
        with root.pass_scope():
            with root.open_app_context_override(override_id, (key,), "old") as scope:
                selected = read(scope, reader_id, key, expression)
        return weakref.ref(root), selected

    root_ref, selected = render()
    gc.collect()
    assert root_ref() is None
    assert selected.resource.is_closed


def test_failed_publication_cannot_supply_provenance() -> None:
    class BadComparison:
        def __eq__(self, other: object) -> bool:
            raise ValueError("comparison")

    root, key, override_id, _ = _setup()
    with root.pass_scope():
        with root.open_app_context_override(override_id, (key,), "old") as scope:
            source = scope.authored_app_context_ref(key).identity
    with pytest.raises(ValueError, match="comparison"):
        source.publish(BadComparison(), (object(),))
    assert source.get() == "old"
    assert source._publication is None
    assert source._published_provenance is None


@pytest.mark.parametrize("expression", (False, True))
def test_failed_projection_keeps_accepted_receipt(expression: bool) -> None:
    class BadComparison:
        def __eq__(self, other: object) -> bool:
            raise ValueError("projection")

    root, key, override_id, reader_id = _setup()
    with root.pass_scope():
        with root.open_app_context_override(override_id, (key,), "old") as scope:
            accepted = read(scope, reader_id, key, expression)
            source = scope.authored_app_context_ref(key).identity
    with pytest.raises(ValueError, match="projection"):
        with root.pass_scope():
            with root.open_app_context_override(override_id, (key,), BadComparison()) as scope:
                read(scope, reader_id, key, expression)
    assert _accepted(root, reader_id, expression) is accepted
    source.next("later")
    assert accepted.resource.revision == 1
