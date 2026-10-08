# Invocation Value Migration

Status: bounded I3c leaf checkpoint in implementation, not acceptance or runtime
activation. Read the single-cohort amendment before the older I3/I3c clauses.
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

Acceptance and the exact reviewed tuple remain pending. Do not treat passing
tests, a checkpoint commit, or publication as a review verdict.
