# SC3-L0 Private Consumer — Code-AXIS REVIEW

**Review object:** SC3-L0 private completion-evidence consumer at Pyrolyze `223d04aa322df32e2adc5f5cd45b27111b111f4b`, diff `dc9e4ccd21715bf8c639d07a2ec4d46af936b2c2..223d04aa322df32e2adc5f5cd45b27111b111f4b`. Controlling contract: `dev-docs/PytoLifecyleIntegSC3-L0Plan.md`; checkpoint: `dev-docs/PytoLifecyleIntegSC3-L0Consumer.md`, implementation candidate dated 2026-10-08, acceptance pending.

**Baseline:** Pyrolyze base `dc9e4ccd21715bf8c639d07a2ec4d46af936b2c2`; reviewed HEAD above. Dependencies: yidl-lifecycle `05554397d1837ecbeafa36e4685477dd5ff30fc6`; YIDL `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`; Astichi `1c47f781d3804130fdd61cbee07a3b2e4529158a`. Sources were inspected in clean tracked working trees; historical sources were read with `git show`. File references below are relative to their named owning repository.

**Date:** 2026-10-08

**Axis:** Code: interfaces, ownership, call graphs, compatibility, completion predicates, and exception propagation. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks; no P0, P1, or P3 findings. I pre-commit to GO on a revision that resolves P2-1 as specified and preserves the passing bounded gates.

---

## 0. Evidence base

- Verified all four exact HEADs and repository statuses at start and end: unchanged. Dependencies stayed clean; Pyrolyze retained only the two excluded untracked rendering-backend documents. Neither was read. No files, builds, caches, bytecode, or Git state were written.
- Read process instructions and the supplied review-loop skill; Pyrolyze `dev-docs/README.md`; the L0 plan, particularly Token-Bound Completion Observation, Error Contract, Consumer Contract, and consumer checkpoint; the consumer verification document; SingleCohortPlan ownership/failure/publication sections; SC3’s resource boundary and consumer gate; yidl-lifecycle `dev-docs/L0CompletionVerification.md` acceptance/scope.
- Inspected Pyrolyze `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:1-464` and `field_only_render.py:1-335`, including their complete reviewed diff. Traced callers through `context_base.py:178-438`, `render_context.py:24-255`, `_base.py:79-109`, `leaf_slot_context.py:23-50`, component replacement/retirement guards, and `src/pyrolyze/runtime/app_context.py:106-132`.
- Read yidl-lifecycle `src/yidl_lifecycle/transaction_yidl.py:69-151,254-706,786-953` to trace original-token observation, canonical key identity, manager finalization, callback outcomes, and outward failures. Accepted library outcomes were not reopened.
- Read retained SC1/SC2 Code closure records and ledgers, the corresponding owner/field-only regression cases, and changed fixture/harness ranges. Executed the authorized three-file pytest command with both selectors unset, bytecode/cache writes disabled, and the prescribed source exports: **native 119 passed in 4.53s; Python backend 119 passed in 10.78s**.
- Independently verified `transaction_failures.json` is byte-identical to the Pyrolyze base; executed the README’s pinned historical-manager reproduction and obtained an exact JSON match. Structured comparison confirmed all seven previous SC2 JSON sections unchanged. The separately named current-library target passed on both backends.
- In-memory probes exercised equal-but-nonidentical configured/requested keys and combined manager/local-cleanup failures. A registered ephemeral module loaded baseline field-only source through `git show` for the finding’s baseline control. `git diff --check` passed.

## 1. Findings

### [P2-1] Exception truthiness drops the original completion failure

**Location:** Pyrolyze `src/pyrolyze/runtime/context_state_lcm/field_only_render.py:283-288`, specifically `primary = failure or propagating` at line 285. The new evidence-driven cleanup at lines 269-282 makes this path reachable after published completion-action failures.

**Violated invariant:** The Consumer Contract requires published-action failures to remain reported independently of generation/cache completion. The Error Contract requires original exception preservation and ordered aggregation of independent cleanup failures.

**Reproduction:** Use a fresh privately enabled exact root. Inside `root.pass_scope()`, enlist a protocol participant on `PASS_TX_KEY` whose preparation/application return normally and whose after-commit callback raises `primary`, a `ValueError` subclass with `__bool__` returning `False`. Inject `_clear_field_only_pass` raising a separate `LookupError`, using the same local-cleanup fault mechanism as the retained tests. Let the render body return normally.

The accepted manager retains `primary`, certifies full publication, finalizes, and raises that exact exception. The owner preserves it. Generation commits once. Local cleanup then raises, but line 285 converts the present, falsy `failure` into `None`. The outward result is **the cleanup `LookupError` alone**, with **no cause or context** containing `primary`, not an ordered exception group. The original survives only in private retained evidence.

**Controls:** An ordinary truthy `ValueError` produces the expected two-error group. A primary whose `__bool__` raises instead produces that unrelated truth-evaluation error. Loading baseline field-only completion in memory preserves the falsy primary because the old readiness gate skips this newly reachable cleanup path.

**Impact:** Combined completion/local-cleanup failure loses the original failure from the outward diagnostic contract. Publication and quarantine remain correct; this is exception-propagation failure, not fabricated rollback.

**Required correction:** Select by presence, without invoking exception truthiness: `failure if failure is not None else propagating`. Preserve the existing ordered grouping, committed generation, and graph quarantine.

**Closure test:** Add narrow combined-failure cases for falsy and raising-`__bool__` primary exceptions. Assert the outward group contains the exact primary first and exact cleanup exception second, never evaluates primary truthiness, commits generation once, clears active bookkeeping, and rejects graph reuse. Re-run the authorized three-file native/Python gates.

## 2. Invariant analysis

- **Original token and key semantics held:** The owner captures the token’s original key/ID before callbacks. Equal nonidentical caller keys successfully resolve an existing canonical manager key; completion identity checks do not incorrectly compare against the caller’s distinct key object.
- **Evidence table held:** Both-backend canonical checks covered empty commit/rollback/abort, validation/preparation abort, incomplete discard/actions, partial application, and published after-action failure. Publication no longer follows `first_failure` or reuse readiness.
- **Authority rejection held:** Missing/malformed evidence, wrong key/ID, nonfinalized or ownership-lost records, and replacement-after-finalization cases quarantine without adopting or rolling back replacement authority.
- **Exactly-once completion held:** Retained tests reject repeated finish and recursive completion, preserve sticky caught failure, isolate other keys, and avoid a guessed second rollback following commit failure.
- **SC1 closures held:** Scope reentry, exceptional validation ownership loss, external borrowing/stale exits, and recursive local finish/abort counterexamples passed under the accepted manager on both backends.
- **SC2 closures held:** Constructor/root ownership, direct/transitive/candidate retirement, lexical early-end protection, no-op replacement admission, discarded nested caches, membership/current-reader separation, and scheduler preservation passed. Source retracing confirmed guards precede deferred resource effects.
- **Boundary/history held:** Runtime edits remain in the two named private files. No resource adapters, manual participant engine, snapshot replacement, selector change, or production activation appeared. Both adoption mismatches transition explicitly; historical observations and prior SC2 sections remain preserved.

## 3. Risks and next action

Full/default/broader suites were not independently rerun; their recorded 13/14 failures remain unwaived owner evidence, not this review’s execution results. Resource adapters, asynchronous rendering, arbitrary payload-alias mutation, and multi-key atomicity remain outside this bounded verdict. The combined-failure counterexample was independently reproduced with the native backend; its corrective regression should cover both backends.

**Next action:** Correct P2-1 and add its narrow regression, then obtain a focused re-verdict on the settled revision. No resource implementation or unrelated baseline-debt work is required.
