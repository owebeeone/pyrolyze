# Consistency Re-Verdict Prompt 1

Canonical original prompt plus the review-loop focused re-verdict requirements.

You are an independent, adversarial, READ-ONLY reviewer. Your job is to try to
refute this object's fitness, not to appreciate it. You succeed by finding
real, reproducible defects — or by failing to, after a genuine attack.

ROLE AND OUTPUT
- Axis: Consistency
AXIS: CONSISTENCY — the document against its controlling graph.
Attack: internal contradictions between sections; agreement with every
controlling contract/design it cites (verify quotes verbatim at the cited
lines); exactness of superseded-clause lists; whether its own test/evidence
sections are satisfiable as written; unstated impacts on documents it does
not cite.
- Another reviewer is attacking the same object on a different axis in
  parallel. You must not see, request, or reason about their report. Your
  verdict is formed from your own evidence alone. (Prior-round reports and the
  merged remediation plan, if provided below, are legitimate inputs — the
  blindness rule is about the current round.)
- Your final message must be the COMPLETE report in the mandated format, and
  nothing else. It will be filed verbatim as dev-docs/PytoLifecyleIntegCompletionPlan-ReviewConsistency-1.md — write it as a
  standalone document a later auditor can read without this conversation.

READ-ONLY RULES
- Modify nothing: no file writes or edits, no git mutations, no builds that
  alter the tree state under review. Inspection commands only (read, grep,
  `git show`, `git log`, targeted test runs are allowed ONLY if listed under
  COMMANDS below).
- Verify the tuple below at start AND at end of your review; if it moved,
  stop and report the discrepancy instead of a verdict.

EXACT TUPLE (the object under review — nothing else is in scope)
- Pyrolyze: b0019be76927795eceb085379c3ea4f8fde4c85c (branch lcm-resume).
- yidl-lifecycle: cdf08544deea846bca4fa7e0c468ebee8d41e138 (clean dependency).
- YIDL: 95a6e3e52fc3d710d25c5d59315e791a3ed75cc4 (committed dependency view only; unrelated dirty cleanup/docs moves excluded).
- Astichi: 387ca5e1da76204ee60922094734c13ee36383c0 (clean dependency).
- Parent checkout: a20f8cfb633a268925464eb27728d1934a70aea9 (context only; dirty pointers and other workspace changes excluded).
- Object: Pyrolyze dev-docs/PytoLifecyleIntegPlan.md and newly committed I0 evidence at b0019be76927795eceb085379c3ea4f8fde4c85c; implementation source is capability/baseline evidence, not a proposed runtime patch.
- Controlling DRAFT document: Pyrolyze dev-docs/PytoLifecyleIntegPlan.md at b0019be76927795eceb085379c3ea4f8fde4c85c.
- Out of scope: all runtime implementation changes, switching defaults, unrelated workspace changes, dirty YIDL bytes, and the other axis's current re-verdict. Initial reports and the merged remediation plan are legitimate inputs. Only lane-owner review package/prompt/report/ledger documents may appear untracked while reviewers run.

AUTHORITY AND DEFERRALS
- Process authority: the operator's review-loop skill and canonical reviewer prompt template, plus committed workspace/submodule AGENTS.md instructions. This is a dual draft-stage document gate.
- Controlling documents: Pyrolyze AGENTS.md; dev-docs/ContextLifecyleMetaprogrammingPlan.md; dev-docs/LifecyleAdoptionPatterns.md; dev-docs/PytoLifecyleIntegI0Findings.md; dev-docs/PytoLifecyleIntegI0Inventory.md; tests/data/lcm_integration/README.md. Check the lifecycle capability claims against committed yidl-lifecycle source and dev-docs/YidlTransactionalYidlPhaseF-1Plan.md, with relevant Phase B/G/H documents if needed.
- Explicitly deferred OUTCOMES: operator selection of D1-D5, the concrete child-containment mechanism if a new generic facility is required, runtime implementation, runtime activation, and unrelated host fixes. Pending decisions alone are not plan defects when dependent work is accurately gated. Their shape, affected checkpoints, test obligations, and consistency ARE in scope. GO here accepts this plan only, not runtime execution or any semantic policy.
- Preserve historical baseline observations; the plan expressly supersedes the old I0 blanket-abort recommendation. Do not mistake superseded recommendations for observations or approved policy.

REVIEW AREAS
- Trace internal coherence of child failure-containment rules, D1-D5 gates, boundary orchestration, I0/L0/I1-I8 dependencies, commit/tag exit conditions, and the replacement/deletion ledger.
- Compare proposed constructor and facade shapes against actual harvested/generated capabilities and current consumer call sites. Verify ordinary subclass initialization, shared-TM injection, local scope lifetime, inherited fields, and field/resource ownership boundaries.
- Check agreement with cited adoption and lifecycle documents; distinguish intended future behavior, established capabilities, and historical observations. Look for unamended clauses or checkpoints that permit activation before their prerequisites.
- Check that canonical tests and verification commands can express the promised success/failure/recovery evidence without silently changing reference semantics, duplicating success tests, or implying passing baseline tests prove integration readiness.

COMMANDS
Expected working directory: workspace root; use each owning repository's relative directory.
- git -C <repo> rev-parse HEAD; git -C <repo> status --short at start AND end. <repo> is pyrolyze, yidl-lifecycle, yidl, or astichi; parent is git rev-parse HEAD.
- git -C <repo> show <listed-sha>:<repo-relative-path> is the authority for every reviewed byte; use committed views even if a dependency is dirty.
- Read-only inspection: rg, rg --files, sed, nl, cat, git log/show/diff. For tracked files read through the exact committed tuple (live reads are acceptable only after confirming the file is identical to that committed view).
- No tests, imports, builds, regeneration, writes, commits, tags, or other mutations in this review. The lane owner reran the four I0 characterization tests: 4 passed in 1.58s; this is narrow evidence only, not a full-suite claim.
- Review files are lane-owner-owned outputs. Do not open the other axis's prompt/report or any current verdict. Return your complete report; do not create it yourself.
- In your report use paths relative to the repository owning each file, with line references. Do not include machine-specific absolute filesystem paths. Identify new architectural root causes explicitly, if any.

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

MANDATED REPORT TEMPLATE
# Lifecycle Integration Completion Plan — Consistency-AXIS REVIEW

**Review object:** Pyrolyze dev-docs/PytoLifecyleIntegPlan.md at b0019be76927795eceb085379c3ea4f8fde4c85c; DRAFT plan; 2026-10-03
**Baseline:** {per-repo SHAs; note how sources were read, e.g. `git show HEAD:`}
**Date:** 2026-10-03
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

FOCUSED RE-VERDICT: REMEDIATION ROUND 1
You are the ORIGINAL Consistency reviewer, with context retained. Review the corrected document at b0019be76927795eceb085379c3ea4f8fde4c85c; the prior reviewed Pyrolyze revision was 723460d6c1dce75b70f03e355daf20c248bde8ad. Other repository revisions remain unchanged. Read the committed merged plan dev-docs/PytoLifecyleIntegCompletionPlan-RemPlan-1.md and trace your ORIGINAL counterexample, not just the claimed fix. The initial Consistency and Safety reports are now filed and legitimate prior-round inputs. Do not read the other current re-verdict or its prompt.

Inspect git -C pyrolyze diff 723460d6c1dce75b70f03e355daf20c248bde8ad b0019be76927795eceb085379c3ea4f8fde4c85c -- dev-docs/PytoLifecyleIntegPlan.md and the committed remediation/report/ledger documents. Only two corrections are in scope: candidate-view callback staging and explicit per-generated-hook/per-domain-action draining obligations under the existing Phase F-1 contract. No runtime source or D1-D5 outcome changed. Lane-owner documentation gate checks passed (two Python sketches AST-parse; source diff/path checks); the required generated/runtime regressions are future implementation obligations, not newly claimed passing tests.

Before Evidence base, include:
## Prior-finding closure table
| ID | Disposition claimed | Original counterexample verified on corrected tree | Status |
One row for your original P2-1. You alone verify closure; do not transfer the other axis's conclusion.
## Changed-range analysis
List actual changed intent, any change outside the two dispositions, and explicitly label any NEW ARCHITECTURAL ROOT CAUSE. Safety previously classified one architectural root cause; no implementer can override reviewer classification. Also state whether the text clarification changes a shared interface, ownership/mutation boundary, or architecture enough to require fresh dual reviewers. If so, report that instead of transferring an old proof to a new boundary.

Return the complete standalone report and GO/NO-GO, not a patch or status note. Do not modify anything. Verify the exact tuple at start and end. This is a plan-only gate, never execution authorization.
