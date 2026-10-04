# SC2 Remediation Round 1 — CODE-AXIS REVIEW

**Review object:** `53c41674f43ab97401ac9b30a79575c19ab5dca9..ca731d89a0086e0bff48dc426d1b5b1472aba869`, within cumulative SC2 diff `1b246d47e934835a4871fbbfc651fae78440b913..ca731d89a0086e0bff48dc426d1b5b1472aba869`. Controlling document: `dev-docs/PytoLifecyleIntegSC2.md`, DRAFT implementation checkpoint, dated 2026-10-04.
**Baseline:** Pyrolyze `ca731d89a0086e0bff48dc426d1b5b1472aba869`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent context only `a20f8cfb633a268925464eb27728d1934a70aea9`. Documents/dependencies were read through pinned `git show` and byte-verified clean exports.
**Date:** 2026-10-04.
**Axis:** Code: architecture, interfaces, call graphs, ownership, compatibility, and error paths. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block; no P0, P1, or P3 findings. I pre-commit to GO on a revision that resolves P2-6 and P2-7 as specified.

---

## Prior-finding closure table
| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| Code P2-1 | Validate parent and nearest-render ownership before allocation | Original cross-root leaf/resource constructions reject; reversed links also reject. Caught rejection aborts; registries/current membership remain empty. Initialization ordering re-traced. | Original closed |
| Code P2-2 | Reject omitted/conflicting scheduler ownership and owned-root activation | Original owner-only and unrelated-root constructors reject; a nested scheduler input also rejects. Legacy owned-root activation rejects. | Closed |
| Code P2-3 | Preflight direct component deactivation/disposal | Original inside/outside paths and recursive ancestor deactivation reject before changing child identity, callback, queue, UI, or generation. | Closed |
| Code P2-4 | Preflight component descendants of removed ancestors | Original native-leaf-contained, committed component with queued boundary cannot be omitted. Membership, callback, queue, UI, and generation survive rejection. Candidate-only variant remains, P2-7. | Original closed; disposition incomplete |
| Code P2-5 | Published debug lookup traverses current membership | Original newly created leaf remains inactive/invisible until commit; discarded additions remain invisible; published removal observations remain old until completion. | Closed |
| State P2-1 | Retain native/publication execution claims after early local completion | Original native callback and publication-body failures retain old current UI/generation, preserve the exact primary error, and permit retry. No-op re-entry variant also verified. | Verified closed on Code axis |
| State P2-2 | Reject direct/recursive retirement before side effects | Original disposal sequence and inside/outside/caught/ancestor variants independently reproduced; no destructive mutation occurs. | Verified closed on Code axis |
| State P2-3 | Check identity before no-op re-entry | Original replaced-token sequence excludes the nested body; replacement has no participants, survives cleanup, and commits no UI. Old owner is quarantined. | Verified closed on Code axis |
| State P2-4 | Separate published debug membership from reuse cache | Original candidate/current contradiction no longer reproduces; activity and slot-specific UI agree with current membership. | Verified closed on Code axis |
| State P2-5 | Reconcile participating discarded nested caches | Original retained newly discarded nested root has empty current membership and registry; fresh retry creates a different component. | Verified closed on Code axis |

## Changed-range analysis
The remediation changes seven runtime modules: two-sided constructor admission, owned-render scheduler validation, recursive retirement preflight, lexical execution counting, native invocation fencing, current-only debug lookup, and participating-root cache reconciliation. It adds 208 narrow-test lines and extends the canonical fixture/target; remaining changes are controlling/process documents. The accepted SC1 mechanism is unchanged in this remediation.

The changes map to the eight merged dispositions; no unrelated activation, dependency change, or historical-fixture rewrite was found. The cumulative audit nevertheless exposed P2-6, an internal mutation caller left incompatible with the changed published-reader contract, and P2-7, incomplete retirement coverage across successive local passes. **Neither is a NEW ARCHITECTURAL root cause:** both are localized call-site/gate omissions within the existing candidate/current and retirement boundaries. P2-7 extends the prior Code P2-4 disposition.

## 0. Evidence base
- Verified all five HEADs at start and end; every SHA matched. Final `git diff -- src tests` was empty. No files were written, builds performed, or git state mutated. No current-round peer prompt/report was read.
- Read parent/Pyrolyze `AGENTS.md`, the supplied review-loop skill/template, SC2.md:1–149, the SingleCohortPlan authority/local-pass/publication/SC2 contracts, SC1-Remediation and SC1-ReviewLoop, both prior SC2 reports, RemPlan-1, and ReviewLoop.
- Inspected remediation and cumulative diffs. Principal source ranges: `context_state_lcm/field_only_render.py:1–304`, `_base.py:1–130`, `context_base.py:106–375,395–760`, `render_context.py:24–471`, `slot_context.py:1–58`, `component_call_slot_context.py:50–325`, `leaf_slot_context.py:1–50`, and `render_attempt.py:1–387`. Also traced retained facades, visitor traversal, and generation completion.
- Read the narrow tests:1–356 and canonical fixture:1–382 with its authored JSON. Byte-compared clean dependency exports against pinned commits: lifecycle 17, YIDL 45, Astichi 84 Python/YIDL source files matched. Read the real transaction manager and managed-field preparation/application/discard templates; actual admitted classes have no user transaction hooks or freeze/thaw converters.
- Ran the permitted command from the Pyrolyze root, with clean exports, selection variables unset, bytecode disabled, and pytest cache disabled: `env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="src:$snapshot/yidl-lifecycle/src:$snapshot/yidl/src:$snapshot/astichi/src" "$PYTHON" -m pytest -p no:cacheprovider -q --tb=short tests/test_runtime_context_state_lcm_field_only_render.py tests/test_lcm_integration_characterization.py::test_common_pass_single_cohort_golden`. Result: **33 passed in 4.11s**.
- Independently ran original-counterexample and additional in-memory probes using real managers, without generated-private-state writes or mocked completion. Reproductions below use `_root`, `_slot_id`, `_leaf`, `_component`, `_ui`, `_tracker`, and `runtime` loaded through `runpy.run_path("tests/data/lcm_integration/common_pass_single_cohort.py")`. All product paths below are Pyrolyze-relative.

## 1. Findings
### [P2-6] Deactivation rebuilds candidate membership from the published reader
**Location and invariant:** `src/pyrolyze/runtime/context_state_lcm/slot_context.py:50–58`, especially line 55, still uses `children_by_slot_id()` for mutation input. `context_base.py:111–112` now makes that reader current-only on activated graphs. Published-reader isolation must not erase unrelated candidate membership; SC2.md:55–57 requires candidate assembly and replacement writes.

**Reproduction and impact:** Commit leaf A at slot 1. In the next root pass, revisit A, create/invoke leaf B at slot 3 emitting `"new-b"`, then call `A.deactivate()`. Immediately before deactivation, candidate children are `[1,3]` and current children are `[1]`. Deactivation copies current minus A and replaces candidate children with `{}`. Outer completion succeeds with empty root UI/membership, while B’s own current UI becomes `["new-b"]`. The same failure reproduces with a plain structural A. A permitted field-only removal silently drops an unrelated rendered sibling and commits inconsistent reachable versus retained state.

**Required correction and closure test:** Use candidate membership for internal deactivation traversal and parent-map edits, retaining current-only published readers and component-descendant preflight. Audit both reader calls in this method. Extend canonical observations so removing an existing leaf/plain slot preserves a newly rendered sibling and its order/UI; add a narrow discard variant proving published membership remains unchanged after failure.

### [P2-7] Retirement admission misses components introduced by an earlier local pass
**Location and invariant:** `src/pyrolyze/runtime/context_state_lcm/context_base.py:331–357`: local entry clears the preceding candidate child map, but exit checks retirement only against `current.children_state`. SC2.md:27–29,62–63 gates component retirement and requires subtree preflight. A component cannot evade that gate merely because its first creation and later omission occur within one outer attempt.

**Reproduction and impact:** In one fresh root pass, ensure native leaf P at slot 5. Its first `invoke_native` creates `_component(P, "nested")`; retain nested root N and queue its leaf through `N._queue_invalidation_from(N._slots_by_id[_slot_id(1)])`. Invoke P again with an empty native callback. P’s candidate children change from `[2]` to `[]`; its current children are still empty, so no retirement check runs. Outer completion succeeds: P has no published children, root UI is empty, N’s current UI is `["nested"]`, one boundary remains queued, and committed generation is 1. `root.run_pending_invalidations()` executes that unreachable boundary and advances generation to 2. This uses admitted constructors and normal invocation/queue methods.

**Required correction and closure test:** Cover previously introduced candidate component descendants when a later local pass removes them. Either reject that repeat topology before removal or enforce the retirement check against the relevant preceding candidate subtree; do not implement deferred retirement or treat cache reconciliation as authorization. Add a narrow two-native-invocation regression requiring rejection/attempt failure, no orphan candidate publication or successful generation advancement, and unchanged pre-existing current graph. Retain the original committed-descendant queue regression.

## 2. Invariant analysis
Constructor attacks from both parent and render now fail before lifecycle initialization/attachment; omitted/conflicting owned-render scheduler inputs and standalone owned activation also fail. Exact normal constructors share the root manager before initialization. Plain structural slots construct successfully without requiring UI-bearing state.

Direct, disposal, recursive, and committed-subtree retirement attacks now reject before scheduler/callback/pointer mutation. Published debug additions/removals and retained discarded nested caches passed independently. Native, publication, lexical-pass, and no-op execution claims prevent early completion; replacement-token admission excludes foreign writes. Sticky failure, primary-error retention, clean retry, other-key isolation, and validator discard held in the permitted canonical run and focused probes.

Cumulative call-site inspection found no activated fallback into legacy local completion on the admitted paths. An independent unactivated nested-component probe retained its historical separate manager and early publication. Those results do not cure P2-6’s mutation-reader mismatch or P2-7’s candidate-only retirement omission.

## 3. Risks and next action
The full/default and broader unactivated suites were not independently rerun. Owner evidence remains **887 passed/13 unchanged failures/20 skipped/1 warning** and **41 passed/14 unchanged failures**, respectively, not an all-green claim. Broad activation, SC3 adapters, SC4 migration, generic manager redesign, and excluded dependency work remain outside this verdict.

**Next action:** Keep SC2 unaccepted and prepare one bounded second remediation addressing P2-6 and P2-7, then settle a revised tuple and independently verify these counterexamples. This review supplies no new architectural root and does not trigger the architectural stop condition.
