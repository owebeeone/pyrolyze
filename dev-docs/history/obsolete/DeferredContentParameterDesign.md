# Deferred Content Parameter Design

## Purpose

This document defines the current design for passing deferred PyRolyze-rendered
content through named UI parameters.

Example use cases:

- `window(menu_bar=...)`
- `main_window(central_widget=...)`
- `button(menu=...)`

The goal is to let a component accept reactive UI content through a named
parameter without treating that content as:

- plain data
- an event handler
- an ordinary ordered child


## Core Idea

A named parameter may carry a deferred render intent.

Source code expresses that with `mint(...)`:

```python
@pyrolyze
def main_page(title: str) -> None:
    name, set_name = use_state("")

    @pyrolyze
    def menu_bar(*, title: str, current_name: str) -> None:
        label(f"{title}: {current_name}")

    with window(
        menu_bar=mint(menu_bar, title=title, current_name=name),
    ):
        app_body()
```

The deferred function itself remains an ordinary `@pyrolyze` function.

`mint(...)` is the special source-surface helper.


## Terms

- `DeferredContent`
  - runtime value representing deferred parameter content
- `mint(...)`
  - public source helper used to capture deferred parameter content
- `@pyrolyze_mint`
  - marker for the `mint(...)` helper path itself
- parameter subcontext
  - callee-owned render subcontext for one named deferred parameter


## Source Rules

Phase 1 rules:

- `mint(...)` is explicit
- the first argument is the deferred `@pyrolyze` function
- captured values after that should be keyword arguments only
- `None` clears the parameter
- one parameter value is one `DeferredContent | None`
- containers such as `list[mint(...)]` are out of scope

Supported:

```python
mint(menu_bar)
mint(menu_bar, title=title, current_name=name)
```

Not supported in phase 1:

```python
mint(menu_bar, title, name)
```

Reason:

- dirtiness must map to named captured values
- comparison must be explicit and stable
- attachment semantics stay simple if one parameter value resolves through one
  deferred-content record

This is a phase-1 simplification, not a permanent limitation.

If a parameter needs richer internal structure, the deferred `@pyrolyze`
function can emit that structure and still produce one parameter-level
`DeferredContent` value.


## Why Compiler Support Is Required

This cannot be a pure runtime convention.

Reasons:

- dirtiness must be propagated correctly
- nested `@pyrolyze` functions may be recreated on rerender
- raw callable identity is not a sufficient diff key
- existing transformed code already uses `__pyr_dirtyof(...)` for named dirty
  packaging
- `mint(...)` should behave like other source-surface constructs: valid in
  authored code, lowered before runtime execution

So `mint(...)` needs a dedicated compiler path.


## Mint Helper Model

`mint(...)` should be treated like other author-facing source helpers.

Authored shape:

```python
@pyrolyze_mint
def mint(fn, **kwargs) -> DeferredContent:
    raise CallFromNonPyrolyzeContext("mint")
```

Lowered shape:

```python
def __pyr_mint(
    fn,
    *,
    __pyr_slot_id,
    __pyr_dirty,
    __pyr_captured_dirty,
    **kwargs,
) -> DeferredContent:
    return DeferredContent(
        target=fn,
        slot_id=__pyr_slot_id,
        dirty=__pyr_dirty,
        captured_dirty=__pyr_captured_dirty,
        kwargs=frozendict(kwargs),
    )
```

Important rules:

- authored code never sees the lowered signature
- transformed code does not call the public `mint(...)` stub directly
- calling `mint(...)` outside transformed code should raise
- `__pyr_captured_dirty` should use the existing `__pyr_dirtyof(...)` packaging


## Example Lowering

Illustrative transformed shape:

```python
def __pyr_menu_bar(
    __pyr_ctx,
    __pyr_dirty_state,
    *,
    title: str,
    current_name: str,
) -> None:
    with __pyr_ctx.pass_scope():
        ...


def __pyr_main_page(
    __pyr_ctx,
    __pyr_dirty_state,
    title: str,
) -> None:
    with __pyr_ctx.pass_scope():
        name, set_name, __pyr_name_dirty = __pyr_ctx.use_state("")
        __pyr_menu_bar_dirty = __pyr_dirty_state.title or __pyr_name_dirty

        __pyr_ctx.call_component(
            window,
            menu_bar=__pyr_mint(
                menu_bar,
                __pyr_slot_id=__pyr_slot_17,
                __pyr_dirty=__pyr_menu_bar_dirty,
                __pyr_captured_dirty=__pyr_dirtyof(
                    title=__pyr_dirty_state.title,
                    current_name=__pyr_name_dirty,
                ),
                title=title,
                current_name=name,
            ),
        )
```

This shows the two distinct dirty signals:

- aggregate dirty bit: `__pyr_menu_bar_dirty`
- named dirty payload: `__pyr_dirtyof(...)`

And it assumes `mint(...)` gets a normal compiler slot id:

- every mint call site increments the module slot counter
- the lowered call uses a real `__pyr_slot_N`
- this is more representative than an abstract call-site token


## DeferredContent Shape

Recommended runtime value:

```python
@dataclass(frozen=True, slots=True)
class DeferredContent:
    target: object
    slot_id: SlotId
    dirty: bool
    captured_dirty: DirtyStateContext
    kwargs: frozendict[str, object]
```

Meaning:

- `target`
  - deferred `@pyrolyze` callable target
- `slot_id`
  - stable compiler slot identity for the mint site
- `dirty`
  - aggregate dirty bit for the deferred parameter as a whole
- `captured_dirty`
  - named dirty payload created with `__pyr_dirtyof(...)`
- `kwargs`
  - captured named values


## Ownership And Identity

Capture happens in the caller.

Rendering happens in a callee-owned parameter subcontext.

That means:

- the caller creates `DeferredContent`
- the receiving component instance owns the parameter subcontext
- the deferred parameter does not belong to the caller’s ordinary container
  slot

Parameter subcontext identity should be based on:

- callee component instance slot id
- parameter name
- nested slot lineage inside that parameter subcontext

Parameter name alone is not enough.


## Runtime State

Illustrative state shape:

```python
@dataclass(slots=True)
class ParameterSubcontextState:
    parameter_name: str
    deferred: DeferredContent | None
    child_slot_id: object
    resolved_head: object | None
    child_context: object | None
    dirty: bool = False


@dataclass(slots=True)
class ComponentInstanceState:
    ...
    parameter_subcontexts: dict[str, ParameterSubcontextState]
```

The parameter subcontext lives on the callee component instance state.


## Dirtiness Model

The enclosing node should be considered dirty if any of these happen:

- ordinary props changed
- deferred target metadata changed
- deferred aggregate dirty bit is true
- deferred captured kwargs changed
- a named parameter subcontext rerendered to a different resolved attachment
- the parameter was cleared

Practical comparison key:

- deferred target metadata
- mint slot id
- deferred aggregate dirty bit
- captured kwargs
- captured dirty payload

Stateful sources feeding `mint(...)` should expose their own dirty handles in
lowered code so the aggregate deferred dirty bit can be computed explicitly.


## Invalidation Strategy

Primary model:

- deferred parameter dirtiness comes from captured dirty state at the mint site
- the callee-owned parameter subcontext rerenders when:
  - the minted payload changes
  - the minted aggregate dirty bit is true
  - the parameter subcontext invalidates itself during evaluation

This keeps deferred parameters aligned with normal transformed PyRolyze
dirtiness instead of inventing a second state system.

Possible fallback:

- treat a parameter subcontext more like an external-store or hidden
  `use_state` source
- when that subcontext evaluates to a different resolved native value, emit a
  hidden invalidation upward so the enclosing component becomes dirty

This may be a reliable cross-context mechanism, but it carries a real risk of
creating evaluation/invalidation loops if deferred evaluation itself causes the
same deferred parameter to invalidate again immediately.

So this should stay a fallback option, not the primary design for phase 1.


## Attachment Contract

The parameter subcontext may render an arbitrary PyRolyze subtree internally.

But the consuming backend attachment point usually still wants one resolved
attachable object.

So phase 1 should require:

- one deferred parameter slot
- one resolved attachable head object
- or one composite wrapper that exposes one attachable head object

Backend reconciliation should stay simple:

- if the resolved attachment changed, call the relevant setter/attach path


## Lifecycle

### Mount

When a component instance receives `DeferredContent` for a named parameter:

1. create or look up the parameter subcontext
2. store the `DeferredContent`
3. render it in that parameter subcontext
4. capture the resolved attachable head object
5. attach that result through the consumer’s backend logic

### Stable rerender

If:

- the deferred value is unchanged
- aggregate dirty is false
- the parameter subcontext is not dirty
- the resolved head did not change

then:

- no deferred rerender is needed
- no attachment update is needed

### Changed deferred input

If:

- target metadata changes, or
- aggregate dirty is true, or
- captured kwargs change, or
- captured dirty payload indicates a relevant change

then:

1. rerender the parameter subcontext
2. compare the resolved head
3. if it changed, mark the enclosing node dirty

### Clear

If the parameter becomes `None`:

1. dispose the parameter subcontext
2. clear stored deferred state
3. clear the resolved head
4. mark the enclosing node dirty so attachment is cleared


## Non-Goals For Phase 1

- implicit sugar like `menu_bar=menu_bar(title)`
- containers of deferred content
- generic multi-root backend attachment
- mixing deferred parameter subcontexts into the caller’s ordinary child slot
  model


## Open Decisions

- exact representation of target metadata for stable comparison
- exact runtime type of `child_context`
- exact contract for “resolved attachable head object”
- whether `mint(...)` should accept only `@pyrolyze` functions or a wider
  compatible set


## TODOs

- verify whether deferred parameter invalidation can be expressed entirely with
  captured dirtiness plus parameter-subcontext invalidation
- if not, evaluate a hidden external-store or hidden `use_state` style
  invalidation path for deferred parameters
- if that fallback is used, guard explicitly against
  evaluation/invalidation loops
