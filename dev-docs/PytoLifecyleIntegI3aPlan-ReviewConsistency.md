# I3a Common Pass Plan — Consistency-AXIS REVIEW

**Review object:** Pyrolyze `0a0968b848809d5cbaf33d66a61bb7705cd844d2`, `dev-docs/PytoLifecyleIntegI3aPlan.md`, lines 1–232. DRAFT, plan-only checkpoint, reviewed 2026-10-03.

**Baseline:**
- Pyrolyze: `0a0968b848809d5cbaf33d66a61bb7705cd844d2`.
- yidl-lifecycle: `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`.
- YIDL: `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`.
- Astichi: `387ca5e1da76204ee60922094734c13ee36383c0`.
- Parent, context only: `a20f8cfb633a268925464eb27728d1934a70aea9`.
- Product and dependency sources were read through `git show` at these pinned revisions; excluded dirty dependency contents were not used.

**Date:** 2026-10-03.

**Axis:** Consistency: internal agreement, conformance to controlling contracts, completion ownership, deletion sequencing, and evidence satisfiability. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero P0, P1, P2, or P3 findings. This accepts the gated plan’s consistency, not implementation feasibility, implementation authorization, or I3a completion.

---

## 0. Evidence base

The review restarted under the corrected canonical prompt. No earlier verdict was carried forward.

Commands executed:
- `git rev-parse HEAD` and `git status --short`, plus both commands with `git -C <repo>` for all four pinned repositories, at restart and completion. Every HEAD matched the required tuple at both ends.
- `git -C pyrolyze rev-parse 0a0968b848809d5cbaf33d66a61bb7705cd844d2:dev-docs/PytoLifecyleIntegPlan.md` returned `81d004dc44bc84516a3484e2a64be9667f0657bc` at both ends.
- The permitted product-tree diff was empty at both ends. Pyrolyze’s untracked files were limited to the review package and prompts. Excluded dirty status listings were unchanged; Astichi was clean.
- The permitted baseline-to-object document diff identifies a new, 232-line addendum.
- Inspection used `git show`, `cat`, `rg`, `nl`, and `sed`. No tests, builds, writes, or Git mutations were performed.

Read evidence, with Pyrolyze paths relative to its repository:
- Parent `AGENTS.md` and Pyrolyze `AGENTS.md`; the complete addendum.
- `dev-docs/PytoLifecyleIntegPlan.md`: Migration First, Completion Contract, scope/ownership semantics, deletion ledger, I2/I3a, dependent resource checkpoints, U1/U2, testing, and D2–D5 decisions.
- `dev-docs/PytoLifecyleIntegI1bEvidence.md:1–146`; `dev-docs/PytoLifecyleIntegHolderFirstPlan-ReviewLoop.md:1–69`; selected I0 findings at lines 78–138, 173–217, and 241–287.
- `src/pyrolyze/runtime/context_state_lcm/`: `_base.py:1–118`, `context_base.py:1–676`, `slot_context.py:1–53`, `render_context.py:1–340`, `_support.py:396–505`, and relevant leaf, rerunnable, container, component-call, slot-call, directive, and override declarations and methods.
- `src/pyrolyze/runtime/context_bare_refactor_lcm.py:96–210,325–415,550–595,870–1035`; original-runtime construction, metadata writers, pass handling, UI assembly, and scope handles; `src/pyrolyze/runtime/context.py:1–50`.
- `tests/test_lcm_integration_characterization.py:1–58`, `tests/data/lcm_integration/characterize.py:1–244`, fixture README and construction fixture; original/decomposed parent-failure snapshots; existing context-base and leaf-rerender tests.
- At the lifecycle pin: `src/yidl_lifecycle/transaction_yidl.py:1–360`, lifecycle decorator code, and targeted core/managed YIDL templates covering facade selection, write permission, enlistment, and completion.

The reported 27-pass drafting run was not reproduced. Its explicit dependence on dirty libraries prevents treating it as verification of the committed tuple. No peer prompt, peer report, or current verdict merge was read.

## 2. Invariant analysis

1. **Authority and accepted scope held.** Addendum lines 5–19 and 210–213 do not promote I1b construction acceptance into publication acceptance. They agree with I1b evidence lines 50–62 and 100–126. The controlling blob matches the holder-first acceptance record. The addendum supersedes no controlling clauses.

2. **Shared-key completion was challenged.** The pinned manager’s nested commit reduces depth, while rollback completes the whole enlisted key. Addendum lines 106–135 accurately acknowledge this limitation. Borrower exit is not presented as discard, and unsupported isolation requires a bounded decision before changing the path. This conforms to controlling-plan lines 280–312 and 826–853; it does not silently authorize savepoints or new cohorts.

3. **Local activity and visibility held as separate obligations.** Original local entry and scoped re-entry support the proposed distinction. The pinned managed default facade can return working values, so the explicit current-reader audit is necessary. Lines 67–79 also protect `publish_write_scope` from accidentally completing a key merely because local activity becomes false. Visitation remains separately reset rather than tied to transaction completion.

4. **Dirty and metadata permissions were not assumed solved.** The owner setters and invalidation traversal contain writes outside local passes; metadata is currently nontransactional and eagerly assigned. The addendum requires writer/cohort and visibility probes before conversion. Its semantic-change stop rule prevents the target classification from silently authorizing changed failure behavior.

5. **Deletion and resource sequencing held.** Snapshot removal is conditional on compatible replacement, not merely decorator installation. Mixed resource dispatch remains until its category migrates. Constructor identities, attachment order, and competing slotted-MI restrictions remain intact. Post-publication failures are distinguished from discardable candidates without assuming pending D4 draining behavior.

6. **Evidence requirements remained coherent.** Historical snapshots distinguish original early-child publication from decomposed-path debt. The new fixture must observe current/candidate separation and actual completion ownership; unrelated output equality is not required. Unsupported recovery blocks completion rather than licensing baseline regeneration or a false partial-completion label.

## 3. Risks and next action

The writer/cohort probes may establish that some dirty, metadata, or borrowed-failure paths cannot migrate using the existing API. GO does not predict their resolution. Existing full-suite debt, resource side effects, and fail-fast lifecycle completion also remain outside any implementation certification.

**Next action:** accept this gated planning revision only; obtain separate implementation authorization before executing its mandatory dependency and writer/cohort preflight.
