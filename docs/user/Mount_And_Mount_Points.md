# Mount And Mount Points

`mount(...)` is the source-level way to select an explicit backend attachment
site for emitted native children.

Use it when a parent mountable exposes more than one child-attachment site, or
when the generated default attach behavior is not the place you want.

This is also how PyRolyze can manage UI toolkit features that are traditionally
wired up imperatively. A mount point turns a backend-specific attachment site
such as a menu bar, corner widget, tab, or pane into something authored code
can drive through normal reactive rerenders and state updates.

## Source shape

The current supported form is a `with` block:

```python
with mount(selector):
    ...
```

Supported variants:

- `with mount(selector):`
- `with mount(selector_a, selector_b):`
- `with mount(*selectors):`
- `with mount(default):`
- `with mount(no_emit):`

Current validation rules:

- selector terms are positional only
- `no_emit` must be the only selector term
- selector values must be `SlotSelector` / `MountSelector` values

## Where selectors come from

Generated native UI libraries expose selector artifacts under a `mounts`
namespace.

Examples:

```python
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary as Tk

Qt.mounts.menu_bar
Qt.mounts.corner_widget(corner=...)
Qt.mounts.widget(row=0, column=1, rowSpan=1, columnSpan=1)

Tk.mounts.tab
Tk.mounts.pane
```

These selector names are backend-specific. They come from the generated backend
schema, not from one global hard-coded list.

## What `mount(...)` means

Without an explicit `mount(...)`, the runtime uses the parent mountable's
generated default attach rules.

With `mount(...)`, directly emitted native children in that block attach
through the selected mount point instead.

That means:

- explicit `mount(...)` overrides default attach for directly emitted children
- nested `mount(...)` blocks are allowed
- the innermost active selector list wins
- backend attachment that would normally be manual stays under reactive update
  control

## Examples

### PySide6 explicit menu-bar attachment

```python
#@pyrolyze
from PySide6.QtCore import Qt as NativeQt
from pyrolyze.api import mount, pyrolyze
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt


@pyrolyze
def mounted_window() -> None:
    with Qt.CQMainWindow(windowTitle="Explicit Mount"):
        with mount(Qt.mounts.menu_bar):
            with Qt.CQMenuBar(objectName="main_menu"):
                with mount(Qt.mounts.corner_widget(corner=NativeQt.Corner.TopLeftCorner)):
                    Qt.CQPushButton("Corner", objectName="corner_button")
```

### Tkinter notebook-tab attachment

```python
#@pyrolyze
from pyrolyze.api import keyed, mount, pyrolyze, use_state
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary as Tk


@pyrolyze
def notebook_example() -> None:
    count, _set_count = use_state(2)

    with Tk.CNotebook():
        for index in keyed(range(count), key=lambda value: value):
            with mount(Tk.mounts.tab):
                Tk.CTtkFrame()
```

## `default` and `no_emit`

`default` resets selection back to normal generated attach behavior:

```python
with mount(default):
    ...
```

`no_emit` creates a non-emitting barrier:

```python
with mount(no_emit):
    ...
```

Invalid:

```python
with mount(no_emit, some_selector):
    ...
```

## Relationship to generated UI libraries

For native backends, `mount(...)` works with the generated library's mount
metadata:

- `UiInterface`
- `UiWidgetSpec`
- `MountPointSpec`

That is why the backend libraries expose both public component callables and
`mounts.*` selector artifacts.

## Current scope

- explicit `mount(...)` is part of the supported authored source surface
- generated PySide6 mount coverage is broader than generated Tkinter coverage
- generated Tkinter mount coverage currently centers on the families present in
  `TkinterUiLibrary`
- not every native toolkit API should or does become a mount point

For backend-internal design history and longer rationale, see the mount design
documents under `dev-docs/`.
