# SC3-L0 Merged Document Remediation 1

Status: **DRAFT corrections; reviewer verification pending**.
Date: 2026-10-04. Reviewed draft:
`2dc64f19542180e9c68f58073eeb484e1b9a2ed0`. Dependency revisions remain the
exact tuple in the review ledger; no runtime, tests, or library files change.

Both complete reports are filed verbatim as
`PytoLifecyleIntegSC3-L0Plan-ReviewConsistency.md` and
`PytoLifecyleIntegSC3-L0Plan-ReviewSafety.md`. Both independently found the
same preparation-write defect. Distinguish axis-qualified IDs below because
each report has its own severity numbering.

## Dispositions And Closure Obligations

| Finding | One Disposition | Closure Obligation |
| --- | --- | --- |
| Consistency P2-1 / Safety P2-1 | Correct the shared preparation-write root with a manager-owned before-hook window and target preparation boundary, enforced through generated transactional writers even for an existing overlay; specify retained-alias restrictions | Trace A-before-B, B changing A's staged field and untouched field. Both reject before working mutation or application, discard both, drain eligible after actions, and preserve contextual evidence. Planned complete-decorator golden also retains valid self-staging and later-unprepared-target staging |
| Consistency P2-2 | Pin entered/unentered phase flags and replace ambiguous prose outcomes with disjoint evidence predicates, after authority/finalization checks | Trace successful empty commit, empty rollback, and pre-application abort. Only empty commit is publication-complete and commits generation; the other two discard and roll generation back. Missing evidence, partial publication, and incomplete cleanup cannot certify reuse |
| Consistency P2-3 | Add the exact historical Phase F-1 supersession table and precedence pointers in both controlling integration documents, plus explicit callback/error traces | Trace two potential preparation failures (only the first occurs), failed application, and failed discard. Each has exactly one controlling attempt/eligibility policy; no blanket Phase F-1 implementation or D5 acceptance follows |
| Consistency P3-1 | Correct the ownership map to include the effective managed-layer hook helpers/contributions and full-decorator regeneration obligations | Follow matcher overrides to effective helper calls, not only core resources. The planned inherited/local golden must show one wrapper per effective independent after hook |

All findings remain open pending reviewer verification. Source-traced document
closure is not execution or an implementation regression-test result.

## One Bounded Patch

The object patch changes `PytoLifecyleIntegSC3-L0Plan.md` and only the necessary
precedence pointers in `PytoLifecyleIntegPlan.md` and
`PytoLifecyleIntegSingleCohortPlan.md`. The SC3 audit, accepted runtime/test
bytes, library/compiler revisions, and resource admission gates are unchanged.

The candidate-write correction refines a mutation boundary and identifies
additional generated writer enforcement. Therefore the corrected committed
tuple receives fresh dual Consistency/Safety review under the skill's
material-change rule. The originating reviewers also re-trace their original
counterexamples; the drafter does not close them. Current-round fresh peer
reports are withheld until both finish. Original reports and this merged
remediation are legitimate prior-round inputs.

This is the first merged remediation, not an extra completed round for the
canceled dispatch. Reviewers classify any new architectural roots against
the recorded cap; the lane owner does not waive that stop rule.

## Verification And Scope

Check document whitespace, report fidelity, repository-relative paths, unchanged
source/test bytes, and all tuple HEADs before dispatch. No tests/builds are
needed or claimed for this document-only correction. The previous focused
127-pass evidence and separate full/broader debt remain historical evidence.

Design GO would approve the bounded library design, including exactly the
listed D4 differences and write boundary. It would not accept implementation,
private consumer adoption, resource delivery order, routing activation, or
snapshot deletion. Existing dirty lazy/mutable YIDL/generated artifacts remain
excluded; implementation must resolve their checkpoint boundary explicitly.
