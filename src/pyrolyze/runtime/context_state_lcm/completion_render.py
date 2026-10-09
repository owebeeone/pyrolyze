"""Private I6b gate: directives and captured outer-completion callbacks."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .callback_render import _graph_states
from .context_base import ContextBaseStateMgr
from .override_render import _OverrideRenderCompletion, _enable_override_render
from .render_attempt import _raise_with_cleanup
from .render_context import RenderContextStateMgr


@dataclass(eq=False, slots=True)
class _CompletionRenderCompletion(_OverrideRenderCompletion):
    directive_selection_enabled = True
    _callbacks: list[tuple[ContextBaseStateMgr, Callable[[], None]]] = field(
        default_factory=list, init=False
    )
    _publication_ready: bool = field(default=False, init=False)
    _invalidated_states: dict[int, Any] = field(default_factory=dict, init=False)

    def _start(self) -> None:
        super(_CompletionRenderCompletion, self)._start()
        self._publication_ready = False

    def note_invalidation(self, state: Any) -> None:
        if getattr(self, "pass_state_selection_enabled", False):
            return
        if self.active is not None and not self._publication_ready:
            self._invalidated_states[id(state)] = state

    def require_slot_type(self, slot_type: type[Any]) -> None:
        from pyrolyze.runtime.context_bare_refactor_lcm import DirectiveSlotContext

        if slot_type is not DirectiveSlotContext:
            super(_CompletionRenderCompletion, self).require_slot_type(slot_type)

    def enqueue_post_commit(
        self, source: ContextBaseStateMgr, callback: Callable[[], None]
    ) -> None:
        self.require_resource_owner()
        self._callbacks.append((source, callback))

    def _complete(self, propagating: BaseException | None) -> None:
        assert self.active is not None
        owner = self.active
        self._publication_ready = False
        callbacks = tuple(self._callbacks)
        failure: BaseException | None = None
        try:
            super(_CompletionRenderCompletion, self)._complete(propagating)
        except BaseException as error:
            failure = error
        errors: list[BaseException] = []
        self._completing = True
        try:
            if owner.published is False or self._publication_ready:
                self._callbacks.clear()
            if self._publication_ready:
                retained = {
                    id(state) for state in _graph_states(self.root, current=True)
                }
                # Resource retirement/setup has drained; callbacks observe the
                # accepted graph/generation, never local or failed candidates.
                for source, callback in callbacks:
                    if id(source) not in retained:
                        continue
                    try:
                        callback()
                    except BaseException as error:
                        errors.append(error)
                        self._cleanup_failure = error
        finally:
            self._completing = False
        # Unknown publication keeps the captured list as quarantined evidence.
        if errors:
            primary = failure if failure is not None else propagating
            if primary is not None:
                _raise_with_cleanup(primary, errors)
            if len(errors) == 1:
                raise errors[0]
            raise BaseExceptionGroup("post-commit delivery failed", errors)
        if failure is not None:
            raise failure

    def _after_field_publication(self, published: bool) -> None:
        retained = {id(state) for state in _graph_states(self.root, current=True)}
        pending, self._invalidated_states = self._invalidated_states, {}
        for identity, state in pending.items():
            if identity in retained:
                # Local end/abort restores pass dirtiness, not independently
                # arriving notifications. Preserve their next scheduled visit.
                state._invoke_dirty = True
        # This seam is reached only after generation and registry acceptance;
        # a later observer failure must not suppress independent callbacks.
        self._publication_ready = published
        super(_CompletionRenderCompletion, self)._after_field_publication(published)


def _enable_completion_render(root: RenderContextStateMgr) -> None:
    _enable_override_render(root)
    root._field_only_completion = _CompletionRenderCompletion(root)
