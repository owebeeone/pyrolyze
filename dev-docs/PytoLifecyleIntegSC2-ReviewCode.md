# SC2 Private Field-Only Render Wiring — CODE-AXIS REVIEW

**Review object:** Implementation diff `1b246d47e934835a4871fbbfc651fae78440b913..53c41674f43ab97401ac9b30a79575c19ab5dca9`, controlled by `dev-docs/PytoLifecyleIntegSC2.md`, DRAFT, dated 2026-10-04.
**Baseline:** Pyrolyze `53c41674f43ab97401ac9b30a79575c19ab5dca9`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent context only `a20f8cfb633a268925464eb27728d1934a70aea9`. Committed documents/dependency code were read through `git show` and the supplied clean exports; inspected Pyrolyze source/test files matched HEAD.
**Date:** 2026-10-04.
**Axis:** Code: architecture, interfaces, call graphs, ownership, compatibility, and error paths. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — five P2 findings block. I pre-commit to GO on a revision that resolves P2-1 through P2-5 as specified.

---

## 0. Evidence base

- Verified all five HEADs at review start and end: every SHA remained exactly pinned. Final `git diff -- src tests` was empty. No files were written, no builds or git mutations were performed, and no current-round peer prompt/report was read.
- Read parent/Pyrolyze `AGENTS.md`, the dispatched review-loop skill and canonical template, SC2.md lines 1–139, SingleCohortPlan.md including its ownership/publication contracts and SC2 refinement, and SC1-Remediation.md/SC1-ReviewLoop.md.
- Inspected the complete 13-file SC2 diff. Read `field_only_render.py:1–257`, `context_base.py:1–760`, `render_context.py:1–449`, `component_call_slot_context.py:1–319`, `_base.py:1–123`, leaf/structural state managers, retained facade constructors/readers, and `visitor.py` traversal.
- Read pinned lifecycle transaction completion and generated managed/core templates. In-memory inspection of actual enlisted participants found no user transaction hooks or converters; generated apply/after paths contained no user callback calls.
- Ran the permitted command with the supplied Python and clean exports: `env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="src:$snapshot/yidl-lifecycle/src:$snapshot/yidl/src:$snapshot/astichi/src" "$PYTHON" -m pytest -p no:cacheprovider -q --tb=short tests/test_runtime_context_state_lcm_field_only_render.py tests/test_lcm_integration_characterization.py::test_common_pass_single_cohort_golden`. Result: **16 passed in 4.10s**.
- Ran read-only, in-memory counterexamples using the real runtime/manager. The shorthand `_root`, `_slot_id`, `_emit`, `_component`, and `_ui` below denotes definitions loaded with `runpy.run_path("tests/data/lcm_integration/common_pass_single_cohort.py")`. All product locations below are relative to the Pyrolyze repository.

## 1. Findings

### [P2-1] Direct slot admission ignores the activated parent’s graph
**Location and invariant:** `src/pyrolyze/runtime/context_state_lcm/_base.py:82–95` chooses admission solely from `render_context_state_mgr`; `slot_context.py:18–20` subsequently attaches to the independently supplied parent. SC2.md:18–24 requires deferred constructors to fail before resource work and forbids legacy completion inside an activated graph.

**Reproduction and impact:** Create activated `root = _root()` and unactivated `legacy = runtime.RenderContext()`. Inside `root.pass_scope()`, construct `runtime.SlotExprSlotContext(render_context=legacy, parent=root, slot_id=_slot_id(7), seen_in_pass=True)`. Construction succeeds, allocates its real call-site manager, and outer success publishes the forbidden child into `root.iter_children()`. An exact `LeafSlotContext` constructed with the same mismatched links also uses the legacy manager: `invoke_native(_emit, ("early",), {}, context_param="context")` publishes its current UI before the root finishes; after raising a parent error, the retained leaf still reports `["early"]`. These are actual constructor paths, not private manager-slot patches.

**Required correction and closure test:** Before lifecycle/resource initialization or graph attachment, validate the parent and render-root relationship and resolve activation from both. Reject incompatible graphs and poison the activated owning attempt when rejection is caught. Add narrow mismatched-parent tests for an admitted leaf and a forbidden resource slot, asserting rejection before allocation/registration, unchanged current membership/UI, and no independent publication.

### [P2-2] Omitting the scheduler root bypasses nested-render admission
**Location and invariant:** `src/pyrolyze/runtime/context_state_lcm/render_context.py:36–57` enables its nested ownership check only when the supplied scheduler root resolves an active gate. `field_only_render.py:29–44` also permits activation of an owned component-render context whose scheduler root is itself. SC2.md:13–16 requires nested renders to receive the owning root’s manager before initialization.

**Reproduction and impact:** Inside an activated root pass, ensure an exact component slot, then call `runtime.RenderContext(owner_slot=component)` without `scheduler_root`. It succeeds with a different manager. Entering this nested context’s pass and emitting `"early"` publishes its current UI while the original root’s render token remains active. `_enable_field_only_render(nested._state_mgr)` also succeeds although its kind is `component_render`. Supplying an unactivated unrelated scheduler root likewise bypasses the new ownership check. The optional argument therefore permits an owned render to escape the activation boundary.

**Required correction and closure test:** Resolve or validate scheduler ownership from the owner slot before allocating a manager; reject omitted/conflicting ownership inputs instead of silently treating an owned render as independent. Reject owned contexts at standalone root activation. Test owner-slot-only and conflicting-root constructors before initialization, while retaining the canonical independent-root and normal nested-sharing observations.

### [P2-3] Direct component deactivation executes the deferred disposal route
**Location and invariant:** The guard added at `component_call_slot_context.py:105–110` covers replacement, but retained `deactivate():228–231` reaches `_dispose_child_context():306–319` without admission. SC2.md:22–24 gates component retirement; membership rollback cannot restore independently detached component state.

**Reproduction and impact:** Commit `_component(root, "old")` and retain its nested context. During the next root pass, revisit the component, call `component.deactivate()`, then raise `ValueError("parent failure")`. Deactivation succeeds before the error: the nested callback is cleared and `component.child_context` becomes `None`. Root rollback restores the current component member and UI `["old"]`, but not its child context. Calling `deactivate()` outside rendering is also admitted and completes disposal. The graph can retain published membership/UI for a component whose execution state was already destroyed.

**Required correction and closure test:** Gate direct component deactivation/disposal before scheduler removal, child traversal, callback clearing, or pointer changes. Do not implement the deferred disposal protocol here. Test direct retirement both outside and inside a pass, including caught rejection, asserting unchanged child identity, callback, scheduler state, current membership, and UI.

### [P2-4] Removing an ancestor silently retires nested components
**Location and invariant:** `src/pyrolyze/runtime/context_state_lcm/context_base.py:350–359` checks only immediate current children for component retirement. Registry reconciliation at `field_only_render.py:244–257` then drops unreachable subtrees without checking their component descendants. SC2.md:22 requires component retirement to remain gated.

**Reproduction and impact:** Commit the admitted topology root → native leaf → component by invoking a native leaf function that calls `_component(context, "nested")`. Queue the component’s nested render boundary. Execute an empty root pass. It succeeds, publishes empty membership/UI, and removes the subtree from the root cache, while the nested render remains mounted and queued. `root.run_pending_invalidations()` subsequently executes that orphan boundary and advances the root generation to 3. This counterexample uses matching roots and ordinary admitted constructors.

**Required correction and closure test:** Before accepting subtree removal, detect component descendants and reject the deferred retirement, or reject that topology at admission. Cache reconciliation must not substitute for retirement authorization. Add a leaf-contained-component removal test with a queued boundary, asserting rejection and preservation of the owned current graph.

### [P2-5] The debug membership reader publishes candidate cache entries
**Location and invariant:** `src/pyrolyze/runtime/context_state_lcm/render_context.py:234–235` still implements `debug_is_active` using `_slots_by_id`. Constructors populate that cache immediately; SC2 reconciliation occurs only at outer completion. SC2.md:48–53 requires published debug/membership readers to use current membership and explicitly distinguishes registration cache from publication.

**Reproduction and impact:** On a fresh activated root, enter `root.pass_scope()` and create/invoke `_leaf(root, "candidate")`. Before outer exit, `root.debug_children_of()` returns `()`, but `root.debug_is_active(_slot_id(1))` returns `True`. The newly reported active member is not published and may disappear on rollback. Published graph inspection therefore contradicts itself during an attempt.

**Required correction and closure test:** On activated graphs, derive debug membership from current reachable graph membership, leaving the candidate lookup cache available for internal slot reuse. Extend the canonical visibility observations to require false before publication, true after successful publication, and false after failed first creation.

## 2. Invariant analysis

The normal admitted constructor path shares the scheduler-root manager before lifecycle initialization; the diff contains no allocate-then-patch workaround. Real outer ownership, local activity, lexical early-release protection, caught-child poisoning, parent-failure discard, repeated-pass order, independent roots, and explicit other-key preservation held in the permitted tests and source trace. The actual validator fault performs validation followed by rollback/after-rollback without apply, preserves generation, and permits clean retry. Lost ownership and adapter-cleanup failures quarantine retry.

Those successful attacks do not cover malformed constructor ownership, direct or transitive retirement, or cache-backed published membership. Findings P2-1 through P2-5 arise specifically from the newly activated boundary, not from a demand to activate deferred resource routes or repair unrelated baseline debt.

## 3. Risks and next action

The full default and broader decomposed suites were not independently rerun. Their supplied 870-pass/13-failure/20-skip and 41-pass/14-failure results remain owner evidence, not an all-green claim or waiver. Broad activation, SC3 adapters, SC4 field migration, and generic cross-key atomicity remain excluded.

The next action is one bounded remediation patch addressing P2-1 through P2-5 with their closure tests, followed by review at a newly settled tuple before accepting SC2.
