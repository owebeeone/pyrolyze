"""Default lifecycle-backed runtime with automatic root completion.

Fresh independent roots own completion; nested roots share that outer decision.
Explicit legacy selectors remain available during compatibility retirement.
This is not another transaction engine.
"""

from __future__ import annotations

from . import context_bare_refactor_lcm as _facades
from .app_context import AppContextLookup, AppContextStore
from .context_state_lcm.field_only_render import _require_fresh_render_root
from .context_state_lcm.pass_state_render import _PassStateRenderCompletion


for _name in _facades.__all__:
    globals()[_name] = getattr(_facades, _name)


class _AdoptionRenderCompletion(_PassStateRenderCompletion):
    # Existing plain scopes keep lexical host effects. Only their Pyrolyze
    # children join completion; private checkpoints retain stricter admission.
    __slots__ = ()
    opaque_containers_enabled = True


class RenderContext(_facades.RenderContext):
    def __init__(
        self,
        *,
        owner_slot: _facades.ComponentCallSlotContext | None = None,
        scheduler_root: _facades.RenderContext | None = None,
        app_context_store: AppContextStore | None = None,
        authored_app_context_lookup: AppContextLookup | None = None,
    ) -> None:
        super().__init__(
            owner_slot=owner_slot,
            scheduler_root=scheduler_root,
            app_context_store=app_context_store,
            authored_app_context_lookup=authored_app_context_lookup,
        )
        if owner_slot is None and scheduler_root is None:
            _require_fresh_render_root(self._state_mgr)
            self._state_mgr._field_only_completion = _AdoptionRenderCompletion(self._state_mgr)


__PYROLYZE_CONTEXT_IMPLEMENTATION__ = "lcm"
__all__ = list(_facades.__all__)
