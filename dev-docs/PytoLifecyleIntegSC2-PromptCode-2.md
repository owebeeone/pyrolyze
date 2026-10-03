You are an independent, adversarial, READ-ONLY reviewer. Your job is to try to
refute this object's fitness, not to appreciate it. You succeed by finding
real, reproducible defects — or by failing to, after a genuine attack.

ROLE AND OUTPUT
- Axis: Code
- Another reviewer is attacking the same object on a different axis in
  parallel. You must not see, request, or reason about their report. Your
  verdict is formed from your own evidence alone. (Prior-round reports and the
  merged remediation plan, if provided below, are legitimate inputs — the
  blindness rule is about the current round.)
- Your final message must be the COMPLETE report in the mandated format, and
  nothing else. It will be filed verbatim as dev-docs/PytoLifecyleIntegSC2-ReviewCode-2.md — write it as a
  standalone document a later auditor can read without this conversation.

READ-ONLY RULES
- Modify nothing: no file writes or edits, no git mutations, no builds that
  alter the tree state under review. Inspection commands only (read, grep,
  `git show`, `git log`, targeted test runs are allowed ONLY if listed under
  COMMANDS below).
- Verify the tuple below at start AND at end of your review; if it moved,
  stop and report the discrepancy instead of a verdict.

EXACT TUPLE (the object under review — nothing else is in scope)
- Pyrolyze HEAD: 4d1b9b089333e99cb98381939db311c2b7ce8bde (round 1 ca731d89a0086e0bff48dc426d1b5b1472aba869; initial SC2 53c41674f43ab97401ac9b30a79575c19ab5dca9; SC2 base 1b246d47e934835a4871fbbfc651fae78440b913).
- yidl-lifecycle HEAD: 335d2795cdd65b2542e0ac9ec70b7f16ee0b1901.
- YIDL HEAD: 95a6e3e52fc3d710d25c5d59315e791a3ed75cc4.
- Astichi HEAD: 387ca5e1da76204ee60922094734c13ee36383c0.
- Parent context only: a20f8cfb633a268925464eb27728d1934a70aea9.
- Object: SC2 remediation round 2, diff ca731d89..4d1b9b089333e99cb98381939db311c2b7ce8bde, cumulative SC2 1b246d47..4d1b9b089333e99cb98381939db311c2b7ce8bde.
- Controlling DRAFT document: dev-docs/PytoLifecyleIntegSC2.md at 4d1b9b089333e99cb98381939db311c2b7ce8bde
- Out of scope: Untracked dev-docs/RenderingBackendBugList.md and RenderingBackendDiscussionReport.md; dirty lifecycle lazy/static/mutable work; dirty YIDL extraction/paper/docs; parent gitlinks and other submodules. Use pinned dependency git show or clean committed exports only. Process-only review artifacts may appear/change; no source/test or HEAD changes while reviewing.

AUTHORITY AND DEFERRALS
- Process authority: Parent and Pyrolyze AGENTS.md; review-loop skill and its canonical prompt template supplied at dispatch. Fresh dual review because admission and cache/scheduler reconciliation call graphs changed.
- Controlling documents to check the object against: dev-docs/PytoLifecyleIntegSC2.md; PytoLifecyleIntegSingleCohortPlan.md as privately refined; accepted SC1 contract/evidence in PytoLifecyleIntegSC1-Remediation.md and PytoLifecyleIntegSC1-ReviewLoop.md. Both initial reports PytoLifecyleIntegSC2-ReviewCode.md and PytoLifecyleIntegSC2-ReviewState.md, both round-1 reports PytoLifecyleIntegSC2-ReviewCode-1.md and PytoLifecyleIntegSC2-ReviewState-1.md, both RemPlan-1.md/RemPlan-2.md, and ReviewLoop.md are legitimate common inputs.
- Explicitly deferred (do not report as findings): Broad/default activation, SC3 resource/notification adapters, component replacement/retirement, external containers/keyed loops/bindings/event callbacks/authored overrides, SC4 dirty/site metadata migration/snapshot removal, manager redesign/cross-key atomicity, recorded baseline debt. The private gate MUST reject deferred routes before side effects. Do not relitigate the operator-approved private field-only proof boundary.
  Deferrals cover a decision's OUTCOME only. Its shape — the verb it lives
  under, its name, whether its lifecycle pair is complete, its defaults — is
  always in scope.

REVIEW AREAS
AXIS: CODE — architecture, interfaces, call graphs, and compatibility reality.
Attack: interface contracts vs. actual call sites; ownership and visibility;
API/wire compatibility with retained readers and older writers; error paths
and hidden panic/allocation paths; whether the diff does what its DRAFT doc
claims and nothing it forbids.

- Audit constructor admission from both parent and render, occupied current/candidate/cache IDs, nearest-root ownership, and reject-before-init/attach call graph in _base.py.
- Candidate writers vs published readers in slot_context.py/context_base.py; deactivation sibling preservation.
- Retirement preflight for preceding candidate AND committed component descendants; legitimate repeat-pass reuse must still work.
- Track publication-only and registry-only nested roots; reconcile clean current caches and cancel unpublished orphan scheduler work without resource callbacks or changing published queues.
- Trace execution claims and completion call graph under native/publication/direct/no-op entry; preserve unchanged legacy mixed-resource routes.
- Verify original Code P2-1..7 and the merged State dispositions (initial P2-1..5, round-1 P2-5 incomplete and P2-6..8). Attack the cumulative diff against the controlling private boundary.

COMMANDS
Read-only git rev-parse/status/show/diff/log, rg/sed/nl/cat. Verify all five HEADs at start and end. Read dependencies with pinned git show or clean exports supplied ephemerally. No writes/builds/bytecode/cache/git mutations.
From Pyrolyze root with existing Python 3.12 and committed exports:
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="src:$snapshot/yidl-lifecycle/src:$snapshot/yidl/src:$snapshot/astichi/src" "$PYTHON" -m pytest -p no:cacheprovider -q --tb=short tests/test_runtime_context_state_lcm_field_only_render.py tests/test_lcm_integration_characterization.py::test_common_pass_single_cohort_golden
In-memory probes under those sources allowed, with no generated-private-state writes or mocked manager completion. No reading the OTHER CURRENT-round prompt/report (-2 suffix).
Owner evidence: focused107 passed in14.12s; full897 passed/13 unchanged failures/20 skipped/1warning in43.45s; broader unactivated41 passed/14 unchanged failures in2.23s. Not an all-green claim. Dependencies and SC1 kernel unchanged. Re-run/re-trace original counterexamples; a green test list alone does not close them.

SEVERITY AND VERDICT CONTRACT
- Findings use IDs P0-n / P1-n / P2-n / P3-n:
  P0 = active corruption, data loss, credential exposure, or false composition.
  P1 = likely destructive or unrecoverable release blocker.
  P2 = concrete correctness, recovery, compatibility, parity, or
       diagnosability defect.
  P3 = bounded robustness, coverage, maintainability, or documentation defect
       with a concrete consequence.
- Verdict is GO or NO-GO. NO-GO while any P0, P1, or P2 is open.
- Each finding: ONE root cause, exact location, violated invariant, credible
  reproduction or state/interleaving sequence, impact, required correction,
  and a closure/regression test. Separate independent root causes.
- Style preferences and speculative unease are not defects. Do not pad.
  Interface shape is not style: wrong command placement, a misleading name,
  a missing half of a lifecycle pair, or an option without a default is a
  finding (P2 or P3), on every axis.
- If your verdict is NO-GO but every blocking finding has a bounded,
  text-or-code-fixable remedy, you may pre-commit: "I pre-commit to GO on a
  revision that resolves {IDs} as specified." This makes the re-verdict cheap
  and is encouraged when honest.


MANDATED REPORT FORMAT
# {OBJECT} — {AXIS}-AXIS REVIEW

**Review object:** {object at exact SHA / doc path + status + date}
**Baseline:** {per-repo SHAs; note how sources were read, e.g. `git show HEAD:`}
**Date:** {date}
**Axis:** {one line: mandate}. Independent, adversarial, read-only. The other
axis runs in parallel; nothing here relies on it. Filed verbatim by the lane
owner.

**Verdict: {GO | NO-GO}** — {counts, e.g. "two P1 and three P2 findings
block"}. {If NO-GO and honest: pre-commit-to-GO clause naming the finding IDs.}

---

## 0. Evidence base
{What was actually read/run: files with line ranges, documents with sections,
commands with results. This section is what makes the verdict auditable.}

## 1. Findings
### [P1-1] {one-line root-cause title}
{Location · violated invariant · reproduction or state sequence · impact ·
remedy · closure test.}
{… one subsection per finding, severity-ordered. Omit section if none.}

## 2. Invariant analysis
{The invariants attacked and the evidence they held — attacks that FAILED are
part of the result; they are what a GO rests on.}

## 3. Risks and next action
{Residual risks below the finding bar; the single next action this verdict
implies.}


REQUIRED REMEDIATION REPORT SECTIONS (ahead of section0)
## Prior-finding closure table
| ID | Disposition claimed | Verified on corrected tree | Status |
{One row per prior finding. "Verified" means the ORIGINAL counterexample was
re-run/re-traced on the new tuple — a claim of fixing is not closure.}

## Changed-range analysis
{What actually changed since the reviewed revision, and whether any change
falls outside the dispositions — new-root-cause candidates go here, and NEW
ARCHITECTURAL root causes must be labeled as such: the two-round cap turns on
that classification, and it is the reviewer's call, not the implementer's.}


Remediation count: two implemented, zero accepted. Round 1 classified its residual findings as localized non-architectural omissions; the original SC2 execution-ownership root remains recorded. Reviewers, not the implementer, classify NEW ARCHITECTURAL roots. This is the final authorized bounded remediation; no third architectural patch is authorized. Report remaining concrete defects honestly; do not lower the bar for a cap.

