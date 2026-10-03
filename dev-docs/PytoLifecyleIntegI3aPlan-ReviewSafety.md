# I3a Common Pass Plan — Safety-AXIS REVIEW

**Review object:** `dev-docs/PytoLifecyleIntegI3aPlan.md` at Pyrolyze `0a0968b848809d5cbaf33d66a61bb7705cd844d2`. DRAFT, plan-only checkpoint; reviewed 2026-10-03.
**Baseline:** Verified at review start and end:
- Pyrolyze: `0a0968b848809d5cbaf33d66a61bb7705cd844d2`.
- yidl-lifecycle: `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`.
- YIDL: `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`.
- Astichi: `387ca5e1da76204ee60922094734c13ee36383c0`.
- Parent, context only: `a20f8cfb633a268925464eb27728d1934a70aea9`.

Product and dependency source reads used `git show <pinned-SHA>:<path>`, not dirty dependency files. Unqualified citations below are relative to Pyrolyze.
**Date:** 2026-10-03.
**Axis:** Safety: degraded paths, completion ownership, irreversible cleanup, recovery, disclosure, and blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero P0, P1, P2, or P3 findings. This accepts the gated plan, not an implementation or runtime activation.

---

## 0. Evidence base

The review restarted under the corrected canonical prompt. No earlier verdict was carried forward.

- Ran `git rev-parse HEAD` and `git status --short` for the parent, and the corresponding `git -C <repo>` commands for all four pinned repositories, at start and end. All HEADs matched and remained unchanged. Pyrolyze contained only allowed untracked review-package/prompt files; excluded dependency and parent noise remained outside review.
- Ran `git -C pyrolyze rev-parse 0a0968b848809d5cbaf33d66a61bb7705cd844d2:dev-docs/PytoLifecyleIntegPlan.md` at both boundaries: blob `81d004dc44bc84516a3484e2a64be9667f0657bc`.
- Ran `git -C pyrolyze diff -- src tests dev-docs/PytoLifecyleIntegI3aPlan.md dev-docs/PytoLifecyleIntegPlan.md` at both boundaries: empty. Read the pinned addendum, lines 1–232, and its specified diff from `5af937343ef3e557667d96bbf6830acce555353a`: a new 232-line document.
- Read parent `AGENTS.md`, Pyrolyze `AGENTS.md`, and the corrected canonical prompt. The named `review-loop` skill was unavailable in the supplied inventory and inspected locations; no additional skill instructions were inferred.
- Read governing `dev-docs/PytoLifecyleIntegPlan.md`: lines 33–73, 152–362, 530–612, 826–886, 1080–1100, and 1371–1403; `dev-docs/PytoLifecyleIntegI1bEvidence.md`, lines 1–146; and historical `dev-docs/PytoLifecyleIntegHolderFirstPlan-ReviewLoop.md`, lines 1–69.
- Read `src/pyrolyze/runtime/context_state_lcm/context_base.py`, lines 67–125, 186–305, 334–408, 491–504, and 591–602; `_base.py`, lines 58–95; `slot_context.py`, lines 1–53; and `render_context.py`, lines 23–80, 171–222, and 315–349.
- Read that directory’s `_support.py`, lines 396–424 and 737–790; `leaf_slot_context.py`, lines 1–43; `slot_expr_slot_context.py`, lines 13–104; and `slot_call_slot_context.py`, lines 21–61 and 167–218. Read owner facade `src/pyrolyze/runtime/context_bare_refactor_lcm.py`, lines 370–398 and 999–1027.
- Read reference `src/pyrolyze/runtime/context_original.py`, lines 459–480, 664–781, 2187–2205, 2302–2313, and 2346–2359. Read `tests/test_lcm_integration_characterization.py`, lines 1–58; fixture `tests/data/lcm_integration/characterize.py`, lines 106–226; `shared_completion.py`, lines 1–88; its complete JSON baseline; and relevant original-baseline failure/recovery observations.
- Read pinned `yidl-lifecycle/src/yidl_lifecycle/transaction_yidl.py`, lines 80–142, 173–295, and 322–439; and `src/yidl_lifecycle/yidl/lifecycle_managed.yidl`, lines 241–326 and 388–443.

No tests, builds, writes, or Git mutations were performed. The reported **27 passes in 4.41s** are drafting evidence using dirty dependencies, not reviewer verification of this tuple.

## 2. Invariant analysis

The following attacks failed to establish a defect permitted by the plan:

1. **Borrowed activity suppresses local initialization.** The existing predicate tests shared-key activity, and its duplicate-entry guard fails for empty maps. Addendum lines 75–87 require separate local activity, actual-entry resets, empty-map duplicate rejection, and no-op scoped re-entry. Lines 200–202 require auditing affected callers before value migration.

2. **Caught child failure discards parent work or leaves failed candidates publishable.** The pinned TM’s nested counts are not savepoints; rollback clears the whole key. Addendum lines 92–95 require an evidenced discard owner/path, while lines 106–135 prohibit borrowed completion and require stopping before unsupported isolation changes. Merely identifying the parent as owner cannot satisfy the required discard evidence.

3. **Parent failure undoes an independently accepted child.** The original golden records changed child UI alongside retained parent UI after failure. Addendum lines 115–116 and 127–128 preserve that publication boundary; lines 180–182 require observing it. The plan does not claim outer atomicity.

4. **Managed conversion removes out-of-pass invalidation permissions or publishes unrelated candidates.** Existing setters write ordinary fields directly. Lines 62–64, 117–125, and 194–196 require writer/cohort probes before conversion and forbid opening a shared key around a dirty setter as a workaround. An incompatible declaration must remain unmigrated pending a bounded decision.

5. **Membership discard is mistaken for resource recovery.** Deactivation unregisters slots and invokes external cleanup separately from managed-map assignments. Lines 121–122 explicitly reject that conflation. Lines 139–150 condition snapshot deletion on compatible cleanup and retain unmigrated resource dispatch rather than deleting the mixed loop.

6. **Completion exception triggers fictitious rollback or leaves local activity stuck.** The pinned TM clears key activity in `finally`, including after publication exceptions. Lines 96–102 explicitly prohibit rollback of an already-finished key and require exactly-once local exit across scope handles, direct leaf execution, and derived overrides. Failure draining is not falsely promised.

7. **Candidate state leaks through committed readers or current-map mutation.** The pinned default facade exposes working values; `.current` selects published storage. Lines 60–71 mandate whole-map replacement and explicit committed-reader separation, including derived overrides and synchronization. Lines 172–174 require public and candidate observations.

8. **Dirty drafting evidence becomes false completion or widens scope.** Lines 30–36 disclose the dependency mismatch; lines 130–135 forbid accepting partial migration as completed I3a; lines 194–213 require settled dependencies, regression evidence, and independent implementation review. Lines 15–19 fence runtime defaults, library APIs, callbacks, resources, and manager unification. No additional production-data disclosure surface is authorized.

## 3. Risks and next action

The plan does not demonstrate that every proposed migration is achievable with the pinned API. Same-key caught recovery, invalidation visibility, resource cleanup, and completion exceptions remain substantive implementation risks. Its stop gates appropriately make those unresolved paths decision points, not permission to defer regressions.

**Next action:** retain plan-only acceptance and, after explicit implementation authorization, perform step 1’s dependency settlement and writer/cohort permission-isolation probes before changing authority or deleting snapshots. This GO does not authorize implementation, tagging, roll-build, or default-runtime activation.
