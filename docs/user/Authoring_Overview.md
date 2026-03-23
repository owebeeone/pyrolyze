# Authoring Overview

PyRolyze source starts with two opt-ins:

1. module opt-in with `#@pyrolyze` on line 1 or 2 (golden fixtures under
   `tests/data/gold_src/` still use the legacy first-line tag `#@pyrolyte`; see
   [../contributor/Testing_And_Goldens.md](../contributor/Testing_And_Goldens.md))
2. component opt-in with `@pyrolyze`

Typical author flow:

1. write declarative component functions
2. use `@pyrolyze_slotted` for value helpers that should run through plain-call slots
3. use hooks such as `use_state(...)` inside `@pyrolyze` bodies
4. emit UI through component calls, containers, generated UI libraries, or `call_native(...)`
5. use `mount(...)` when a backend requires an explicit attachment site

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
- [Mount_And_Mount_Points.md](Mount_And_Mount_Points.md)
