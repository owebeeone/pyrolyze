# Bounded Callback Selection — CODE-AXIS REVIEW

**Review object:** Pyrolyze `dd3d3a7..e1cce818e3c99712d54b37976a5794a8d85cfb57`, branch `lcm-resume`; controlling contract `dev-docs/PytoLifecyleIntegCallbacks.md`, status “bounded implementation contract.”
**Baseline:** Pyrolyze `dd3d3a746cec6bea84bd0c594500080e7a8a8523`. Unchanged dependencies: yidl-lifecycle `05554397d1837ecbeafa36e4685477dd5ff30fc6`; yidl `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`; astichi `1c47f781d3804130fdd61cbee07a3b2e4529158a`. Documents were read with `git show e1cce818:…`; tracked source reads were corroborated by clean tracked status.
**Date:** 2026-10-08
**Axis:** Architecture, interfaces, call-site compatibility, and error-path correctness. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — Three P2 findings block. I pre-commit to GO on a revision that resolves P2-1, P2-2, and P2-3 as specified.

---

## 0. Evidence base

- All four HEADs and statuses matched at start and end. Pyrolyze had only the two specified excluded untracked documents; dependencies were clean. Neither excluded document nor another reviewer’s current-round output was read. Nothing was modified.
- Read repository/workspace `AGENTS.md` and the available read-only `review-agent` skill; no `review-loop` skill was discoverable.
- Read the complete bounded diff, callback contract, completion consumer Boundary, and SC3 Local Completion Inventory/Writer And Key Audit.
- Inspected `src/pyrolyze/runtime/context_state_lcm/event_handler_slot_context.py:1-88`, `callback_render.py:1-104`, `component_call_slot_context.py:50-319`, `context_base.py:186-378`, `context_base.py:409-499`, and `context_base.py:662-728`.
- Traced constructor/manager injection, deactivation write scopes, registry reconciliation, completion authority, facade accessors, original/monolithic callback and component-owned callers, and the unchanged runtime selector.
- Read both callback fixtures, their JSON, characterization harness, and narrow callback faults. `git diff --check dd3d3a7 e1cce818` passed.
- From the Pyrolyze repository root (`.`), ran the prescribed environment and `../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short tests/test_lcm_integration_characterization.py tests/test_runtime_context_state_lcm_callbacks.py`: **19 passed native; 19 passed Python**. Bytecode/cache writes were disabled.
- Ran only in-memory probes under that environment. The three counterexamples below reproduced on both engines. Reference comparisons used retained original and monolithic implementations; component probes supplied the recognized `_pyrolyze_meta._func` protocol and unchanged argument schema.

## 1. Findings

### [P2-1] Deleted local discard publishes a failed component-owned selection

**Location:** `src/pyrolyze/runtime/context_state_lcm/component_call_slot_context.py:207-221`, specifically the deleted retained-handler rollback call; managed selection is staged at `event_handler_slot_context.py:46-48`.

**Violated invariant:** The unactivated decomposed route must preserve retained reference callback behavior; a failed child invocation must not silently accept its callback candidate.

**Reproduction:** On an unactivated root, accept component-owned pending handler A. In another root pass, pass binding B through `root.component_call`; the child raises inside its pass scope. Catch that exception in the parent and let the parent pass succeed. Invoke the retained dispatch.

**Observed impact:** Original and monolithic routes produce `["A", "A"]`; decomposed LCM produces `["A", "B"]`. The owned handler shares the parent transaction, and the remaining local rollback bookkeeping no longer discards its staged selection. Failed child work becomes callable.

**Required correction:** Preserve local failed-selection discard on the retained unactivated route without restoring manual publication or silently changing parent-catch semantics.

**Closure test:** Add this successful-parent/caught-child-failure comparison to the canonical callback fixture. Assert A remains selected, dispatch identity remains stable, and a subsequent successful B invocation can replace it.

### [P2-2] Global pruning treats failed-attempt visitation as current omission

**Location:** `src/pyrolyze/runtime/context_state_lcm/callback_render.py:69-79`; visitation originates at `component_call_slot_context.py:231-239` and is not restored for owned handlers by completion cleanup.

**Violated invariant:** A failed render preserves accepted owned handlers, and later child-only work must not retire them using stale scratch from that failed render.

**Reproduction:** Enable the private callback gate. Accept component-owned handler A. Invoke the same component with `None` instead of its pending handler, then fail the parent pass. A remains callable immediately after discard, but its `_seen_in_pass` remains false. Rerun the retained child with `component.child_context._run_boundary()`, without rebinding parent arguments.

**Observed impact:** Completion prunes the owned handler and stages retirement despite no new parent omission. Registration disappears and retained dispatch raises `event handler is inactive`. Original and monolithic references retain A across this sequence.

**Required correction:** Make owned-handler visitation attempt-local: restore/clear it on discard and restrict omission pruning to components whose owned-handler argument pass belongs to the completing attempt. Do not manually restore managed membership.

**Closure test:** Extend the owned-handler canonical case with failed omission followed by child-only rerun and retained-component reuse without reinvocation. Both must preserve A; a later successful parent omission must still retire it.

### [P2-3] Equal reselection cannot cancel staged explicit retirement

**Location:** `src/pyrolyze/runtime/context_state_lcm/event_handler_slot_context.py:46-48` and `:59-74`.

**Violated invariant:** Successful accepted membership must have the requested callback selection; explicit removal followed by reselection cannot leave a registered inactive handler.

**Reproduction:** Under the private callback gate, accept callback A. In one subsequent pass, deactivate its slot, then call `root.event_handler` for the same slot and exact A with `dirty=False`. Complete successfully and invoke the returned dispatch.

**Observed impact:** The accepted cache entry is reused and membership restored, but the current-key equality check skips selection writes, leaving pending retirement `None`. The slot is registered while dispatch raises `event handler is inactive`. Original, monolithic, and unactivated decomposed routes return a callable handler.

**Required correction:** Allow explicit retirement cancellation to stage the requested selection even when it equals current. Keep ordinary selection eligibility and the historical A/B/A quirk unchanged.

**Closure test:** Add successful and failed deactivate/reselect sequences using identical and value-equal callbacks with `dirty=False`. Assert accepted membership and callability, without premature current mutation.

## 2. Invariant analysis

The ordinary selection attacks held: strong stable dispatch reads current, bound receiver/function identity is preserved, dirty-forced equal-callable replacement retains the exact new object, and historical A/B/A results remain unchanged. Constructor inheritance injects the owning manager.

The four manual stores and transfer methods disappeared from the active decomposed implementation and callers. However, P2-1 demonstrates that deleting transfer calls did not preserve every retained caller’s discard semantics.

Empty handler UI uses the polymorphic surface. Original/monolithic implementation, historical callback JSON, and runtime selector are unchanged. The original field-only gate still rejects handlers; the new gate adds only exact handler slots. Retirement preparation stages managed values before owner completion, rather than manually publishing fields.

## 3. Risks and next action

Broad suite results remain lane-owner evidence, not independently rerun. Accepted manager/core-owner behavior, partial-publication quarantine, activation, and deferred resource categories were not reopened.

Next action: repair the three bounded callback defects, add the specified canonical regressions, and submit the settled tuple for focused re-review.
