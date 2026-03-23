# Examples

## Dynamic grid example

The main shipped example is:

- `examples/grid_app.py`

It shows:

- `use_state`
- nested keyed loops
- container calls
- component calls
- native `UIElement` emission

The host runner is:

- `examples/run_grid_app.py`

## Generated native mount examples

The current end-to-end generated native mount coverage lives in tests:

- `tests/test_pyside6_native_host.py`
- `tests/test_tkinter_native_host.py`

Those are the best current source examples for authored `mount(...)` with
generated backend libraries.

## Simple native emitter

```python
#@pyrolyze
from pyrolyze.api import UIElement, call_native, pyrolyze


@pyrolyze
def badge(text: str) -> None:
    call_native(UIElement)(
        kind="badge",
        props={"text": text, "visible": True},
    )
```

## Source-backed compiler examples

For smaller examples, inspect:

- `tests/data/gold_src/`

Those files are useful because they are:

- real source fixtures
- transformed in golden tests
- easier to inspect than inline test strings
