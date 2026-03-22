# UI Interface Schema

## Purpose

Describe the runtime schema for `UiInterface` and `UiInterfaceEntry`, and make
clear which UI-interface families currently exist in the repository.


## Short answer

The common UI-interface name in this repository is:

- `CoreUiLibrary`

Today there are four relevant UI-interface families:

- `CoreUiLibrary`
  - shared semantic/common surface
  - shipped under `src/pyrolyze/backends/common/`
- `PySide6UiLibrary`
  - generated native PySide6 surface
  - shipped under `src/pyrolyze/backends/pyside6/`
- `TkinterUiLibrary`
  - generated native tkinter surface
  - shipped under `src/pyrolyze/backends/tkinter/`
- `HydoUiLibrary`
  - testing-only fake toolkit surface
  - not currently shipped as a real backend package


## Code map

Schema types:

- [src/pyrolyze/backends/model.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/model.py)

Shipped backend UI interfaces:

- [src/pyrolyze/backends/common/generated_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/common/generated_library.py)
- [src/pyrolyze/backends/pyside6/generated_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/pyside6/generated_library.py)
- [src/pyrolyze/backends/tkinter/generated_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/tkinter/generated_library.py)

Testing-only fake toolkit:

- [src/pyrolyze/testing/hydo.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/testing/hydo.py)
- [scratch/generated_hydo_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/scratch/generated_hydo_library.py)

Related generation docs:

- [docs/contributor/Backend_Generation_And_Learnings.md](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/docs/contributor/Backend_Generation_And_Learnings.md)


## Schema

The current runtime schema is defined in
[model.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/model.py):

```python
@dataclass(frozen=True, slots=True)
class UiInterfaceEntry:
    public_name: str
    kind: str


@dataclass(frozen=True, slots=True)
class UiInterface:
    name: str
    owner: type[Any] | None
    entries: frozendict[str, UiInterfaceEntry]

    def bind_owner(self, owner: type[Any]) -> UiInterface: ...
    def build_element(self, public_name: str, /, **props: Any) -> Any: ...
```

The intended meaning is:

- `UiInterface.name`
  - human-readable library/interface name
  - examples: `CoreUiLibrary`, `PySide6UiLibrary`
- `UiInterface.owner`
  - the class that owns the interface
  - usually set by `@ui_interface`
- `UiInterface.entries`
  - public callable surface for that library
  - key is the authored/public name
  - value tells PyRolyze which `UIElement.kind` to emit

- `UiInterfaceEntry.public_name`
  - the public authored name
  - examples: `button`, `CQPushButton`
- `UiInterfaceEntry.kind`
  - the emitted/native kind string that downstream runtime and backend code
    resolve


## What `@ui_interface` does

The `@ui_interface` decorator binds a `UiInterface` manifest onto a class and
sets the interface owner.

The result is a class that provides:

- `UI_INTERFACE`
  - structured manifest for compiler/runtime use
- public component methods or functions
  - examples: `CoreUiLibrary.button`, `PySide6UiLibrary.CQPushButton`

Those public callables are the authored entry points, while `UI_INTERFACE`
provides the explicit schema that tools and runtime code can inspect.


## Current interface families

### `CoreUiLibrary`

Location:

- [src/pyrolyze/backends/common/generated_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/common/generated_library.py)

Purpose:

- provide the common semantic/frozen surface:
  - `section`
  - `row`
  - `badge`
  - `button`
  - `text_field`
  - `toggle`
  - `select_field`

This is the “common one” now living under `backends/`.


### `PySide6UiLibrary`

Location:

- [src/pyrolyze/backends/pyside6/generated_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/pyside6/generated_library.py)

Purpose:

- generated native PySide6 callable surface
- carries:
  - `UI_INTERFACE`
  - `WIDGET_SPECS`
  - mount-point metadata


### `TkinterUiLibrary`

Location:

- [src/pyrolyze/backends/tkinter/generated_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/backends/tkinter/generated_library.py)

Purpose:

- generated native tkinter callable surface
- carries:
  - `UI_INTERFACE`
  - `WIDGET_SPECS`


### `HydoUiLibrary`

Current status:

- conceptually part of the same family
- used as the fake/test toolkit interface
- not currently shipped as `src/pyrolyze/backends/hydo/`

Current locations:

- [src/pyrolyze/testing/hydo.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/src/pyrolyze/testing/hydo.py)
- [scratch/generated_hydo_library.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/scratch/generated_hydo_library.py)

So the repository currently has:

- three shipped backend UI interfaces under `src/pyrolyze/backends/`
- one testing-only UI interface for fake-platform verification


## Minimal example

Conceptually, a library class looks like this:

```python
@ui_interface
class ExampleUiLibrary:
    UI_INTERFACE = UiInterface(
        name="ExampleUiLibrary",
        owner=None,
        entries=frozendict(
            {
                "CExampleButton": UiInterfaceEntry(
                    public_name="CExampleButton",
                    kind="ExampleButton",
                ),
            }
        ),
    )
```

And the manifest is used like this:

```python
element = ExampleUiLibrary.UI_INTERFACE.build_element(
    "CExampleButton",
    text="Save",
)

assert element.kind == "ExampleButton"
```


## Relationship to widget specs and mount specs

`UiInterface` is only the entry-point manifest.

For native backends, that manifest normally sits beside richer backend schema:

- `UiWidgetSpec`
- `MountPointSpec`
- `MountState`

So the usual stack is:

1. `UiInterface`
   - how source names map to emitted/native kinds
2. `UiWidgetSpec`
   - constructor/prop/method/event/mount metadata for each kind
3. backend engine
   - creates and updates native objects from those specs

This separation is deliberate:

- `UiInterface` answers “what can source code call?”
- widget/mount specs answer “how does that kind behave at runtime?”


## Current limitations

- `HydoUiLibrary` is not yet promoted to a real shipped backend package.
- The broad design docs still contain some older terminology and transition
  history.
- `TkinterUiLibrary` generation is less complete than `PySide6UiLibrary`,
  especially around discovered mount points.


## Tests

Current regression coverage:

- [tests/test_generated_backend_libraries.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/tests/test_generated_backend_libraries.py)

That test now verifies:

- `CoreUiLibrary`
- `PySide6UiLibrary`
- `TkinterUiLibrary`

all import cleanly and expose real `UiInterface` manifests.
