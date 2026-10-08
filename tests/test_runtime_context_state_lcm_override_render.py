from __future__ import annotations

import pytest

from pyrolyze.runtime import context_bare_refactor_lcm as runtime
from pyrolyze.runtime.app_context import AppContextKey
from pyrolyze.runtime.context_state_lcm.override_render import _enable_override_render


def test_failed_override_does_not_notify_accepted_subscribers() -> None:
    root = runtime.RenderContext()
    _enable_override_render(root._state_mgr)
    key = AppContextKey("theme", lambda host: "unused")
    slot_id = runtime.SlotId(runtime.ModuleId("override-proof"), 1)
    with root.pass_scope():
        with root.open_app_context_override(slot_id, (key,), "old") as scope:
            ref = scope.authored_app_context_ref(key)
    events = []
    unsubscribe = ref.subscribe(lambda: events.append(ref.get()))
    try:
        with pytest.raises(ValueError, match="discard"):
            with root.pass_scope():
                with root.open_app_context_override(slot_id, (key,), "new") as scope:
                    assert scope.get_authored_app_context(key) == "new"
                    assert scope.authored_app_context_ref(key).get() == "new"
                    assert scope.committed_values == ("old",)
                raise ValueError("discard")
        assert events == []
        assert ref.get() == "old"
    finally:
        unsubscribe()


def test_independent_parent_event_survives_failed_candidate() -> None:
    from pyrolyze.runtime.app_context import (
        EMPTY_APP_CONTEXT_LOOKUP,
        OverlayAppContextLookup,
    )
    from pyrolyze.runtime.drip import Drip

    key = AppContextKey("theme", lambda host: "unused")
    parent = Drip(initial="old")
    root = runtime.RenderContext(
        authored_app_context_lookup=OverlayAppContextLookup(
            EMPTY_APP_CONTEXT_LOOKUP, {key: parent}
        )
    )
    _enable_override_render(root._state_mgr)
    slot_id = runtime.SlotId(runtime.ModuleId("override-proof"), 1)
    with root.pass_scope():
        with root.open_app_context_override(slot_id, (key,), None) as scope:
            ref = scope.authored_app_context_ref(key)
    events = []
    unsubscribe = ref.subscribe(lambda: events.append(ref.get()))
    try:
        with pytest.raises(ValueError, match="discard"):
            with root.pass_scope():
                with root.open_app_context_override(slot_id, (key,), "candidate"):
                    parent.next("independent")
                raise ValueError("discard")
        assert events == ["independent"]
        assert ref.get() == "independent"
        assert scope.committed_values == (None,)
    finally:
        unsubscribe()


def test_caught_structure_failure_aborts_outer_attempt() -> None:
    from pyrolyze.runtime.context_state_lcm.render_attempt import RenderAttemptAborted

    root = runtime.RenderContext()
    _enable_override_render(root._state_mgr)
    key = AppContextKey("theme", lambda host: "unused")
    slot_id = runtime.SlotId(runtime.ModuleId("override-proof"), 1)
    with pytest.raises(RenderAttemptAborted):
        with root.pass_scope():
            with pytest.raises(RuntimeError, match="arity"):
                with root.open_app_context_override(slot_id, (key,)):
                    pass
    assert root._state_mgr.current.children_state == {}


def test_observer_failure_preserves_publication_and_drains_other_keys() -> None:
    root = runtime.RenderContext()
    _enable_override_render(root._state_mgr)
    keys = tuple(AppContextKey(name, lambda host: "unused") for name in ("a", "b"))
    slot_id = runtime.SlotId(runtime.ModuleId("override-proof"), 1)
    with root.pass_scope():
        with root.open_app_context_override(slot_id, keys, 1, 1) as scope:
            refs = tuple(scope.authored_app_context_ref(key) for key in keys)
    error = ValueError("observer")
    events = []

    def fail() -> None:
        raise error

    refs[0].identity._error_policy = "raise"
    unsubs = (
        refs[0].subscribe(fail),
        refs[1].subscribe(lambda: events.append(refs[1].get())),
    )
    try:
        with pytest.raises(ValueError) as caught:
            with root.pass_scope():
                with root.open_app_context_override(slot_id, keys, 2, 2):
                    pass
        assert caught.value is error
        assert events == [2]
        assert scope.committed_values == (2, 2)
        completion = root._state_mgr._field_only_completion
        assert completion.last.published is True
        with pytest.raises(RuntimeError, match="not ready"):
            with root.pass_scope():
                pass
    finally:
        for unsubscribe in unsubs:
            unsubscribe()


def test_observer_reentry_cannot_start_another_render() -> None:
    root = runtime.RenderContext()
    _enable_override_render(root._state_mgr)
    key = AppContextKey("theme", lambda host: "unused")
    slot_id = runtime.SlotId(runtime.ModuleId("override-proof"), 1)
    with root.pass_scope():
        with root.open_app_context_override(slot_id, (key,), "old") as scope:
            ref = scope.authored_app_context_ref(key)
    errors = []

    def changed() -> None:
        try:
            with root.pass_scope():
                pass
        except RuntimeError as error:
            errors.append(error)

    unsubscribe = ref.subscribe(changed)
    try:
        with root.pass_scope():
            with root.open_app_context_override(slot_id, (key,), "new"):
                pass
        assert len(errors) == 1
        assert ref.get() == "new"
    finally:
        unsubscribe()


def test_parent_stream_does_not_retain_discarded_render_graph() -> None:
    import gc
    import weakref
    from pyrolyze.runtime.app_context import (
        EMPTY_APP_CONTEXT_LOOKUP,
        OverlayAppContextLookup,
    )
    from pyrolyze.runtime.drip import Drip

    key = AppContextKey("theme", lambda host: "unused")
    parent = Drip(initial="old")

    def render() -> object:
        root = runtime.RenderContext(
            authored_app_context_lookup=OverlayAppContextLookup(
                EMPTY_APP_CONTEXT_LOOKUP, {key: parent}
            )
        )
        _enable_override_render(root._state_mgr)
        with root.pass_scope():
            with root.open_app_context_override(
                runtime.SlotId(runtime.ModuleId("override-proof"), 1), (key,), None
            ):
                pass
        assert parent.has_subscribers()
        return weakref.ref(root)

    root_ref = render()
    gc.collect()
    assert root_ref() is None
    assert not parent.has_subscribers()


def test_concrete_transition_detaches_parent_before_parent_publication() -> None:
    root = runtime.RenderContext()
    _enable_override_render(root._state_mgr)
    key = AppContextKey("theme", lambda host: "unused")
    module = runtime.ModuleId("override-proof")
    outer_id, inner_id = runtime.SlotId(module, 1), runtime.SlotId(module, 2)
    with root.pass_scope():
        with root.open_app_context_override(outer_id, (key,), "old") as outer:
            with outer.open_app_context_override(inner_id, (key,), None) as inner:
                ref = inner.authored_app_context_ref(key)
    events = []
    unsubscribe = ref.subscribe(lambda: events.append(ref.get()))
    try:
        with root.pass_scope():
            with root.open_app_context_override(outer_id, (key,), "new") as outer:
                with outer.open_app_context_override(inner_id, (key,), "concrete"):
                    pass
        assert events == ["concrete"]
    finally:
        unsubscribe()
