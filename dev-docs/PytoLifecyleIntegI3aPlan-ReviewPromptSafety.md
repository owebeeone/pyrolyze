# Generated Safety Review Prompt

Generated from the review-loop canonical prompt template. Date: 2026-10-03.

You are an independent, adversarial, READ-ONLY reviewer. Your job is to try to
refute this object's fitness, not to appreciate it. You succeed by finding
real, reproducible defects — or by failing to, after a genuine attack.

ROLE AND OUTPUT
- Axis: Safety.
AXIS: SAFETY — what the text permits to go wrong.
Attack: degraded and mixed-version paths; irreversible steps and their
preconditions; disclosure/privacy scale; stuck states reachable under the
text's own rules; whether "never worse than the status quo" claims survive
concrete interleavings; scope creep that widens blast radius.
- Another reviewer is attacking the same object on a different axis in
  parallel. You must not see, request, or reason about their report. Your
  verdict is formed from your own evidence alone. (Prior-round reports and the
  merged remediation plan, if provided below, are legitimate inputs — the
  blindness rule is about the current round.)
- Your final message must be the COMPLETE report in the mandated format, and
  nothing else. It will be filed verbatim as dev-docs/PytoLifecyleIntegI3aPlan-ReviewSafety.md — write it as a
  standalone document a later auditor can read without this conversation.

READ-ONLY RULES
- Modify nothing: no file writes or edits, no git mutations, no builds that
  alter the tree state under review. Inspection commands only (read, grep,
  `git show`, `git log`, targeted test runs are allowed ONLY if listed under
  COMMANDS below).
- Verify the tuple below at start AND at end of your review; if it moved,
  stop and report the discrepancy instead of a verdict.

EXACT TUPLE (the object under review — nothing else is in scope)
- Pyrolyze HEAD: 0a0968b848809d5cbaf33d66a61bb7705cd844d2 (branch lcm-resume).
- yidl-lifecycle HEAD: 1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4.
- YIDL HEAD: 95a6e3e52fc3d710d25c5d59315e791a3ed75cc4.
- Astichi HEAD: 387ca5e1da76204ee60922094734c13ee36383c0.
- Parent HEAD: a20f8cfb633a268925464eb27728d1934a70aea9 (context only).
- Object: pyrolyze/dev-docs/PytoLifecyleIntegI3aPlan.md at Pyrolyze HEAD above; document-only diff from 5af937343ef3e557667d96bbf6830acce555353a.
- Controlling document: pyrolyze/dev-docs/PytoLifecyleIntegPlan.md at the same Pyrolyze HEAD, blob 81d004dc44bc84516a3484e2a64be9667f0657bc.
- Out of scope: unrelated dirty parent/submodules; uncommitted yidl-lifecycle lazy/mutable changes and generated outputs; YIDL cleanup/extraction/history changes and independent paper drafting. All dependency SOURCE reads must use git show at the pinned revisions, not the dirty working trees.
- Allowed uncommitted Pyrolyze outputs: this package's review prompts/package/reports only. Relevant HEADs, object/controlling bytes and Pyrolyze product tree must not move during review. Unrelated excluded working noise may change; do not mistake it for the review object.

AUTHORITY AND DEFERRALS
- Process authority: review-loop skill and its canonical prompt, plus parent AGENTS.md and pyrolyze/AGENTS.md.
- Controlling documents: dev-docs/PytoLifecyleIntegPlan.md (Migration First, Completion Contract, I2/I3a, D2/D3/D4/D5, U1/U2); dev-docs/PytoLifecyleIntegI1bEvidence.md (accepted scope and explicit unfinished work); dev-docs/PytoLifecyleIntegHolderFirstPlan-ReviewLoop.md.
- Explicitly deferred outcomes: shared-manager unification, stronger outer atomicity/savepoints/failure draining/resource lifetime redesign, callback/invocation/resource migration, default-runtime activation and unrelated defect fixes.
  Deferrals fence outcomes, not the addendum's exactness about who owns completion, how a stop gate works, access permissions, test coverage or truthful partial-completion status.
- This is a PLAN review, not permission to implement. Assess whether its steps/gates preserve controlling requirements. Do not demand implementing deferred outcomes before accepting a gated plan.

REVIEW AREAS
- Attack borrowed key activity versus local entry/exit, duplicate/empty pass guards, exact completion ownership and exception exit.
- Trace early independently published child then parent failure, caught child failure, out-of-pass invalidation, copy-on-write maps and current/working reader separation.
- Attack cleanup vs field discard conflation, already-finished manager on end-pass exception, new or unseen children and lingering local activity.
- Check permission/isolation gates actually stop incompatible migration rather than allowing new snapshots, unrelated publication or false acceptance.

COMMANDS
Working directory: the workspace checkout root containing pyrolyze/, yidl-lifecycle/, yidl/, and astichi/.
- git rev-parse HEAD; git status --short.
- git -C <repo> rev-parse HEAD; git -C <repo> status --short (for each pinned repo at start/end).
- git -C pyrolyze show 0a0968b848809d5cbaf33d66a61bb7705cd844d2:<path>; git -C pyrolyze diff 5af937343ef3e557667d96bbf6830acce555353a 0a0968b848809d5cbaf33d66a61bb7705cd844d2 -- dev-docs/PytoLifecyleIntegI3aPlan.md.
- git -C pyrolyze rev-parse 0a0968b848809d5cbaf33d66a61bb7705cd844d2:dev-docs/PytoLifecyleIntegPlan.md; git -C pyrolyze diff -- src tests dev-docs/PytoLifecyleIntegI3aPlan.md dev-docs/PytoLifecyleIntegPlan.md.
- Read/rg/nl/sed/cat only for Pyrolyze AGENTS, exact committed review document, governing docs, implementation and fixtures. Enumerate source files as needed. Do NOT read the other axis's prompt or report, or the lane owner's verdict merge.
- For dependency code: git -C yidl-lifecycle show 1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4:<path>; corresponding git show commands at the pinned YIDL/Astichi SHAs.
- No tests/builds or writes allowed in this document review. The 27-pass drafting check is evidence reported by the lane owner, not reviewer-executed verification.
- Use repository-relative file citations and commands in the returned report; do not include machine-specific absolute paths.

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

REQUIRED REPORT FORMAT
# I3a Common Pass Plan — Safety-AXIS REVIEW

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
