# Container Call Nullifier Design

## Purpose

This document covers one specific runtime/lowering issue:

- allowing a container-form helper to suppress entry into a `with` boundary

This is not the same problem as mount dependency analysis.

It is a runtime/container-call problem.

The goal is to let helper wrappers such as:

- `mount_call(...)`
- similar analysis/testing helpers

participate in container lowering while still being able to decide that the
site should be inactive for this pass.

## Problem

Current container lowering is structurally like:

```python
if dirty_guard or __pyr_ctx.visit_slot_and_dirty(__pyr_slot_1):
    with __pyr_ctx.container_call(__pyr_slot_1, section, ... ) as __pyr_ctx_slot_1:
        ...
```

That assumes:

- once the dirty/visit guard passes
- the container boundary is entered

For some helpers, that is too rigid.

Example:

```python
with mount_call(sd.mount_body, selector):
    ...
```

If `sd.mount_body` is absent or disabled, we may want:

- the authored site to still exist conceptually
- but the container boundary not to open at all for this pass

## Existing runtime seam

The current runtime entry point is already fairly flexible:

```python
def container_call(
    self,
    slot_id: SlotId,
    container_fn: CompValue[Callable[..., Any]] | Callable[..., Any],
    *args: CompValue[Any] | Any,
    dirty_state: DirtyStateContext | None = None,
    _pyr_param_names: tuple[str, ...] | None = None,
    _pyr_args_dirty: tuple[Any, ...] | None = None,
    _pyr_kwargs_dirty: dict[str, Any] | None = None,
    **kwargs: CompValue[Any] | Any,
) -> _ContainerCallHandle:
    self._require_active_scope()
    raw_container_fn, _ = _unwrap(container_fn)
```

and the current unwrap seam is:

```python
def _unwrap(value: _SlotCallResult[Any] | CompValue[Any] | Any) -> tuple[Any, bool]:
    if isinstance(value, CompValue):
        return value.value, value.dirty
    if isinstance(value, _SlotCallResult):
        return value.value, _dirty_state_truthy(value.dirty)
    return value, False
```

This is important because it means `container_call(...)` already accepts more
than a plain raw callable.

That makes it a natural place to support a nullifying wrapper type.

## Why this matters

This is useful for testing and analysis because it allows:

- more realistic authored helper wrappers
- container sites that are structurally present but conditionally inactive
- easier construction of mount-heavy test shapes without hand-writing extra
  `if ...:` guards around every site

It is also useful independently of mount fuzzing:

- it is a cleaner container-call runtime capability

## Proposed lowering change

The proposed standard lowering is:

```python
if handle := __pyr_ctx.container_call(...):
    with handle:
        ...
```

instead of unconditional:

```python
with __pyr_ctx.container_call(...):
    ...
```

This means:

- `container_call(...)` may return a falsy/null handle
- if it does, the `with` body is skipped
- if it returns a real handle, execution proceeds as normal

## Likely implementation direction

One plausible implementation is:

- introduce a new carrier/wrapper type for container-call helpers
- that wrapper resolves to either:
  - `None`
  - or a real underlying container callable plus concrete args/kwargs
- `container_call(...)` treats `None` as “inactive site for this pass”

In other words, the nullification decision can likely happen at the same seam
where `CompValue` / `_SlotCallResult` are already normalized.

That is preferable to adding a separate external enable-check protocol because:

- the callable-normalization seam already exists
- helper-provided “no container this pass” can be represented in-band
- `container_call(...)` already has to decide which concrete slot/context handle
  type to return depending on what kind of container call this is

So the nullifier fits naturally into existing runtime structure.

### Important design constraint

This should **not** be modeled as:

- a fake `ComponentRef`
- or a `CompValue`

`CompValue` is deprecated and should not be the basis of new work.

The new wrapper should be a dedicated container-call carrier.

Conceptually:

```python
@dataclass(frozen=True, slots=True)
class ResolvedContainerCall:
    container_fn: Callable[..., Any]
    args: tuple[Any, ...] = ()
    kwargs: Mapping[str, Any] = ...


@dataclass(frozen=True, slots=True)
class ContainerCallThunk:
    helper_name: str
    resolver: Callable[[object], ResolvedContainerCall | None]
```

The important part is the semantics:

- if the helper is inactive for this pass, the resolver returns `None`
- if the helper is active, the resolver returns the real target container
  callable and any rewritten args/kwargs

This also means a helper such as `mount_call(...)` can effectively resolve into
“call `container_call(...)` again, but with the real target callable and real
arguments”.

That is the right level of indirection.

### Container-call-specific unwrap

Although this can reuse the general unwrap seam conceptually, the cleaner design
is likely:

- keep general `_unwrap(...)` mostly unchanged
- add a container-call-specific normalizer

For example:

```python
def _unwrap_container_call_target(
    value: object,
) -> ResolvedContainerCall | None: ...
```

Then `container_call(...)` can do:

```python
resolved = _unwrap_container_call_target(container_fn)
if resolved is None:
    return None
```

and proceed with the resolved real callable/args/kwargs.

This is better than overloading the generic `_unwrap(...)` helper with
container-call-specific semantics.

## Consequence for returned handle types

Today `container_call(...)` may return different concrete handle objects
depending on the kind of container site being opened.

The nullifier design therefore does not need to replace that behavior.

It only needs to add one more possibility:

- return a falsy/null handle when the wrapped callable resolves to “inactive”

So the design space is:

- existing concrete container handle types remain
- one additional inactive/null handle path is added

That is much smaller than redesigning all container-call handle types.

## Important semantic clarification

The nullifier path is not a separate “empty slot notification” mechanism.

The intended semantics are simply:

- the site becomes dirty
- the site is evaluated
- the wrapped callable resolves to `None`
- `container_call(...)` returns `None`
- the `with` body is not entered for this pass

That is enough.

This is exactly analogous to:

```python
if do_render:
    with ...
```

except that the decision is made by the container-call helper at evaluation
time rather than by an outer authored `if`.

The important follow-on is:

- if the value changes again later, the site is dirty again
- it is reevaluated again
- and it may then return a real handle or `None`

So `None` is not a terminal “site is gone forever” signal.
It is simply the evaluated result for this pass.

No separate “slot is empty” notification is needed.

The only real implementation constraint is:

- `container_call(...)` must not create or mark the child boundary before it
  knows whether the wrapped callable resolved to `None`

If the nullification check happens first, early return is the whole mechanism.

## Why this is preferable

This is better than introducing a separate preflight API such as:

```python
if __pyr_ctx.site_enabled(mount_call, sd.mount_body):
    with __pyr_ctx.container_call(...):
        ...
```

Reasons:

- one mechanism instead of two
- the runtime/container-call path owns the enable/disable decision
- fewer compiler concepts
- cleaner helper story

The helper does not need a separate “is enabled?” channel.
It only needs to influence the returned container handle.

## Interaction with helper wrappers

This makes helper wrappers such as `mount_call(...)` much simpler.

They do not need to:

- participate in a separate compiler-visible preflight API
- split into “is enabled?” and “actually call” phases

Instead they only need to provide a wrapped container callable payload that:

- resolves to a real callable when active
- resolves to `None` when inactive

The runtime then does the rest through ordinary `container_call(...)` lowering.

So `mount_call(...)` is best thought of as:

- a container-call helper wrapper
- not a normal emitted component ref
- not a special preflight-enable object

## Relationship to helper wrappers

This is especially relevant for wrapper helpers such as:

- `mount_call(...)`

The idea is that these helpers are still authored/runtime constructs, but the
container-call machinery can treat them as a helper-controlled container site.

The interaction point is runtime-oriented:

- helper participates in container-call semantics
- helper may decide the site should be inactive
- runtime expresses that by returning a falsy handle

So this is a runtime-domain issue, not a mount-analysis-domain issue.

## Effect on slot/context behavior

The tricky part is not the `if handle := ...` syntax itself.

The tricky part is what happens to slot visitation and teardown when the handle
is falsy.

The runtime must still define clearly:

- whether the site is treated as visited
- whether prior retained state is torn down
- whether committed children under that site are cleared
- how inactive-state transitions are represented in debug/analysis tooling

Those semantics need to be defined in `container_call(...)` / container handle
behavior, not spread across helper-specific custom logic.

## Testing value

For test shapes, this makes authored code simpler.

Instead of:

```python
if sd.mount_body:
    with mount_call(sd.mount_body, selector):
        ...
```

we can write:

```python
with mount_call(sd.mount_body, selector):
    ...
```

and let the helper/runtime decide whether the site is active.

That gives us:

- more compact test shapes
- clearer structural intent
- easier experimentation with mount-heavy scenarios

## Scope

This design does **not** define:

- full mount dependency analysis
- full shape-site attribution
- fuzzing legality rules

It only defines:

- a container-call/runtime mechanism for helper-driven no-op container sites

## First implementation slice

The smallest useful first step is:

1. allow `container_call(...)` to return a falsy/null handle
2. change compiler lowering for container sites to:
   - `if handle := __pyr_ctx.container_call(...):`
   - `with handle:`
3. define runtime semantics for:
   - skipped site
   - teardown of previously active retained state
   - committed-ui clearing for that site
4. add one helper-oriented test case using a container wrapper that nullifies
   the site

That is enough to validate the mechanism.

## Staged plan

### Stage 1. Clean up callable/value unwrapping first

Before adding a new container-call nullifier carrier, clean up the existing
legacy unwrap path.

Current helper:

```python
def _unwrap(value: _SlotCallResult[Any] | CompValue[Any] | Any) -> tuple[Any, bool]:
    if isinstance(value, CompValue):
        return value.value, value.dirty
    if isinstance(value, _SlotCallResult):
        return value.value, _dirty_state_truthy(value.dirty)
    return value, False
```

The immediate replacement target is:

```python
def _unwrap_or_none(value: _SlotCallResult[Any] | CompValue[Any] | None | Any) -> tuple[Any, bool]:
    if isinstance(value, CompValue):
        return value.value, value.dirty
    if isinstance(value, _SlotCallResult):
        return value.value, _dirty_state_truthy(value.dirty)
    return value, False
```

But the real point of this stage is broader:

- verify whether `CompValue` and `_SlotCallResult` are still genuinely produced
  on the container-call path
- clean up `runtime/context.py` so new container-call work is not layered on top
  of deprecated carriers
- remove container/directive/component-call references to `CompValue` and
  `_SlotCallResult` where they are no longer needed

Current reality check:

- `CompValue` and `_SlotCallResult` are still referenced heavily in
  `src/pyrolyze/runtime/context.py`
- they are also still referenced in:
  - `src/pyrolyze/runtime/slot_expr.py`
  - `src/pyrolyze/runtime/__init__.py`
  - `tests/test_runtime_slot_expr.py`

So Stage 1 is not “rename one helper”.
Stage 1 is:

1. verify actual live production sites for `CompValue` and `_SlotCallResult`
2. narrow or remove their use from the container-call family first
3. replace `_unwrap(...)` with a cleaner nullable/container-call-friendly seam
4. only then introduce the new nullifier carrier

### Stage 2. Add a container-call-specific wrapper carrier

After Stage 1, introduce the new dedicated container-call wrapper/carrier:

- not `CompValue`
- not a fake `ComponentRef`

This wrapper resolves to either:

- `None`
- or a real underlying container callable plus concrete args/kwargs

### Stage 3. Change container lowering

Lower container sites to:

```python
if handle := __pyr_ctx.container_call(...):
    with handle:
        ...
```

This makes container-call activation a runtime decision.

### Stage 4. Define skipped-site semantics

Make the skipped/nullified case precisely equivalent to:

- the site was evaluated
- it returned `None`
- no container boundary was opened this pass

This should not require a separate “empty slot” notification path.

### Stage 5. Add helper-oriented tests

Add tests for:

- a helper wrapper that resolves to `None`
- a helper wrapper that later resolves back to a real container
- retained subtree teardown/recreation through the nullifier path
