# Component Selection Checkpoint

Status: implemented behind `_enable_component_render`, extending the mount
expression proof. Normal rendering and earlier proof gates remain unchanged.
Aggregate implementation review is deferred.

## Storage And Completion

Component identity, argument schema, and installed child are one immutable
`_ComponentSelection` record, managed with identity comparison under `PASS_TX_KEY`.
Existing managed parent `children_state` supplies membership; child rendering
shares the root manager and outer decision. Construction installs the complete
selection only after the child factory succeeds. Original-token fencing precedes
the candidate write. Current graph traversal uses the current selection, not
the candidate child.

An initial child remains provisional until outer publication. Rollback clears
its selection even if a caller retains the component facade. Unchanged successful
renders retain child identity. Existing legacy/earlier-gate behavior is preserved
through a temporary local compatibility record; it is not a second permanent API.

## Replacement And Retirement

The same proof now admits component replacement and omission. Replacement keeps
the current child intact, clears only candidate selection, and constructs the
replacement under the original outer owner. Failed/superseded children remain
tracked even when tracebacks or snapshots retain their facades.

Before participant capture, unreachable component subtrees stage empty membership,
selection, and UI. Existing callback/subscription/expression/effect adapters see
the current graph and candidate graph and perform their established resource
retirement. This is not recursive imperative `deactivate()` before publication.
Explicit component deactivation also stages membership and selection; parent
failure restores the accepted child without reconnecting callbacks manually.

After a known outcome, orphan roots lose their mounted callback, registration
cache, and scheduler membership. Successful replacement retires the old child;
rollback detaches only rejected candidates. Unknown publication preserves roots
as quarantined evidence. Independent cleanup actions drain, and failures preserve
publication evidence while blocking reuse.

## Scope Boundary

This covers component selection and the bounded I5b retirement path on the proof
gate, not normal-route activation or completion of every graph/registry migration.
Owned-handler membership stages through managed `children_state`; this proof no
longer captures legacy order snapshots. The declaration/manual compatibility
consumers remain until adoption. Registry reconciliation remains the existing
cache rebuild, not a new resource teardown mechanism. Opaque containers and
structural directives are still outside admission.

The single-cohort contract supersedes older I5 language about independent nested
managers or independent child publication. No new resource ownership contract,
lifecycle-library change, or compiler change is introduced.

## Coverage

`tests/data/lcm_integration/component_selection_lifecycle.py` and its authored
JSON baseline cover provisional membership/selection, accepted UI, outer failure,
unchanged-child reuse, and retry. Narrow fault tests cover retained failed initial
selection, factory failure, failed replacement, explicit-retirement rollback,
failed-candidate resource cleanup, and cleanup-failure draining/quarantine.
The canonical trace also covers real subscriptions, superseded replacements,
old-child retirement, omission, and retained child snapshots. Historical output
baselines remain unchanged.

Selection-only verification was **1060 passed, 2 unchanged host-ordering failures,
20 skipped**, with **103 affected tests on each backend**. Retirement verification
is **1063 passed, 2 unchanged host-ordering failures, 20 skipped** in the full
native suite, and **106 affected tests passed on Python assembly**. The native
focused run including callback compatibility checks passes **114 tests**.
