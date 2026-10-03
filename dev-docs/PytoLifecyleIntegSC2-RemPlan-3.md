# SC2 Localized Follow-Up

Status: **operator-authorized bounded correction; independent closure pending**.
Date: 2026-10-04. Reviewed implementation:
`4d1b9b089333e99cb98381939db311c2b7ce8bde`; process-record HEAD:
`85ee82a8206edc1cacc2901d76896a78862b89bc`. Dependencies remain the pinned
SC2 tuple.

The operator approved a bounded correction and re-review after both round-2
reviewers classified their remaining P2 findings as non-architectural omissions.
This is a third, strictly non-architectural follow-up, not permission to reopen
architecture or widen activation. Any newly identified architectural root stops
the follow-up for operator disposition. No automatic fourth patch.

## Dispositions And Exact Closure

| Finding | Correction | Original-counterexample closure |
| --- | --- | --- |
| Code P2-9 | Reject a duplicate owned render before lifecycle initialization. Check reciprocal installed-child identity at execution/publication entry and before owner UI propagation | Committed and candidate components cannot acquire a competing root. Caught rejection aborts the attempt; installed identity/callback/current UI/generation and published queues remain intact. A first, uninstalled root cannot execute or propagate UI; normal component installation/reuse remains supported |
| State P2-9 | Preflight unseen candidate children before the membership filter, retaining preceding/current retirement checks | Both a directly constructed unseen component and an unseen native leaf containing a component reject retirement, discard component/nested UI, do not advance generation or leave an executable orphan, and permit clean retry |

## Scope And Verification

Use the existing constructor and completion admission boundaries only. Child
attachment also checks the nearest render's reciprocal ownership. A root
with no owner needs no reciprocal child check. Construction may precede child
installation, but execution must not. Preserve retained legitimate nested roots
and legacy unactivated behavior; do not add reachability or resource disposal
requirements. Admission errors poison an existing attempt through its current
reject path, not a second failure mechanism.

The preceding/current retirement inventory remains admission-only. Add unseen
candidate preflight without snapshots, restoration, callbacks, or manager work.

Run both original reproductions red, then their extended narrow cases. Apply
one merged patch, retain the canonical success target unchanged, and run the
focused, full-default, and broader-unactivated gates using committed dependency
exports. Settle the correction before fresh peer-blind Code/State review: the
execution-admission call graph changes even though its contract does not.
Require original-counterexample closure tables for both P2-9 findings and
preservation of all earlier closures. File reports verbatim; acceptance still
requires both GO verdicts on the exact tuple.

## Red And Focused Evidence

The eighteen new fault cases returned **17 failed, 1 passed, 42 deselected in
2.87s** before runtime changes. The passing discarded-owner case was already
rejected by parent-membership admission. Both original failures and the added
execution/propagation paths ran red without mocked manager completion or writes
to generated private state. Initialization instrumentation patches only the
constructor method; callback instrumentation touches only the runtime callback.

The first narrow/canonical green run passed **61 tests in 4.39s**. After
formatting, the seven-file focused gate passed **125 tests in 12.68s**. The
canonical success source/JSON are unchanged. No manager, lifecycle dependency,
resource callback, public selector, or graph activation boundary changed.

Two additional direct slot-construction cases under an uninstalled render ran
red (**2 failed, 60 deselected in 2.30s**) before the same reciprocal guard was
added at the existing constructor seam. This is the Code P2-9 disposition,
not a new authority or architecture. The final narrow fault delta is twenty
cases; the canonical success target remains the sole end-to-end success proof.

## Final Settlement Gates

After the constructor-seam addition and formatting, the final seven-file
focused gate passed **127 tests in 12.79s**. Full default: **917 passed,
13 failed, 20 skipped, 1 warning in 43.96s**. Broader decomposed, unactivated:
**41 passed, 14 failed in 2.10s**. The narrow/canonical review subset passed
**63 tests in 4.46s**. All failures have the same identities as the recorded
SC2 baseline; no waiver or full-green claim. Black and owned-source/path
whitespace checks pass. No source or test changed after these final gates.

Only four runtime modules, the narrow fault test, the controlling SC2 document,
and process evidence are part of the settlement. Unrelated backend documents
and dirty lifecycle/YIDL/parent work remain excluded. Commit the correction,
record its exact SHA, and keep source/tests/HEAD frozen through fresh dual
review. No tag, push, merge, worktree, or parent gitlink update.
