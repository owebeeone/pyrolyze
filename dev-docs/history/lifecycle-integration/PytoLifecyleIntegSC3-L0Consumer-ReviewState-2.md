# SC3-L0 Private Consumer — State-AXIS REVIEW

**Review object:** SC3-L0 private completion-evidence consumer at Pyrolyze `b1461a1128da15c21dad482d41bd5792253904cd`; cumulative diff `dc9e4ccd21715bf8c639d07a2ec4d46af936b2c2..b1461a1128da15c21dad482d41bd5792253904cd`. Controlling document: `dev-docs/PytoLifecyleIntegSC3-L0Plan.md`, Consumer Contract and consumer checkpoint. Implementation checkpoint: `dev-docs/PytoLifecyleIntegSC3-L0Consumer.md`, candidate pending independent acceptance, 2026-10-08.
**Baseline:** Original reviewed consumer `223d04aa322df32e2adc5f5cd45b27111b111f4b`. Dependencies unchanged: yidl-lifecycle `05554397d1837ecbeafa36e4685477dd5ff30fc6`; YIDL `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`; Astichi `1c47f781d3804130fdd61cbee07a3b2e4529158a`. Inspection used committed Git views and unchanged tracked files; baseline execution loaded `git show` source into registered ephemeral modules.
**Date:** 2026-10-08.
**Axis:** State: completion authority, publication/generation ordering, error retention, quarantine, and recovery legality. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — both prior State P2 findings are verified closed; zero new P0, P1, P2, or P3 findings. Acceptance covered by this verdict is limited to the private consumer.

---

## Prior-finding closure table
| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| State P2-1 | Fence captured key/exact integer ID at admission and terminal observation; make observed rejection sticky | Independently replayed key/ID relabeling before scoped and no-op entry under both backends. Corrected code rejected before reset/body; restoring metadata and attempting another entry still rejected. Original source admitted compromised execution. Post-finalization `tx_id=True` also now rejects, preserves actually published UI, issues no generation decision, and blocks reuse. | Closed |
| State P2-2 | Reject unreachable phase/failure combinations before accepting authority; retain supplied errors independently | Independently replayed both original contradictory records under both backends: empty-publication/action-failure and successful-all-phases/error. Original source committed generation; corrected code retained the exact supplied exception, reported incomplete authority, kept publication classification unknown and generation pending, and rejected subsequent pass/publication writes and second completion. | Closed |

## Changed-range analysis
The correction from `223d04aa322df32e2adc5f5cd45b27111b111f4b` changes only the two existing private runtime files, narrow field-only tests, checkpoint evidence, and filed process records.

In `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:116–132,211–293`, identity checks now include captured metadata and sticky integrity loss; completion validation rejects the demonstrated contradictions; supplied completion exceptions remain reportable even when state authority is rejected. In `field_only_render.py:283–288`, primary-error selection uses explicit presence instead of exception truthiness. Tests add nine parameterized cases at `tests/test_runtime_context_state_lcm_field_only_render.py:710–889`.

These edits implement the merged dispositions at existing guard/observation sites. No changed shared interface, execution call graph, mutation boundary, library/compiler source, resource admission, selector, or golden was identified. Process documentation is within the authorized correction. **New architectural root causes: none.**

## 0. Evidence base
- Verified all four exact HEADs and repository statuses at start and end: unchanged. Dependencies remained clean; Pyrolyze retained only the two excluded untracked rendering documents, neither read. No files, builds, bytecode, caches, checkouts, or Git state were written. Correction and cumulative `git diff --check` passed.
- Continued the prior process/contract inspection: workspace/Pyrolyze `AGENTS.md`, supplied review-loop skill, documentation index, L0 observation/error/consumer contract, SingleCohortPlan ownership/failure/publication rules, SC3 boundary, and accepted library verification. Confirmed controlling documents and fixture directory were unchanged by remediation; reread the consumer contract at `dev-docs/PytoLifecyleIntegSC3-L0Plan.md:312–363`.
- Read the combined remediation plan and both permitted prior-round reports in `dev-docs/history/lifecycle-integration/`. No current-round peer report was accessed.
- Inspected the complete correction diff and revised runtime admission/completion ranges: `render_attempt.py:45–390` and `field_only_render.py:123–335`; read new tests `tests/test_runtime_context_state_lcm_field_only_render.py:710–889`. Retained runtime/test paths and earlier SC1/SC2 closure evidence remained in scope.
- Ran the permitted three-file pytest command with selectors unset, prescribed source exports, bytecode disabled, and cache provider disabled: **native 128 passed in 4.69s; Python backend 128 passed in 10.98s**. This is the permitted subset, not the owner’s seven-file 147-test gate.
- Independent baseline-versus-corrected probes used real private graphs with original `render_attempt.py` loaded from `git show 223d04aa:...`. Both backends reproduced the original metadata and terminal-record failures and passed corrected assertions. Reset/body instrumentation, tracker commit/rollback instrumentation, exact exception identity, restored-metadata reentry, quarantine, and exactly-once completion were checked.
- A baseline-only probe expectation initially assumed restored-ID entry always reached its body; generated stale-overlay checking rejected that particular second entry. The baseline expectation was corrected; all corrected-tree assertions remained unchanged.
- Additional native probes covered falsy and raising-boolean primary exceptions combined with scratch/cache/generation failures, release failure before/after removal, and late callback token relabeling. All completed assertions passed.
- Reproduced historical manager `371dfa530a975c27f7a6c09a7648f7f00532ab29` in a registered ephemeral module. Historical and current traces exactly matched their respective JSON. All three consumer goldens were byte-identical to the initial candidate; all seven original SC2 sections remained preserved.

## 2. Invariant analysis
**Authority rejection held.** Compromised metadata cannot enter local execution, and restoration cannot rehabilitate observed loss. Terminal boolean IDs and the original contradictory records cannot supply publication or rollback certificates. Rejected evidence preserves actual current values and exact supplied exception objects without adoption, guessed undo, second completion, or retry.

**Publication remains separate from readiness.** Both-backend canonical coverage retained empty commit/rollback/abort, validation/preparation abort, complete nonpublication discard, incomplete discard/after cleanup, partial application, and full publication followed by action failure. Published-after-failure generation commits once; partial or uncertified outcomes leave generation pending. Neither readiness nor `first_failure` determines publication.

**Late failures remain observable and fail closed.** Eight native combinations exercised falsy/raising-boolean primary errors with scratch, cache, and generation failure before/after mutation. Every outward group retained the exact primary first and cleanup error second, without evaluating exception truthiness. Published UI remained visible. Scratch/cache and post-mutation generation failures retained generation 1; pre-mutation generation failure left generation pending. No rollback or later write was admitted.

**Earlier closures survive.** Retained SC1 exceptional validation, borrowing/stale ownership, recursive finish/abort, and cleanup regressions passed on both backends. Independent release-fault probes preserved discard and quarantine. Retained SC2 lexical/reentry, retirement, candidate-sibling, constructor collision, current-reader, nested-cache, and duplicate/uninstalled-owner cases passed; their unchanged admission boundaries were retraced against prior closure evidence.

**History and isolation held.** Partial-apply values remained historical `[1,0,0]` versus current `[1,0,1]`; preparation-plus-discard failure retained both original errors. Explicit restaging was not treated as repaired cleanup. Independent-key cases remained covered. No resource activation follows from these results.

## 3. Risks and next action
This is a synchronous, in-memory checkpoint, not filesystem durability, process-restart recovery, or parallel-render certification. Full/default/broader suites were not repeated; the owner’s unchanged 13/14 failure identities remain supplied evidence, not independently verified broad acceptance. Resource adapters, global routing, and multi-key atomicity remain deferred.

**Next action:** Merge this State GO with the independently formed current-round Code verdict at the exact tuple before recording private-consumer acceptance. Resource admission and broader activation remain gated.
