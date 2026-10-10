# Lifecycle Compatibility Retirement

This document supersedes staged rollout instructions for current runtime work.
Historical design and review records remain evidence of their original scope,
not instructions to activate a private checkpoint or select an old engine.

## Runtime Boundary

`runtime.context` directly exports `context_lifecycle`. The retired environment
selectors no longer select another implementation. Independent roots install
the final completion controller; nested roots share that outer decision.

The temporary `context_bare_refactor_lcm.py` facade module is removed. Public
contexts in `context_lifecycle` inherit the lifecycle-backed implementations in
`context_state_lcm`; construction initializes the public context itself, rather
than allocating a separate state-manager facade. Owner links identify that same
working context, including when read through its committed lifecycle view.
Internal graph consumers and fixtures no longer unwrap a `_state_mgr` object.
The remaining public adapters preserve constructor signatures, argument order,
and accepted-value reads. They do not hold a delegated context object.
The standalone expression API also remains supported and is not a render
fallback to delete.

## Retired Code

- Original, bare, monolithic LCM, and ordinary refactored engines and their
  duplicate state-manager tree.
- Private `_enable_*_render` activation helpers and feature-admission probes
  that tested intermediate rollout restrictions rather than current behavior.
- Legacy leaf and slot-call invocation records, component and keyed-item
  selection records, directive selectors, and override value snapshots.
- Manual local pass commit/rollback, child-order and dirty snapshots, and
  component handler-order restoration.
- Duplicate dirty/visitation fields; requested and handled revisions plus
  managed visitation remain authoritative.

## Coverage Mapping

| Retired evidence | Current coverage |
| --- | --- |
| Engine-by-engine success replays | Compiler-generated graph fixtures and final-runtime integration goldens |
| Local parent/child completion expectations | Single-cohort publication, abort, retry, and transaction-outcome goldens |
| Legacy invocation tracking | Invocation-value and slot-call-value goldens, including conversion and replacement fencing |
| Callback local selection restoration | Callback/component selection goldens and narrow reentry/failure checks |
| Slot-preflight admission gates | Current construction/ownership faults and supported resource goldens |
| Manual dirty restoration | Revision acknowledgment, notification retention, and pass-state failure tests |
| Independent nested manager assumption | Shared-manager construction and component selection tests |

Unused old-engine JSON snapshots and their scripts are removed. Their original
versions and review evidence remain available in Git history. Current goldens
were not regenerated to bless changed render behavior: removed observations
were legacy-only sections or storage-schema assertions replaced with checks
for the authoritative managed state.

Construction-time manager injection, detached state-manager initialization,
protocol fault injection, uncertain completion evidence, rollback, callback
identity, retained subscriptions, mount routing, and physical backend ordering
remain covered. Historical tests are not kept merely to exercise deleted code.

## Verification

The coordinated public-context cutover passes the full regression: 1,164 passed,
20 existing skips, and the unchanged Tk Tix deprecation warning. All 240 focused
lifecycle-runtime checks pass on both the default and Python assembly engines.
Grip adapter and Pyrolyze demo checks pass: 31 tests. The 23 integration goldens
also pass without changing their expected behavior for this cutover.

The new construction checks pin self-ownership, shared manager identity through
the committed view, and absence of a wrapped `_state_mgr` object. Existing
ownership, failed construction, abort/retry, callback, subscription, and reentry
assertions remain in place. The demo's worker-thread test accesses the flush
poster directly; its thread-delivery assertion is unchanged.

## Performance Check

The native Qt 20-by-20 example was compared against the committed runtime,
using isolated source snapshots and identical dependencies. The workload edits
the last cell and toggles row layout to grid layout and back. Timings include
Qt reconciliation but exclude startup and grid creation.

An initial sequential Mac comparison suggested a slowdown; alternating versions
did not reproduce it. Treat that first comparison as inconclusive on the busy
machine, not as evidence of a runtime regression. Mac profiles recorded about
91,000 fewer calls for an update and 813,000 fewer calls for paired toggles;
callback graph visit counts were unchanged.

An independent Raspberry Pi comparison used Python 3.12.12, PySide6 6.11.1,
and the Python assembly engine for both versions. Four subprocesses ran in
current/baseline/baseline/current order, each measuring two updates and two
paired toggles. Wall and process CPU times were nearly identical.

| Operation | Baseline median | Cleanup median | Reduction |
| --- | --- | --- | --- |
| Last-cell update, including Qt | 0.436 s | 0.420 s | 3.7% |
| Paired layout toggle, including Qt | 8.964 s | 8.704 s | 2.9% |
| Update render completion only | 0.277 s | 0.263 s | 4.8% |
| Paired-toggle render completion only | 7.228 s | 7.041 s | 2.6% |

These are small-sample measurements of the entire compatibility cleanup and
facade removal together, not an isolated attribution to facade removal or a
performance guarantee. No runtime optimization was needed to resolve the
initial apparent regression. Existing remote checkouts were left untouched;
the benchmark used its own source snapshots and virtual environment.

## Earlier Verification

The results below describe the preceding compatibility-retirement checkpoint.

Final default-engine full regression: 1,162 passed, 20 existing skips, no
failures. The existing Tk Tix deprecation warning is unchanged. Grip adapter
and Pyrolyze demo integration checks: 31 passed. Whitespace validation passed.

The first concurrent Python-engine focused run passed 75 checks but timed out
at the construction golden's existing 60-second subprocess limit. An isolated
replay matched the unchanged expected JSON in 9.40 seconds. The complete
focused Python-engine rerun then passed all 96 checks in 322.45 seconds with
the existing assertions and subprocess limit unchanged.
