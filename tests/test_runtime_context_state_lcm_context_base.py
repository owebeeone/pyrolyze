from __future__ import annotations

from pyrolyze.runtime.context_state_lcm.context_base import ContextBaseStateMgr


class _DummyPassScope:
    def __init__(self, *, context: object, activate: bool) -> None:
        self.context = context
        self.activate = activate


class _DummyOwner:
    _generation_tracker_key_const = object()
    _pass_scope_handle_cls = _DummyPassScope


class _RenderContextWithStateMgr:
    def __init__(self, state_mgr: object) -> None:
        self._state_mgr = state_mgr


class _DerivedContextBaseStateMgr(ContextBaseStateMgr):
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner=owner, **kwargs)


def test_context_base_resolves_render_context_state_mgr_from_explicit_initvar() -> None:
    explicit_state_mgr = object()
    from_render_context = object()

    mgr = ContextBaseStateMgr(
        owner=_DummyOwner(),
        render_context_state_mgr=explicit_state_mgr,
        render_context=_RenderContextWithStateMgr(from_render_context),
    )

    assert mgr._render_context_state_mgr is explicit_state_mgr
    assert "render_context_state_mgr" not in mgr.__state_cls__.__field_specs__
    assert "render_context" not in mgr.__state_cls__.__field_specs__
    assert "_resolved_render_context_state_mgr" not in mgr.__state_cls__.__field_specs__


def test_context_base_resolves_render_context_state_mgr_from_render_context_initvar() -> None:
    from_render_context = object()

    mgr = ContextBaseStateMgr(
        owner=_DummyOwner(),
        render_context=_RenderContextWithStateMgr(from_render_context),
    )

    assert mgr._render_context_state_mgr is from_render_context


def test_context_base_subclass_can_forward_owner_keyword_to_managed_constructor() -> None:
    explicit_state_mgr = object()

    mgr = _DerivedContextBaseStateMgr(
        owner=_DummyOwner(),
        render_context_state_mgr=explicit_state_mgr,
    )

    assert mgr._render_context_state_mgr is explicit_state_mgr
