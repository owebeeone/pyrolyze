# Components, Containers, And Function Semantics

PyRolyze cares about how a function is meant to be used.

## Three important callable kinds

- component
  - marked with `@pyrolyse`
  - lowered to a component runtime entry point
- slotted helper
  - marked with `@pyrolyze_slotted`
  - lowered through `call_plain(...)`
- plain Python function
  - left as a normal Python call

## Container syntax

PyRolyze reserves:

```python
with helper(...):
    ...
```

for container-style reactive emission.

Ordinary Python context-manager syntax stays:

```python
with expr(...) as value:
    ...
```

That is not PyRolyze container syntax.

## Passing functions

If you pass functions around, preserve the intended kind:

- component-valued flow: `ComponentRef[...]`
- slotted helper flow: `SlotCallable[...]`
- ordinary callable flow: `Callable[...]`

This matters because the compiler needs to preserve the right calling semantics.

## `call_native(...)`

`call_native(...)` is not a function kind.

It is a compiler intrinsic used inside `@pyrolyse` bodies. It lowers to
`ctx.call_native(...)` and hands native UI values to the current runtime
context. Treat it as syntax-level emission machinery, not as a callable type.

Read next:

- [Native_UI_And_UIElement.md](Native_UI_And_UIElement.md)
- [Hooks_And_State.md](Hooks_And_State.md)
