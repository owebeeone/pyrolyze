from __future__ import annotations

from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, Callable

from pyrolyze.api import MountDirective, SlotSelector
from ._base import USE_FACTORY, USE_OWNER
from .context_base import PASS_TX_KEY, ContextBaseStateMgr
from .field_only_render import _field_only_completion
from .lifecycle_adapter import local_store, managed, managed_context
from .slot_call_slot_context import SlotCallSlotContextStateMgr

if TYPE_CHECKING:
    from .completion_render import _CompletionRenderCompletion


@managed_context
class DirectiveSlotContextStateMgr(SlotCallSlotContextStateMgr):
    _selectors: tuple[SlotSelector, ...] = managed(default=(), tx_key=PASS_TX_KEY)
    _legacy_selectors: tuple[SlotSelector, ...] = local_store(default=())
    _pass_committed_selectors: tuple[SlotSelector, ...] = local_store(default=())

    def _directive_completion(self) -> _CompletionRenderCompletion | None:
        completion = _field_only_completion(self)
        return (
            completion
            if getattr(completion, "directive_selection_enabled", False)
            else None
        )

    @property
    def _committed_selectors(self) -> tuple[SlotSelector, ...]:
        if self._directive_completion() is not None:
            return self.current._selectors
        return self._legacy_selectors

    def evaluate_directive(
        self,
        directive_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        host: Any = USE_OWNER,
        runtime_context_factory: Callable[[], Any] | object = USE_FACTORY,
    ) -> tuple[SlotSelector, ...]:
        completion = self._directive_completion()
        execution = nullcontext() if completion is None else completion.attempt_scope()
        with execution:
            owner = None if completion is None else completion.active
            result = self.evaluate(
                directive_fn,
                args,
                kwargs,
                host=host,
                runtime_context_factory=runtime_context_factory,
            )
            selectors = self._validate_selectors(result.value)
            if owner is not None:
                owner._require_open()
                owner._require_identity()
                self._selectors = selectors
            return selectors

    @staticmethod
    def _validate_selectors(value: Any) -> tuple[SlotSelector, ...]:
        selectors = tuple(value)
        for selector in selectors:
            if not isinstance(selector, SlotSelector):
                raise TypeError(
                    "mount directive evaluator must return SlotSelector values"
                )
        return selectors

    def pending_selectors(self) -> tuple[SlotSelector, ...]:
        if self._directive_completion() is not None:
            return self._selectors
        binding = self._binding
        if binding is None:
            return self._committed_selectors
        return self._validate_selectors(binding.exposed_value())

    def _nested_children(self) -> tuple[Any, ...]:
        candidate = self._directive_completion() is not None
        return tuple(
            element
            for child in self.children_state.values()
            for element in (
                child.ui_state
                if candidate and isinstance(child, ContextBaseStateMgr)
                else child.committed_ui()
            )
        )

    def has_pending_emitted_children(self) -> bool:
        return bool(self.own_ui_entries_state or self._nested_children())

    def begin_scope_pass(self) -> None:
        # Only unactivated compatibility routes retain selector snapshots.
        if self._directive_completion() is None:
            self._pass_committed_selectors = self._legacy_selectors
        super().begin_pass()

    def _complete_legacy_selection(self, *, committed: bool) -> None:
        # Directives project selectors at their own local exit; the previous
        # parent dispatcher excluded them despite slot-call inheritance.
        return None

    def commit_scope_pass(self) -> None:
        if self._directive_completion() is None:
            self._legacy_selectors = self.pending_selectors()
        super().end_pass()
        self._pass_committed_selectors = ()

    def rollback_scope_pass(self) -> None:
        super().rollback_pass()
        if self._directive_completion() is None:
            self._legacy_selectors = self._pass_committed_selectors
        self._pass_committed_selectors = ()

    def build_committed_ui(self) -> tuple[MountDirective, ...]:
        own_children = tuple(entry.element for entry in self.own_ui_entries_state)
        nested_children = self._nested_children()
        return (
            MountDirective(
                selectors=(
                    self._selectors
                    if self._directive_completion() is not None
                    else self._legacy_selectors
                ),
                children=own_children + nested_children,
                slot_id=self.current_slot_id(),
            ),
        )
