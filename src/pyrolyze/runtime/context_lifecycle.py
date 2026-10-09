"""Lifecycle adoption candidate with automatic root completion.

Select with PYROLYZE_CONTEXT_IMPL=lifecycle while normal-route admission and
consumer migration are verified. This is not another transaction engine.
"""

from __future__ import annotations

from . import context_bare_refactor_lcm as _facades
from .app_context import AppContextLookup, AppContextStore
from .context_state_lcm.pass_state_render import _enable_pass_state_render


for _name in _facades.__all__:
    globals()[_name] = getattr(_facades, _name)


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
            _enable_pass_state_render(self._state_mgr)


__PYROLYZE_CONTEXT_IMPLEMENTATION__ = "lcm"
__all__ = list(_facades.__all__)
