# Override Read Acknowledgment: Safety Draft Review

- Date: 2026-10-09
- Object: `dev-docs/PytoLifecyleIntegOverrideReadAcknowledgment.md`
- SHA256: `85d8701988611f299972c76f3ae1cf2e40df425670070b6dda05dd80ff7cd8aa`
- Baseline HEAD: `7974efd4c3a73eee3cd23abd3d7a8fff527bd0f2`
- Verification: object hash and HEAD matched at both start and end.
- Scope: lightweight single-reviewer Safety review, including internal consistency. Read-only; no edits, git mutations, builds, tests, or agents. Other uncommitted documents were excluded.

## Decision

**GO**: suitable for bounded implementation, not runtime acceptance or default activation.

The proposed suppression invariant survived the examined counterexamples when its explicit conservative fallback rules are applied. No P0–P3 findings were identified. This review uses the user-authorized hash-frozen uncommitted draft exception; it is not formal review-loop acceptance.

## Evidence

Source paths below are relative to the repository root.

- `src/pyrolyze/runtime/context_state_lcm/override_lookup.py:30`: `_OverrideDrip.get()` exposes lexical values only outside notification. `next()` temporarily forces accepted-stream reads and restores the prior flag.
- `src/pyrolyze/runtime/context_state_lcm/context_base.py:144`: authored refs use the stable drip as identity, subscribe through synchronous priority callbacks, ignore initial subscription delivery, and subsequently call a zero-argument listener.
- `src/pyrolyze/runtime/context_state_lcm/subscription_binding.py:50`: notifications currently increment resource revision before marking the weak host refresh-only. Binding reuse retains that resource and callback; reads create detached value/revision selections at lines 116–119 and 135–140.
- `src/pyrolyze/runtime/context_state_lcm/subscription_expr_render.py:38`: expression notification hosts resolve call sites through weak state links. Current invalidation visits both current and visible contexts; acknowledgment must use only the published selection, as the draft requires.
- `src/pyrolyze/runtime/context_state_lcm/field_only_render.py:281`: field completion precedes domain delivery; unknown publication does not enter the delivery hook.
- `src/pyrolyze/runtime/context_state_lcm/override_render.py:56`: delivery reads accepted override selections and detaches stale parent links across the batch before synchronization.
- `src/pyrolyze/runtime/context_state_lcm/app_context_override_slot_context.py:62`: concrete synchronization and transparent parent forwarding both reach `drip.next()`. Parent callbacks are synchronous and weak for managed override streams.
- `src/pyrolyze/runtime/drip.py:97`: priority subscribers execute synchronously after value update; nested callbacks can emit additional events. Callback errors follow Drip’s configured policy.

The controlling `dev-docs/PytoLifecyleIntegAdoptionAudit.md` treats publication acknowledgment as a separate candidate-route defect and preserves independent scheduler work, quarantine, and default-activation gates. The draft is consistent with those limits.

## Findings

None at P0, P1, P2, or P3.

No bounded corrective draft edit is required. A second review axis is not warranted by a discovered P2 issue.

## Invariant Analysis

| Refutation attempt | Analysis |
| --- | --- |
| Candidate read, independent event, then rollback | The receipt remains provisional and is discarded. Accepted receipt and independent revision/queued work remain unchanged under draft lines 31–44. |
| Delivery before reader publication | The existing domain hook follows field publication. Resolving the currently published binding, rather than a visible candidate, matches that ordering. Unknown outcomes cannot acknowledge. |
| Subscription reused after a new read | The callback remains old, but the selected binding owns the receipt. Matching resource identity and resolving the current selection avoids stale closure acknowledgment. |
| Independent event during rendering | Transaction activity or equal values cannot identify publication. Such events follow ordinary revision/invalidation handling, including events after the candidate read. |
| Independent event nested inside publication delivery | A surrounding delivery marker alone would be unsafe. Draft lines 65–68 explicitly require plain events to be unmarked, with nested marker restoration. Implementation must honor this event-specific distinction. |
| Transparent child reads parent A; parent changes to B before synchronization | Local selection identity alone cannot certify consumption of B. Effective-source provenance and ambiguity fallback at lines 84–87 prohibit that suppression; the independent parent event remains observable. |
| Parent publication forwards through an existing transparent link | Forwarded delivery is suppressible only with exact effective-source publication evidence. Missing evidence must notify; detach-before-delivery remains unchanged. |
| Clean reader, replacement, removal, or collection | Previous receipts cannot acknowledge a new selection; resource matching prevents stale-resource suppression. Weak links and normal fallback avoid resurrecting scheduling targets. |

The safety distinction is between **publication consumed by this published read selection** and **an event occurring while publication is being delivered**. The draft maintains that distinction without relying on value equality, clearing queues, or changing ownership.

## Next Action

Proceed with the bounded implementation and specified notification matrix on both backends. Explicitly exercise same-stream reentrant independent events and transparent-parent changes between read and delivery for both reader forms.

Record actual implementation evidence in the adoption audit afterward. This source-only review neither independently reproduces the reported failing trace nor certifies runtime behavior.
