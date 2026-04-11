from __future__ import annotations

from typing import Any, Callable

from pyrolyze.api import MountDirective, SlotSelector
from ._base import USE_FACTORY, USE_OWNER

from .slot_call_slot_context import SlotCallSlotContextStateMgr


class DirectiveSlotContextStateMgr(SlotCallSlotContextStateMgr):
    # TODO: Mount/directive state is still architecturally too implicit.
    # Today selectors come from slot-call binding state, emitted children come
    # from generic ContextBase staged/committed UI state, and the final
    # MountDirective is reconstructed later by _build_committed_ui(). That
    # makes mount fragile because one logical structural transaction is spread
    # across several different state machines with different commit ordering.
    #
    # When we revisit this during the lifecycle refactor, treat mount as a
    # first-class structural state model owned here:
    # - staged vs committed selectors
    # - staged vs committed own children
    # - staged vs committed nested children
    # - pre-commit validation such as no_emit + emitted children
    # - MountDirective as a derived projection of that committed state
    #
    # That should let mount validate and commit as one coherent unit instead
    # of depending on inherited ContextBase mechanics plus slot-call binding
    # behavior lining up by accident.
    def __init__(self, owner: object, **kwargs: object) -> None:
        super().__init__(owner, **kwargs)
        self._committed_selectors: tuple[Any, ...] = ()
        self._pass_committed_selectors: tuple[Any, ...] = ()

    def evaluate_directive(
        self,
        directive_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        host: Any = USE_OWNER,
        runtime_context_factory: Callable[[], Any] | object = USE_FACTORY,
    ) -> tuple[Any, ...]:
        result = self.evaluate(
            directive_fn,
            args,
            kwargs,
            host=host,
            runtime_context_factory=runtime_context_factory,
        )
        selectors = tuple(result.value)
        for selector in selectors:
            if not isinstance(selector, SlotSelector):
                raise TypeError("mount directive evaluator must return SlotSelector values")
        return selectors

    def pending_selectors(self) -> tuple[Any, ...]:
        binding = self._binding
        if binding is None:
            return self._committed_selectors
        selectors = tuple(binding.exposed_value())
        for selector in selectors:
            if not isinstance(selector, SlotSelector):
                raise TypeError("mount directive evaluator must return SlotSelector values")
        return selectors

    def has_pending_emitted_children(self) -> bool:
        if self._staged_ui_entries:
            return True
        return any(bool(child_state_mgr.committed_ui()) for child_state_mgr in self._children.values())

    def begin_scope_pass(self) -> None:
        self._pass_committed_selectors = self._committed_selectors
        super().begin_pass()

    def commit_scope_pass(self) -> None:
        self._committed_selectors = self.pending_selectors()
        super().end_pass()
        self._pass_committed_selectors = ()

    def rollback_scope_pass(self) -> None:
        super().rollback_pass()
        self._committed_selectors = self._pass_committed_selectors
        self._pass_committed_selectors = ()

    def build_committed_ui(self) -> tuple[Any, ...]:
        own_children = tuple(
            entry.element
            for entry in self._staged_ui_entries + []
        )
        nested_children = tuple(
            element
            for child in self._children.values()
            for element in child.committed_ui()
        )
        return (
            MountDirective(
                selectors=self._committed_selectors,
                children=own_children + nested_children,
                slot_id=self.current_slot_id(),
            ),
        )
