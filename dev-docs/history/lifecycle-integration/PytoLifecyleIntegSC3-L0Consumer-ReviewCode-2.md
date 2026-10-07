# SC3-L0 Private Consumer — Code-AXIS REVIEW

**Review object:** SC3-L0 private completion-evidence consumer at Pyrolyze `b1461a1128da15c21dad482d41bd5792253904cd`, cumulative diff `dc9e4ccd21715bf8c639d07a2ec4d46af936b2c2..b1461a1128da15c21dad482d41bd5792253904cd`. Controlling contract: `dev-docs/PytoLifecyleIntegSC3-L0Plan.md`; checkpoint: `dev-docs/PytoLifecyleIntegSC3-L0Consumer.md`, implementation candidate dated 2026-10-08, remediation 1/2, acceptance pending.

**Baseline:** Prior reviewed Pyrolyze candidate `223d04aa322df32e2adc5f5cd45b27111b111f4b`; implementation base `dc9e4ccd21715bf8c639d07a2ec4d46af936b2c2`. Dependencies: yidl-lifecycle `05554397d1837ecbeafa36e4685477dd5ff30fc6`; YIDL `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`; Astichi `1c47f781d3804130fdd61cbee07a3b2e4529158a`. Inspection used unchanged tracked files, Git diffs, and `git show` for historical sources. References below are owning-repository-relative.

**Date:** 2026-10-08

**Axis:** Code: interfaces, ownership, call graphs, compatibility, completion predicates, and exception propagation. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — Code P2-1 verified closed; zero new or open Code findings at P0/P1/P2/P3. This accepts only the bounded private consumer.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| Code P2-1 | Select the primary exception by explicit `None` presence; preserve ordered failures, generation, and quarantine | Independently replayed both original after-action/local-cleanup counterexamples on native and Python backends. Prior-SHA completion loaded into a registered ephemeral module reproduced the masking failures. Corrected completion retained the exact primary first and cleanup exception second, performed zero truthiness evaluations, committed generation exactly once, preserved published UI, cleared active/local bookkeeping, and rejected retry. The committed regressions also passed. | Closed |

## Changed-range analysis

Since `223d04aa322df32e2adc5f5cd45b27111b111f4b`:

- Pyrolyze `src/pyrolyze/runtime/context_state_lcm/field_only_render.py:285` replaces truthiness-based exception selection with explicit presence selection.
- `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:61-63,116-132,211-293` adds sticky captured-metadata checks, exact integer-ID checks, additional coherence predicates, and failure retention independent of record authority.
- `tests/test_runtime_context_state_lcm_field_only_render.py:710-889` adds nine parameterized counterexamples covering the three merged dispositions.
- Remaining changes file the prior reports/remediation plan and update checkpoint evidence. No changes outside these dispositions were identified. Fixtures, canonical JSON, other controlling contracts, dependencies, activation, and resource admission are unchanged.

**New ARCHITECTURAL root causes: none identified.** The correction remains within existing admission, observation, and error-aggregation boundaries; it introduces no new interface, participant dispatcher, field authority, or resource mechanism.

## 0. Evidence base

- Verified all four exact HEADs and statuses at start and end: unchanged. Dependencies remained clean; Pyrolyze retained only the two excluded untracked rendering documents. Neither was read. No files, builds, caches, bytecode, checkouts, or Git state were written.
- Continued the prior Code review’s controlling-document and SC1/SC2 closure context. Read both legitimate prior-round consumer reports and `dev-docs/history/lifecycle-integration/PytoLifecyleIntegSC3-L0Consumer-RemPlan-1.md`; no current-round peer report was accessed.
- Read the complete correction diff, revised owner `render_attempt.py:40-390`, completion path `field_only_render.py:120-335`, and new tests `710-889`. Rechecked L0Plan Error/Consumer Contract and consumer checkpoint sections `312-373,423-451`; verified the other controlling contracts unchanged since the prior candidate.
- Retraced accepted manager phase construction at yidl-lifecycle `src/yidl_lifecycle/transaction_yidl.py:433-533` against the tightened predicates, without reopening accepted library outcomes.
- Ran the authorized three-file pytest command with both selectors unset, prescribed source exports, `PYTHONDONTWRITEBYTECODE=1`, and `-p no:cacheprovider -q --tb=short`: **native 128 passed in 4.70s; Python backend 128 passed in 10.99s**. Targets were the owner, field-only, and characterization test files.
- Independently ran both-backend in-memory probes: original truthiness counterexamples and prior-SHA controls; four key/ID relabel-and-restore admission cases; six terminal-authority faults; equal-but-nonidentical key compatibility.
- Verified all three consumer JSON files byte-identical to the initial candidate, historical JSON byte-identical to the implementation base, and all seven prior SC2 sections unchanged. Re-executed the fixture README’s historical reproduction using manager `371dfa530a975c27f7a6c09a7648f7f00532ab29`; output exactly matched the preserved JSON.
- Cumulative `git diff --check` passed. Source searches retained the same private activation/owner call sites.

## 2. Invariant analysis

- **Exception preservation:** The original masking attacks now fail. Falsy and raising-`__bool__` primary exceptions survive unchanged and ordered before local cleanup failure, without truthiness evaluation.
- **Sticky admission rejection:** Key and ID relabeling reject before a new local reset/body and before no-op reentry. Restoring metadata does not rehabilitate the owner. Generation remains pending and uncertified; publication and reuse are not claimed.
- **Rejected authority retains errors:** Boolean token ID, both original contradictory record combinations, partial application without failure evidence, ownership-lost evidence, and mixed valid/invalid failure entries all quarantine. Supplied exception objects remain outwardly reachable by identity. Actual published values remain untouched, with zero generation decisions and no second completion.
- **Legitimate evidence remains usable:** Both-backend canonical checks retain empty commit/rollback/abort, validation/preparation abort, incomplete discard/actions, partial application, and published-action-failure distinctions. Equal nonidentical caller keys still preserve the manager’s canonical original key.
- **SC1/SC2 closures remain intact:** Retained tests reran scope reentry, ownership loss, stale/external borrowing, recursive completion, lexical early-end protection, constructor/root ownership, retirement/resource admission, nested-cache reconciliation, published membership, and scheduler preservation. The correction changes no deferred resource-effect path.
- **Boundary and history remain intact:** No hidden production activation, resource adapter, manual participant engine, snapshot replacement, marker/compiler change, or historical-baseline substitution appeared. Publication, generation certification, and reuse readiness remain separate.

## 3. Risks and next action

Full/default/broader suites and the owner’s seven-file 147-test native gate were not independently repeated. Their recorded unchanged 13/14 failure identities remain owner evidence, not this review’s execution results or waivers. Parallel rendering, resource adapters, arbitrary payload-alias mutation, and multi-key atomicity remain uncertified.

**Next action:** File this Code GO and merge the independent current-round verdict at the exact revised tuple. Any resulting acceptance must remain limited to the private consumer; resource admission and broader activation stay gated.
