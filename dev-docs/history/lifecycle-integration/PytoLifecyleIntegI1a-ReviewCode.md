# I1a Constructor Checkpoint — CODE-AXIS REVIEW

**Review object:** I1a at Pyrolyze `30cb868c168d70907ad2fceff1bb8e2841dda16e`; diff from `1aab26c7cccb19bd77e1bfd6f0365871972134dd`. Controlling DRAFT: `dev-docs/PytoLifecyleIntegPlan.md`, accepted blob `81d004dc44bc84516a3484e2a64be9667f0657bc`. Interior implementation review, 2026-10-03.

**Baseline:**
- Pyrolyze: `30cb868c168d70907ad2fceff1bb8e2841dda16e`.
- yidl-lifecycle: `cdf08544deea846bca4fa7e0c468ebee8d41e138`.
- YIDL: `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`, committed view only.
- Astichi: `387ca5e1da76204ee60922094734c13ee36383c0`.
- Parent workspace: `a20f8cfb633a268925464eb27728d1934a70aea9`, context only.

Sources were inspected through pinned `git show`, the exact permitted diff, and clean source reads. Parent/YIDL content inspection used committed views exclusively.

**Date:** 2026-10-03  
**Axis:** Code: architecture, interfaces, call graphs, constructor compatibility, ownership, and error paths. Independent, adversarial, read-only. This is the recorded single-axis interior gate; nothing relies on a current-round counterpart report. Filed verbatim by the lane owner.

**Verdict: GO** — zero P0/P1/P2/P3 findings. This verdict covers I1a only, not completed holder replacement, unification, or activation.

---

## 0. Evidence base

Paths below are relative to their owning repository.

- Verified all five HEADs and inspected statuses at start and end. Every HEAD matched the supplied tuple. Pyrolyze contained only the authorized untracked Code prompt; lifecycle and Astichi were clean. Excluded YIDL/parent dirt remained unchanged.
- Read applicable parent/Pyrolyze `AGENTS.md` and the review-loop skill. No current-round counterpart prompt or report was read.
- Inspected the complete permitted diff: three source files, two narrow test files, and `dev-docs/PytoLifecyleIntegI1aEvidence.md:1–95`.
- Independently compared complete committed plan outputs at accepted revision `78e3184132eae33169ae3c329be35f3146ed338a` and the reviewed revision: identical. Examined particularly lines 152–232, 364–428, and 784–824.
- Traced `context_bare_refactor_lcm.py:63–104,327–350,927–947`; `context_state_lcm/_base.py:15–24`; `context_base.py:67–85,94–162,244–363`; `slot_context.py:11–43`; `rerunnable_slot_context.py:7–12`; and `render_context.py:23–65`.
- Examined decorated construction and attachment in `slot_expr_slot_context.py:12–74` and `component_call_slot_context.py:28–116`; retained callback behavior in `event_handler_slot_context.py`; and independent call-site allocation in `call_site_context.py:146–157`.
- Read lifecycle generation/harvesting in `lifecycle.py:34–64`, `lifecycle_harvester.py:44–145`, and `yidl/lifecycle_core.yidl:634–659`. Inspected committed YIDL package/runtime exports.
- Searched repository Python callers, state-manager class selections, bootstrap names, and private-manager assignments. No remaining bootstrap declaration/function or replacement private-manager write was found in the decomposed path.
- Read both changed test files completely, the leaf-rerender test, characterization harness/README, I0 findings, relevant inventory sections, and earlier HolderFirstPlan re-review reports as historical evidence only. Historical snapshot files are absent from the reviewed test diff.

Executed exactly the authorized focused command from Pyrolyze:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short tests/test_runtime_context_state_lcm_context_base.py tests/test_runtime_context_state_lcm_slot_expr.py
```

Result: **15 passed in 0.58s**, exit status 0. No other tests, builds, regeneration, file writes, or Git mutations occurred. The lane-owner’s canonical, broader, and full-suite counts were not independently executed.

## 2. Invariant analysis

- **Constructor dispatch:** All active facade construction calls supply keyword inputs. The new keyword-only forwarding path therefore does not strand a positional repository caller. Ordinary subclasses retain their initializer dispatch; decorated subclasses use generated initialization.
- **Multiple inheritance:** The rerunnable path resolves `ContextBaseStateMgr.create` before the shared base implementation, then reaches its existing constructor branch. The permitted tests independently passed manager-identity checks for this path and decorated slot-expression construction.
- **Manager precedence and timing:** Explicit render-state input takes precedence over render-facade resolution. A non-`None` boundary manager replaces a conflicting supplied manager before construction, matching the deleted bootstrap’s precedence. Without a boundary manager, supplied constructor arguments remain intact. The early-factory test observes the injected manager during initialization, not merely afterward.
- **Single generated state:** The construction entry point delegates to `cls(owner=..., **kwargs)`; it creates no additional wrapper and performs no generated-state mutation. The generated constructor installs its manager before field initialization. The discarded per-slot allocation/overwrite mechanism is removed.
- **Existing cohorts:** Render construction still allocates independently, including nested renders. Rerunnable participants receive their render’s manager. Call-site collections retain their own allocation. Nested-render independence passed the focused verification.
- **Compatibility boundaries:** Attachment factories, pass completion/rollback, local-scope checks, callback transfer, resource delivery, and selector defaults are unchanged. Their existing limitations are not repaired or represented as completed migration. Direct constructors remain available; boundary resolution now intentionally requires `create` or explicit injection, as the accepted I1a contract states.

## 3. Risks and next action

The focused run used the established workspace with excluded dirty YIDL present; it is not fresh-checkout reproducibility evidence. Conflicting-manager precedence and direct-constructor explicit injection were source-traced rather than independently exercised by additional tests. Canonical snapshots and broader resource/failure behavior were inspected but not rerun.

The documented I0 failures and pending D4/D5 decisions remain separate obligations. This GO does not certify local-scope repair, explicit attachment, authoritative holders, or runtime routing.

**Next action:** Record Code GO for this exact tuple and I1a scope only. No blocking finding triggers State escalation.
