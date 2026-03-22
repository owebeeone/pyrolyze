# Authoring Overview

PyRolyze source starts with two opt-ins:

1. module opt-in with `#@pyrolyze` on line 1 or 2
2. component opt-in with `@pyrolyze`

Typical author flow:

1. write declarative component functions
2. use `@pyrolyze_slotted` for value helpers that should run through plain-call slots
3. use hooks such as `use_state(...)` inside `@pyrolyze` bodies
4. emit UI through component calls, containers, or `call_native(...)`

Minimal shape:

```python
#@pyrolyze
from pyrolyze.api import UIElement, call_native, pyrolyze


@pyrolyze
def label(text: str) -> None:
    call_native(UIElement)(kind="badge", props={"text": text, "visible": True})
```

The main rule is that source stays declarative, while the compiler lowers it to
explicit runtime operations.

Read next:

- [Decorators_And_Annotations.md](Decorators_And_Annotations.md)
- [Components_Containers_And_Function_Semantics.md](Components_Containers_And_Function_Semantics.md)
