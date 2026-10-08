# Invocation Value Migration

Status: **bounded I3c leaf checkpoint accepted after Code/State GO/GO** at
`b188301216486aee3b43c1ecc7b7fe89307d0273`, not runtime activation or completion
of all I3c work. Read the single-cohort amendment before the older I3/I3c clauses.
The operator requested implementation review rather than another design loop.

## Leaf Checkpoint

The source audit corrects the old I0 inventory: leaf arguments are currently
written **before** execution, and leaf calls have no unchanged-call elision.
Elision belongs to slot-call evaluation, whose binding/resource route remains
gated. Do not add leaf elision or admit slot-call resources in this checkpoint.

- Replace the leaf's initializer-only argument stores with one frozen argument
  record declared as `managed(init=False, compare="identity", tx_key=PASS_TX_KEY)`.
  The pair publishes/discards together; its tuple containers are not a deep
  freeze of objects supplied by the caller.
- Stage the private route's record after local pass entry, before calling the
  leaf. Normalize keywords inside the original attempt, then recheck that
  captured authority immediately before assigning the candidate.
- Private public `last_args`/`last_kwargs` read current accepted arguments;
  internal execution may read the candidate. Local success does not publish.
  Caught child failure and parent failure discard through the outer owner.
- Ordinary `invoke` still returns the callable result and does not introduce
  UI/local-pass resets. Its private route joins/starts the outer attempt.
- Keep one explicitly named `local_store` argument record for the unactivated
  compatibility route. That route continues reporting the last attempted
  arguments, including failed calls. It is not a snapshot/restore authority
  for the private route and is never written there. Delete this adapter only
  when that route's completion ownership migrates. Preserve the reference's
  sequential positional/keyword tracking if keyword normalization fails.
- No identity/schema/site/loop/container or resource holder migration is claimed
  by this checkpoint. Component invocation already has a managed call record;
  replacement/retirement policy remains gated. Slot-call invocation values and
  elision must migrate with the corresponding approved binding adapter, not by
  pretending a managed reference makes the referent transactional.

## Verification And Review

Extend the existing subprocess/JSON canonical harness with a separately named
`invocation_values_lifecycle.py` target. Preserve historical JSON. Cover paired
current/candidate reads, keyword ordering, local success followed by parent
failure, caught child failure, fresh retry, repeated identical leaf execution,
plain invocation returns, standalone private completion, and unactivated
last-attempt compatibility. Include declaration/manager identity and shallow
argument retention in that canonical proof, not duplicate success unit tests.

Narrow tests cover keyword-normalization exceptions and replacement-token
reentry for both invocation entry points. Required insertion/write rejection
must not contaminate a newer transaction. Keep resource admission unchanged.

Run the focused eight-file integration baseline plus the narrow invocation
fault tests on native assembly, the affected harness/fault tests on Python
assembly, and the full default regression suite. Attribute existing failures
by identity, not count. Settle the intended checkpoint before a bounded
Code/State implementation review; no new plan review or broad cleanup.

## Leaf Acceptance

Both bounded implementation reviews returned GO with no findings and no
remediation: [Code report](history/lifecycle-integration/PytoLifecyleIntegInvocation-ReviewCode.md)
and [State report](history/lifecycle-integration/PytoLifecyleIntegInvocation-ReviewState.md).
The reviewed tuple is:

| Repository | Revision |
| --- | --- |
| `pyrolyze` runtime/fixtures | `b188301216486aee3b43c1ecc7b7fe89307d0273` |
| `yidl-lifecycle` | `05554397d1837ecbeafa36e4685477dd5ff30fc6` |
| `yidl` | `a7cc1de7b630b55bd194940ecad83f3f1738cf8a` |
| `astichi` | `1c47f781d3804130fdd61cbee07a3b2e4529158a` |

Final verification: focused native **167 passed**; affected Python **23 passed**;
full default **957 passed, 13 unchanged failures, 20 skipped**; broader unactivated
route **44 passed, 11 unchanged failures**. Failure identities match the callback
checkpoint. Formatting and diff checks pass; historical JSON, runtime selection,
and library/compiler source are unchanged. Code independently ran the 23 affected
tests on both backends; State ran native coverage and additional fault probes.

The review also confirmed a pre-existing limitation: hostile keyword mappings
can replace transaction ownership during later callable argument expansion.
This checkpoint fences normalization and candidate writes, not arbitrary user
callable side effects or deep mutation of argument referents. It does not claim
to repair that existing limitation.

The next authorized bounded checkpoint is slot-call invocation values together
with binding selection. Elision, replacement, failed-attempt discard, and retry
must be proved together. Other resource categories and default activation remain
gated; an immutable invocation record does not make its binding transactional.

## Slot-Call Value Checkpoint

Status: implementation authorized, acceptance pending. This is a bounded
plain-value selection adapter, not approval of external resource completion.

- Redeclare slot-call configuration as constructor-time lifecycle constants
  and runtime locals as `local_store`; remove the manual generated-init chain.
- Publish callable identity, schema, arguments, and selected value binding as
  one frozen managed record on `PASS_TX_KEY`. Public reads use current, while
  in-attempt elision compares against the candidate. A new detached value
  binding prevents evaluation from rebinding the accepted binding in place.
- Use a separate private graph gate admitting exact ordinary slot-call slots
  and the already admitted field/callback routes. Select and reject external
  stores, effects, async effects, and mount requests before binding side effects.
  Existing gates and the runtime selector remain unchanged.
- Capture original attempt ownership before normalization. Recheck after user
  equality/callable/result-projection work and before candidate assignment;
  caught preparation/execution failure remains sticky at outer completion.
- Keep one legacy local-store record for the unactivated route; preserve its
  immediate binding reuse/replacement and existing commit/rollback/deactivation
  calls. Do not change shared slot-call handlers or claim rollback of referents.
- Ordinary result replacement, not graph slot replacement or component
  retirement, is admitted. Argument/value referents remain shallow and caller
  owned. Site metadata and runtime locals remain existing scratch state.

The canonical subprocess target covers current/candidate selection, same-input
elision, callable/shape/argument changes, dirty-forced evaluation, repeated
in-attempt changes, parent failure after child success, caught callable failure,
fresh retry, runtime-context injection, declaration/manager identity, and legacy
binding reuse. Narrow tests cover resource rejection before side effects,
preparation/projection failures, and replacement-token reentry. Run the expanded
focused baseline, affected Python assembly, unactivated slot-call compatibility,
and full default regression before a bounded Code/State implementation review.

Implementation verification, 2026-10-08: native focused integration plus the
existing decomposed slot-call compatibility file **204 passed**; affected
canonical/fault coverage on Python assembly **27 passed**; full default
**967 passed, 13 unchanged failures, 20 skipped**; broader unactivated route
**44 passed, 11 unchanged failures**. The existing visitor/host-order and
override/mount/generation failures retain their leaf-checkpoint identities.
Historical snapshots, shared handlers, runtime selection, and compiler/library
source are unchanged. The new canonical JSON is an authored target, not a
replacement of historical observations. Acceptance is pending implementation
review on the settled tuple, not implied by these checks.
