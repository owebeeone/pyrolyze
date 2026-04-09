from __future__ import annotations

from typing import Any, Callable

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
    def evaluate_directive(
        self,
        directive_fn: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> tuple[Any, ...]:
        result = self.owner.evaluate(directive_fn, args, kwargs)
        selectors = tuple(result.value)
        for selector in selectors:
            if not isinstance(selector, self.owner._slot_selector_type):
                raise TypeError("mount directive evaluator must return SlotSelector values")
        return selectors

    def pending_selectors(self) -> tuple[Any, ...]:
        binding = self.owner.binding
        if binding is None:
            return self.owner.committed_selectors
        selectors = tuple(binding.exposed_value())
        for selector in selectors:
            if not isinstance(selector, self.owner._slot_selector_type):
                raise TypeError("mount directive evaluator must return SlotSelector values")
        return selectors

    def has_pending_emitted_children(self) -> bool:
        owner = self.owner
        if owner._staged_ui_entries:
            return True
        return any(bool(getattr(child, "_committed_ui", ())) for child in owner._children.values())
