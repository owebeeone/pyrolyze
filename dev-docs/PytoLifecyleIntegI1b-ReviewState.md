# I1b Construction Checkpoint — STATE-AXIS REVIEW

**Review object:** Pyrolyze I1b at `7676cc975cb72c6dcb97a29e13f7a41838864312`, diff from `6af59c9`. Interior construction checkpoint, reviewed on 2026-10-03. Controlling DRAFT: `dev-docs/PytoLifecyleIntegPlan.md`, accepted blob `81d004dc44bc84516a3484e2a64be9667f0657bc`, unchanged.
**Baseline:**
- Pyrolyze: `7676cc975cb72c6dcb97a29e13f7a41838864312`.
- yidl-lifecycle: `cdf08544deea846bca4fa7e0c468ebee8d41e138`.
- YIDL: `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`, committed view only.
- Astichi: `387ca5e1da76204ee60922094734c13ee36383c0`.
- Parent workspace: `a20f8cfb633a268925464eb27728d1934a70aea9`, context only.

Sources were inspected using pinned `git show`, the permitted diff, and clean source reads. Excluded dirty YIDL/parent changes were not review inputs.
**Date:** 2026-10-03
**Axis:** State: construction legality, failure ordering, manager ownership, registration, and recovery compatibility. Independent, adversarial, read-only. This is the recorded single-axis interior gate; no current-round counterpart report is an input. Filed verbatim by the lane owner.

**Verdict: GO** — zero P0/P1/P2/P3 findings. This accepts I1b construction only, not completed I3a, manager unification, or activation.

---

## 0. Evidence base

Paths below are relative to their owning repository.

- Verified all five HEADs and inspected statuses at start and end. Every HEAD matched the supplied tuple. Pyrolyze contained only the authorized untracked State prompt; lifecycle and Astichi were clean. Excluded YIDL/parent status listings were unchanged.
- Read applicable `AGENTS.md` instructions, the review-loop skill, and its canonical reviewer template. No current-round counterpart prompt or report was read.
- Inspected the permitted source/test/evidence diff. Read `dev-docs/PytoLifecyleIntegI1bEvidence.md:1–120`; the plan’s Architecture Contract, Construction And Initialization, I1, and I3 sections; I1a evidence/report; and I0 findings/inventory as historical debt evidence.
- Compared complete committed plan text with the accepted blob: identical. Compared all six historical characterization JSON files between `6af59c9` and the reviewed revision: identical.
- Traced `context_state_lcm/_base.py:23–94`, `slot_context.py:11–53`, `rerunnable_slot_context.py:1–8`, `context_base.py:45–355`, `render_context.py:23–80`, and ordinary derived initializers.
- Examined `component_call_slot_context.py:28–61,104–114`, `slot_expr_slot_context.py:13–104`, `slot_call_slot_context.py:22–32`, `container_slot_context.py:6–10`, and retained event/leaf initialization.
- Audited facade construction in `context_bare_refactor_lcm.py:63–104,326–381,415–492,927–947`, repository constructor references, and independent call-site allocation in `call_site_context.py:146–157`.
- Read lifecycle generation/harvesting: `lifecycle.py:34–64`, `lifecycle_harvester.py:54–147,540–595`, and `yidl/lifecycle_core.yidl:261–290,354–443,530–659`; inspected local-store generation and committed YIDL exports.
- Read the construction fixture/golden, three failure cases, characterization harness/README, and all five authorized test files.

Executed exactly the authorized focused command from Pyrolyze:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short tests/test_runtime_context_state_lcm_construction.py tests/test_runtime_context_state_lcm_context_base.py tests/test_runtime_context_state_lcm_slot_expr.py tests/test_runtime_context_state_lcm_leaf_rerender.py tests/test_lcm_integration_characterization.py
```

Result: **27 passed in 3.15s**, exit status 0. No other tests, builds, regeneration, file edits, or Git mutations were performed. Lane-owner broader/full counts were not independently executed.

## 2. Invariant analysis

- **Initialization before exposure:** `create` calls the concrete constructor before attachment. Ordinary and rerunnable derived initializers remain dispatched; decorated descendants receive generated initialization. All three late-failure cases passed without registration. No attachment factory remains in the active target path.
- **Single backing state:** Common inputs are inherited initvars; stored fields are generated once. Removing the handwritten common initializer avoids a second initialization path. The rerunnable MRO reaches the existing generated context initializer without separately decorating the slot branch.
- **Manager identity and precedence:** Boundary resolution occurs before constructor execution. A present render manager takes precedence over a supplied conflicting manager; otherwise explicit injection/default allocation remains available. Generated initialization installs the selected manager before factories. Nested renders and call-site collections retain independent completion owners.
- **Registration ordering:** Successful construction attaches once, root before parent. Failure during the second registration can still leave the first registration present; that is the explicitly retained two-step policy, not a new atomicity guarantee. The changed code adds no filesystem persistence or restart format.
- **Roots and callers:** Render roots inherit neutral parent/slot inputs but do not traverse slot attachment. Active graph-owning facades use `create` and supply their graph identities. Direct constructors remain detached, as the new golden verifies.
- **Compatibility:** The golden passed mixed identity-write policies across seven state types. Dirty/seen remain plain nontransactional fields; site metadata remains local-store storage. Pass snapshots, publication/resource algorithms, and runtime selection were not changed. Historical failure/recovery characterizations passed against unchanged snapshots.

## 3. Risks and next action

The focused run used the established workspace with excluded dirty YIDL present; it is not fresh-checkout reproducibility evidence. Attachment-call exceptions and concurrent registration were source-traced, not independently fault-injected. This review establishes no stronger graph-wide rollback, locking, or durability guarantee.

Known I0 defects and deferred local-scope, holder, resource, D4/D5, unification, and routing work remain outside this acceptance.

**Next action:** Record State GO for this exact tuple and I1b scope only. No blocking finding or reviewer request triggers fresh Code escalation.
