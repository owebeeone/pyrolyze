# Decorators And Annotations

## Core decorators

- `@pyrolyze`
  - marks a reactive component or emitter
- `@pyrolyze_slotted`
  - marks a slotted value helper lowered through `call_plain(...)`

## Core callable annotations

- `ComponentRef[...]`
  - use for component-valued locals, parameters, or return values
- `SlotCallable[...]`
  - use for slotted helper values
- `Callable[...]`
  - use when a callable should stay plain Python
- `PyrolyzeHandler[...]`
  - reserved callback typing surface for explicit event-boundary use (canonical
    spelling in `pyrolyze.api`)
- `PyrolyteHandler[...]`
  - compatibility alias for the same annotation (older spelling); the compiler
    accepts both names when matching imports

## When you must annotate

Annotate a function-valued symbol when the compiler cannot classify it directly
from the definition site.

Typical cases:

- returning a nested `@pyrolyze` component from a factory
- passing around a slotted helper as a value
- making it explicit that a callable should remain plain Python

Examples:

```python
from pyrolyze.api import ComponentRef, SlotCallable


def make_panel() -> ComponentRef[[str]]:
    ...


def transform_label(fn: SlotCallable[[str], str], text: str) -> str:
    ...
```

## What to avoid

- leaving function-valued flows untyped
- using a plain `Callable[...]` when the value is actually a component or a
  slotted helper

For call behavior, read
[Components_Containers_And_Function_Semantics.md](Components_Containers_And_Function_Semantics.md).
