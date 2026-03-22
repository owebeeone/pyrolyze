# Packed `kwds` UI Interface Optimization

## Purpose

Explain the generated `UiLibrary.__element(..., kwds=...)` convention and the
compiler behavior it enables.

## Rule

When a generated or hand-written UI library defines an internal helper like:

```python
@classmethod
def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
    return UIElement(kind=kind, props=dict(kwds))
```

the trailing keyword-only parameter named `kwds` is a source-level signal to
the PyRolyze compiler.

If a matching `@pyrolyze` method is a thin native wrapper around
`call_native(cls.__element)(...)`, the compiler lowers the private `__pyr_*`
runtime helper to accept `**kwds` and forward that packed keyword payload into
`__element(...)`.

## Why It Exists

Generated UI libraries can expose very large public parameter lists for IDE
support and discoverability. Without this optimization, each lowered wrapper
would rebuild a large props dictionary every time it runs.

With the packed-`kwds` lowering:

- public component methods stay explicit and annotated
- the private lowered helper uses `**kwds`
- only arguments actually passed by the caller are forwarded
- omitted optional arguments do not appear in `UIElement.props`

This makes generated wrappers easier to read and reduces concern about the
large source-level parameter lists.

## Behavioral Example

Given:

```python
PySide6UiLibrary.CQPushButton("Save")
```

the resulting `UIElement.props` should include only:

```python
{"text": "Save"}
```

not every optional parameter from the public signature.

If the caller explicitly passes `flat=None`, then `flat` should appear in
`UIElement.props`.

## Scope

This optimization is intentionally narrow.

It applies only when the compiler can prove the `@pyrolyze` method is a pure
native wrapper around the internal `__element(...)` helper.

More complex component bodies continue to use the normal lowered calling
convention.

## Related Files

- [src/pyrolyze/compiler/kernels/v3_14/rewrite.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/compiler/kernels/v3_14/rewrite.py)
- [src/pyrolyze/runtime/context.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/runtime/context.py)
- [tests/test_ast_phase7_native_call_rewrite.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/tests/test_ast_phase7_native_call_rewrite.py)
