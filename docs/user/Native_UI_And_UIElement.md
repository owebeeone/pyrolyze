# Native UI And UIElement

PyRolyze lets authored code emit native-style UI nodes through `call_native(...)`
and `UIElement`.

## `UIElement`

`UIElement` is the current source-level UI node container:

```python
UIElement(kind: str, props: dict[str, Any], children: tuple[UIElement, ...] = ())
```

## `call_native(...)`

Use it inside `@pyrolyze` bodies:

```python
call_native(UIElement)(kind="badge", props={"text": text, "visible": True})
```

Current runtime contract:

- return `UIElement` to emit one node
- return `None` to emit nothing
- anything else is an error

## Current frozen v1 kinds

The shipped reconciler currently knows these normalized kinds:

- `section`
- `row`
- `badge`
- `button`
- `text_field`
- `toggle`
- `select_field`

Custom kinds require reconciler and backend work. See
[Building_A_UI_Library.md](Building_A_UI_Library.md).
