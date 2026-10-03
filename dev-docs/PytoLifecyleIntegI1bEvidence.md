# I1b: Common Construction And Explicit Attachment

## Scope And Status

The user authorized the next checkpoint after I1a. This implements I1b and the
common-construction prerequisite of I3a. It does not complete I3a's publication
or local-scope migration, callback/invocation holders, resource integration,
manager unification, or activation.

Baseline: Pyrolyze `6af59c9`; controlling plan
`dev-docs/PytoLifecyleIntegPlan.md`, accepted blob
`81d004dc44bc84516a3484e2a64be9667f0657bc`. Those plan bytes are unchanged.

Review tier: **one independent, read-only State review**, alternating from I1a's
Code review. Any P0/P1/P2 or reviewer request escalates to a fresh Code reviewer.
Commit the implementation before review and pin all dependency revisions. Only
review output documents may be uncommitted during the gate. This is an interior
checkpoint behind the accepted construction boundary, not a surface freeze.

## Construction Shape

- `StateMgrBase` declares owner, render/root resolution, parent/slot inputs,
  context kind, dirty/seen initialization, and site metadata once. Root state
  uses neutral parent/slot defaults; it does not attach as a slot.
- Common inputs are initvars, not a second authoritative facade attribute
  store. Stored fields remain lifecycle-generated state. The intermediate
  `_resolved_render_context_state_mgr` initvar is no longer needed.
- Manager resolution/injection moves to `StateMgrBase.create`, extending I1a's
  pre-initialization injection to ordinary slots as well as rerunnable slots.
  Render-boundary precedence and explicit-manager fallback remain unchanged.
- The existing ordinary hierarchy is retained. Its multiple-inheritance MRO
  selects the existing generated context initializer; no second independently
  decorated slot branch, extra facade wrapper, or initializer chaining is added.
  Decorating both branches would introduce competing slotted layouts.
- `SlotContextStateMgr.create` constructs the complete concrete state first,
  then calls `attach_to_graph` once. Registration remains root before parent.
  Direct constructors now construct detached states; graph-owning callers use
  `create`. Repository facade factories already use that entry point.
- Removed the manual common-field initializer and its class-dispatch branch,
  the redundant rerunnable initializer, both `_attach_to_graph_bad_program`
  declarations/factories, duplicate input/copy declarations, and duplicate site
  metadata initialization in container/slot-call state.

Common identity declarations retain existing write behavior: ordinary slots
allow parent/slot reassignment; context-backed render identity and the two
previously decorated slot types' parent/slot identities stay const. Small
overrides preserve this compatibility without duplicating inputs or copy
implementations. No public setter is removed or silently made ineffective.

## Value And Completion Boundary

Dirty/seen remain nontransactional fields and site metadata remains
nontransactional helper storage in this construction checkpoint. Their
published/local-pass classification, `_pass_child_order` / `_pass_child_dirty`
removal, and local scope ownership remain I3a/I2 work. This document does not
call those fields' final transactional behavior implemented.

Ordinary event state now receives its render's manager during construction;
its callback holders are still manual and are not newly enlisted or published.
Nested renders retain their own managers, and call-site collections retain
their independent completion owners. No begin/end/rollback method, field key,
resource-delivery algorithm, or native emission path is changed.

No registration happens if an initializer or constructor factory raises.
Attachment itself still performs the existing two domain calls; failure in the
second registration is not given a new graph-wide rollback guarantee here.
Existing cleanup/registration semantics beyond the construction boundary are
not silently hardened.

## Verification

- Initial red: all three late-failure tests registered partially initialized
  objects; the construction golden lacked common fields/manager injection and
  observed attached direct constructors. Four tests failed before source edits.
- The added identity-write golden then caught an overly strict common identity
  draft. Small compatibility overrides restored the existing policies; no
  historical runtime snapshot was updated to accommodate the draft.
- Final focused set: **47 passed in 3.11s**, including the I1a checks, new
  construction golden, three narrow failure cases, leaf rerender, and all
  historical characterization cases.
- The new canonical JSON covers seven ordinary/decorated/MI state types, single
  common field identities, completed initialization at registration, manager
  identity, root/parent registration order, detached direct construction, and
  existing identity-write policies. Bespoke tests cover only late initialization
  failures; they do not duplicate the golden's success assertions.
- Historical JSON baselines are byte-unchanged. No library/YIDL/Astichi source,
  parent pointer, selector default, tag, push, or merge is changed.
- Diff whitespace check passes. Active source has no attachment pseudo-field,
  attachment default factory, or intermediate resolved-render initvar.

Final full default suite: **817 passed, 13 failed, 20 skipped, 1 warning in
30.75s**. These are the same eleven visitor/export and two host-ordering failure
names recorded at I1a; the four new passes are construction coverage. The
eight-file decomposed subset still has **41 passed and 14 failed** in the same
override, mount, generation, and event-UI clusters. I0's pre-existing failures
are not treated as repaired by construction changes.

The exact implementation revision and final independent review outcome are
recorded after the settled checkpoint's review. These suite results alone do
not claim acceptance or activation.

## Reproduction And Next Work

From the Pyrolyze repository root:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short \
  tests/test_runtime_context_state_lcm_construction.py \
  tests/test_runtime_context_state_lcm_context_base.py \
  tests/test_runtime_context_state_lcm_slot_expr.py \
  tests/test_runtime_context_state_lcm_leaf_rerender.py \
  tests/test_lcm_integration_characterization.py
```

The integration plan names the broader/full commands; adjacent fixture README
documents golden inspection. Next is the remaining I3a value/local-pass work,
then I3b callback selection and I3c invocation holders at existing boundaries.
