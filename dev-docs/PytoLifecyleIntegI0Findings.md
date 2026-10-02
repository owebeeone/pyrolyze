# Lifecycle Integration I0 Findings

## Status

Baseline and inventory recorded on 2026-10-03 for
`dev-docs/PytoLifecyleIntegPlan.md`. No runtime behavior changed. I0's semantic
approval gate is still open; this is not an I1/L0 completion claim or permission
to start a roll-build.

The detailed field/resource mapping is in
`dev-docs/PytoLifecyleIntegI0Inventory.md`. Reproducible characterization fixtures
and snapshot regeneration instructions are in
`tests/data/lcm_integration/README.md`.

## Checkout And Environment

| Repository | Tested Revision |
| --- | --- |
| Parent checkout | `a20f8cfb633a268925464eb27728d1934a70aea9` |
| Pyrolyze, `lcm-resume` | `b8d189f770dc5dc956584f1fb6dbe845651c15d8` plus the new I0 fixtures/docs |
| yidl-lifecycle, `lcm-resume` | `cdf08544deea846bca4fa7e0c468ebee8d41e138` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` plus existing dirty extraction/doc cleanup |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |

Python 3.12.12; macOS 26.6.2, arm64; pytest 9.0.3; pytest-cov 7.1.0.
The latter is outside Pyrolyze's declared `pytest-cov<7` optional test range.
No dependency or lockfile changes were made. The source import of
`yidl_lifecycle` works, but its installed distribution metadata is absent in
this workspace environment. This is evidence for the working checkout, not a
fresh-wheel reproducibility claim.

Pyrolyze's pytest11 import-hook plugin is automatically discovered when `src`
is on `PYTHONPATH`. Explicitly adding the same plugin with `-p` fails with
duplicate registration before running tests. Dynamic fixtures use the compiler's
existing `load_transformed_namespace` helper.

The lifecycle and Astichi repositories were clean. YIDL's pre-existing dirty
runtime-wrapper removal, documentation moves, and example import updates were
left untouched. The parent checkout has other unrelated changed submodules and
files. No submodule pointers, commits, tags, or runtime defaults were changed
for I0.

## Verification Results

| Target | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: |
| Existing seven-file focused LCM baseline | 32 | 0 | 0 |
| Full default suite before I0 fixtures | 802 | 13 | 20 |
| Full default suite after I0 fixtures | 806 | 13 | 20 |
| Broader eight-file subset: original | 55 | 0 | 0 |
| Broader eight-file subset: default monolithic LCM | 53 | 2 | 0 |
| Broader eight-file subset: decomposed LCM | 41 | 14 | 0 |
| External-store/effect/slot-expression subset: each of the three runtimes | 53 | 0 | 0 |
| New isolated characterization snapshots | 4 | 0 | 0 |

The full suite's failure names are identical before and after I0. Initial run:
125.73 seconds; final run: 31.62 seconds. These are suite wall times in a reused
environment, not a controlled performance comparison. Both runs also emitted
one existing tkinter/Tix deprecation warning.

`python -m yidl_lifecycle.regenerate_lifecycle_base` reported that the committed
generated base matches regenerated YIDL. No rewrite was needed. I0 did not
change the library and did not rerun its full suite; its previously recorded
264-pass/46-skip result remains historical, not a new I0 result.

### Existing Failures

Default full suite:

- Eleven visitor/visualization failures: `visitor.py` calls public
  `own_committed_ui_entries()`, absent from the monolithic `RenderContext`.
  Affected files: `test_basic_pyro_shapes.py` (4),
  `test_comprehensive_backend_visualize.py` (1), `test_runtime_pyro_call.py` (1),
  `test_visitor_context_graph.py` (2), and
  `test_visitor_context_graph_integrated.py` (3).
- `test_buggy_reconcile_mode_keeps_retained_nested_row_above_trailing_sibling`:
  retained row is ordered after the trailing sibling.
- `test_native_pyside6_conditional_nested_layout_toggle_keeps_row_above_trailing_label`:
  retained row is below the trailing label.

Decomposed broader subset:

- Nine app-context-override failures: stale `_scope_active` access, while the
  base exposes `is_scope_active()` with graph-wide key activity semantics.
- One loop-scope mount-advertisement failure: no advertisement reaches the
  expected enclosing native container.
- One generation-relocation failure: grid generation stays 0 instead of 1.
- Three event-handler integration failures: UI assembly assumes every child
  has `ui_state`, but `EventHandlerSlotContextStateMgr` does not. These affect
  component callback identity, scheduled flushing, and deactivated dispatch.

The two monolithic broader-subset failures are the existing visitor failures.
These clusters are baseline blockers for eventual I7 routing, not fixes made by
I0. Do not equate the 32 focused passes with a completed integration.

## Observed Boundary Semantics

The authored fixture renders `panel -> row -> child -> text`, then changes the
child label before the parent throws. It separately records root UI and each
registered child's published UI.

| Scenario | Original | Monolithic LCM | Decomposed LCM |
| --- | --- | --- | --- |
| Parent fails after child succeeds | Root remains old; child's published UI is new | Same as original | Root and observed child UI remain old |
| Child failure is caught; outer pass continues | Outer tail becomes new; failed child stays old | Same as original | Same visible result |
| Next successful render | Publishes recovered values | Publishes recovered values | Publishes recovered values |
| Unchanged repeated input | Child body is elided | Child body is elided | Child body is elided |

The decomposed result is for this fixture, not proof of graph-wide atomicity:
nested render contexts still allocate separate managers, and resources retain
separate publication mechanisms. It also reports implementation metadata as
`bare_refactor`, despite selecting `bare_refactor_lcm`; the snapshot makes this
existing mismatch visible.

**The original runtime is not graph-wide atomic.** The proposed I3 assertion
that an earlier child remains provisional until the outer render succeeds is
an intentional semantic change if accepted, not an equivalence test.

**Caught child failure is currently local.** Making one shared publication
transaction abort on that failure changes behavior too. Preserving local
recovery requires an explicit design; nested begin counts are not savepoints.
The fixture catches at an ordinary boundary callback because authored `try`
is not supported by the compiler.

## Manager Failure Completion

The three-participant probe uses the actual extracted `TransactionManager` and
minimal protocol participants. It tests dispatch/error mechanics, not generated
field conversion or an ownership adapter.

| Injected Failure | Current Observation |
| --- | --- |
| Participant 2 prepare | No values publish; rollback and after-rollback visit all participants if cleanup succeeds |
| Participant 2 apply | Participant 1 publishes; participant 3 apply is skipped; no after-commit callbacks run |
| Participant 1 after-commit | All values publish; later after-commit callbacks are skipped |
| Participant 1 rollback | Later rollback and every after-rollback callback are skipped; participant work/tokens remain |
| Participant 1 after-rollback | All rollback callbacks ran; later after-rollback callbacks are skipped |
| Prepare plus rollback failure | Cleanup exception becomes the outward error; original prepare failure is only exception context |

Every scenario clears the manager's active transaction even when participant
cleanup was skipped. Explicitly restaging all participants allows a subsequent
successful transaction in the probe; it does not repair missed external
retirement/notifications. This substantiates the existing L0 prerequisite.

## Decisions To Approve

1. **Recommend atomic outer-boundary publication.** An earlier successful child
   remains provisional if a later parent fails. Accept that this differs from
   the original and monolithic paths, and update acceptance fixtures explicitly.
2. **Recommend aborting the owning boundary after nested failure for the first
   migration.** Catching the Python exception must not allow a partially failed
   shared transaction to publish. If localized recovery is required instead,
   specify a savepoint/equivalent facility before I1/I2; do not fake it with
   the old field snapshot engine.
3. Approve the publication/default key versus pass/scratch key split and the
   resource-category mapping in the inventory. Existing mutable subscriptions
   need more than a renamed holder field.
4. Approve lifecycle-owned L0 drain/report handling before transferring mandatory
   resource cleanup to hooks. Finalize generation publication, scratch cleanup,
   retirement, and notification ordering before removing their legacy paths.

The first two questions were raised with the project owner during I0. No answer
has yet been recorded here. No dependent semantic implementation was attempted.

## Reproduction

Run from the Pyrolyze root with the existing workspace interpreter. Fixture
commands are documented beside the snapshots; the integration plan lists the
seven focused files.

Full suite:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short
```

Broader comparison, fresh process per selection:

```sh
for implementation in original lcm bare_refactor_lcm; do
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  PYROLYZE_CONTEXT_IMPL="$implementation" \
    ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short \
    tests/test_runtime_call_site_context.py \
    tests/test_app_context_override_context.py \
    tests/test_mount_advert_binding.py \
    tests/test_generic_backend_harness.py \
    tests/test_generic_backend_generation.py \
    tests/test_context_graph_phase5_component_call.py \
    tests/test_context_graph_phase8_scheduler.py \
    tests/test_visitor_context_graph.py
done
```

For the resource subset, use the same environment/selection loop with
`tests/test_context_graph_phase2_external_store.py`,
`tests/test_context_graph_phase6_use_effect.py`, and
`tests/test_runtime_slot_expr.py`. Existing scheduler, call-site, override, and
mount tests additionally cover cancellation/unsubscribe/deactivation behavior.
Some tests exercise shared substrate classes directly; passing this subset is
not proof of shared-TM integration or root-boundary failure atomicity.
