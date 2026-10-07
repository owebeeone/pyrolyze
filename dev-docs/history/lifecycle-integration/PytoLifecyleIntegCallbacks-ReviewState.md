# Pyrolyze Callback Selection — STATE-AXIS REVIEW

**Review object:** Pyrolyze `dd3d3a7..e1cce818e3c99712d54b37976a5794a8d85cfb57`, bounded callback selection, branch `lcm-resume`. Controlling contract: `dev-docs/PytoLifecyleIntegCallbacks.md` at that HEAD. Candidate implementation reviewed on 2026-10-08.
**Baseline:** Pyrolyze `dd3d3a746cec6bea84bd0c594500080e7a8a8523`; unchanged yidl-lifecycle `05554397d1837ecbeafa36e4685477dd5ff30fc6`, YIDL `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`, Astichi `1c47f781d3804130fdd61cbee07a3b2e4529158a`. Documents were read using `git show HEAD:`, implementation through the baseline diff and numbered clean tracked-source reads.
**Date:** 2026-10-08
**Axis:** STATE: publication authority, membership, rollback, recovery legality, and adverse write interleavings. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block. I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified.

---

## 0. Evidence base

- Start and end: `git rev-parse HEAD` and `git status --short --branch` in each repository root (`.`). All four HEADs matched throughout. Tracked trees remained clean; Pyrolyze retained only the two excluded untracked documents. Neither was read.
- Authority: repository and workspace `AGENTS.md`; `dev-docs/README.md`; callback contract, especially Scope and Completion Timeline; consumer contract Boundary; SC3 registry/writer constraints and D5 completion boundary. No current-round reviewer report was inspected.
- Main implementation: `src/pyrolyze/runtime/context_state_lcm/callback_render.py:1-104`, `event_handler_slot_context.py:1-88`, `component_call_slot_context.py:1-320`, and `field_only_render.py:1-338`.
- Supporting source under the same runtime directory: `context_base.py:186-233,299-467,704-728`, `slot_context.py:35-59`, `_base.py:79-105`, `render_context.py:95-190,304-311`, and `render_attempt.py:75-145,211-374`. Facade: `src/pyrolyze/runtime/context_bare_refactor_lcm.py:417-450`.
- Coverage read: `tests/data/lcm_integration/callback_selection_lifecycle.py:1-251`, `callback_selection.py:1-102`, `tests/test_runtime_context_state_lcm_callbacks.py:1-107`, and `tests/test_lcm_integration_characterization.py:1-88`.
- At Pyrolyze repository root (`.`), using the workspace virtualenv, bytecode disabled, both context selectors unset, and local `src` imports from the four repositories:
  `python -m pytest -p no:cacheprovider -q --tb=short tests/test_lcm_integration_characterization.py tests/test_runtime_context_state_lcm_callbacks.py`
  Result: **19 passed native; 19 passed Python**.
- In-memory probes reproduced both findings on native and Python. Additional native probes covered callback-property token replacement, retirement failure between callback/key writes after an earlier handler was staged, and unchanged field-only admission. No probe files were written.
- `git diff --check dd3d3a7 e1cce818e3c99712d54b37976a5794a8d85cfb57` passed. No broad suites, builds, regeneration, git mutations, or dependency implementation review were performed.

## 1. Findings

### [P2-1] Global normalization promotes stale failed-pass visitation into removal authority

**Location:** `src/pyrolyze/runtime/context_state_lcm/callback_render.py:69-79`. Component visitation is reset at `component_call_slot_context.py:231-239`; coherent-discard cleanup at `context_base.py:370-380` does not restore these component-owned handler flags.

**Violated invariant:** A failed render-owned removal remains provisional. A later unrelated write scope must not adopt that failed removal.

**Reproduction:** Use the component-owned pending-handler construction demonstrated in `tests/data/lcm_integration/callback_selection_lifecycle.py:193-212`:
1. Accept owned handler H as a component argument, plus independent root handler U.
2. In another root pass, invoke the same component with `None`, retain U, let the child succeed, then raise `ValueError` in the parent.
3. After discard, H remains registered and callable, but H's `_seen_in_pass` is `False`.
4. Outside any pass, call U's accepted holder's `deactivate()`.

The unrelated removal successfully completes, but global component normalization removes H too. Native output was `after_failed_removal True False True`, followed by `after_unrelated_removal False False True`; H's dispatch then raised `event handler is inactive`. Python reproduced the same state transition. The final `True` indicates that reuse was nevertheless certified.

**Impact:** A cleanly discarded omission becomes an unintended accepted retirement during a subsequent supported operation.

**Required correction:** Make owned-handler omission authority attempt-specific. Normalize only owners whose owned-handler pass participated in the current attempt, and clear or restore their visitation/order scratch at coherent completion. An unvisited owner must retain accepted membership.

**Closure test:** Add the above failed-child-omission/parent-failure followed by unrelated out-of-pass handler removal. Assert H retains its callback, membership, and dispatch identity while U alone retires; verify on both engines.

### [P2-2] Callback introspection and equality invalidate the token fence before selection writes

**Location:** `src/pyrolyze/runtime/context_state_lcm/event_handler_slot_context.py:34-48`, particularly the authority check at line 41 preceding user-executable key construction/comparison at lines 44-46.

**Violated invariant:** Selection writes belong exclusively to the original render token and must not mutate an externally installed replacement transaction.

**Reproduction:** Accept callable A, whose armed `__eq__` executes `manager.rollback(PASS_TX_KEY)`, installs `manager.begin(PASS_TX_KEY)`, and returns `False`. Arm A, then select callback B with `dirty=False` in a root pass. Equality runs after the original-token check; both selection fields are consequently written into the replacement.

Outer completion raises the ownership error, but the replacement remains active with `_callback is B` and `_callback_key is B`; current selection is still A. Committing that replacement as a diagnostic publishes B, and the held dispatch calls B. This reproduced on native and Python. A native variant using B's `__self__` property reproduced replacement contamination with `dirty=True`, without equality.

**Impact:** Late quarantine correctly rejects the original owner's authority but cannot undo writes already made into someone else's token. A failed render's selection can become callable through replacement publication.

**Required correction:** Retain the original owner/token across callback introspection and comparison, then revalidate that same authority after user-executable operations and immediately before selection writes. Do not validate whichever owner happens to be active afterward.

**Closure test:** Extend the narrow stale-token test with replacement during equality and callback-property access. Assert the replacement receives neither selection field, current selection remains A, and the original attempt remains uncertified and non-reusable. Run both engines.

## 2. Invariant analysis

- Canonical tests preserved stable dispatch, current-only visibility, inactive new handlers, dirty-forced equal-callable replacement, bound receiver identity, the historical A/B/A selection quirk, and empty handler UI.
- Successful nested child selection followed by parent failure remained unpublished. Caught child failure poisoned outer completion. These immediate rollback guarantees held; P2-1 concerns their later state transition.
- Ordinary omission/removal, failed removal, new-handler discard, and stale-holder removal preserving a same-ID replacement passed canonical coverage.
- Retirement preparation was attacked after one handler had been fully staged and after the next handler's callback write but before its key write. Both accepted handlers and membership survived coherent discard; the identical preparation exception escaped, `published` was `False`, and clean reuse remained legal.
- Preparation reentry was rejected by the focused fault test. Pre-entry token replacement was rejected before mutation; replacement during key evaluation was not, as P2-2 demonstrates.
- The accepted owner correctly retained `published=None` and `reuse_ready=False` after ownership loss. This review found no fabricated undo/retry certificate in that dependency.
- The original field-only gate still rejected handlers and poisoned a caught admission failure. The callback gate continued rejecting slot-expression, slot-call, and override resources.

## 3. Risks and next action

The adapter remains private. This review does not certify activation, external registration, subscriptions/effects, component replacement/retirement, stronger atomicity, or unrelated baseline failures. No process-kill or filesystem durability experiment was run; this diff adds no persistence protocol.

Next action: correct P2-1 and P2-2 in one bounded revision, add their regression cases, and rerun the permitted focused native/Python coverage before re-verdict.
