# PySide6 Studio Class Support Plan

## Purpose

This document defines the plan for making the following `PySide6` classes
properly usable in authored `@pyrolyze` source for Studio-style applications:

- `QMainWindow` as a top-level window
- `QWidget` for title bars, explorer columns, tab strips, and layout shells
- `QVBoxLayout` / `QHBoxLayout` for structure and stretch-based panel splits
- `QMenuBar` for inline menu bars
- `QMenu` / `QAction` for top menus, submenus, and actions
- `QLabel` for captions and status fragments
- `QPushButton` for window chrome and pseudo-tab strips
- `QTreeView` for the explorer view
- `QTextEdit` for editor and output panes
- `QStatusBar` for the status line

This is not just a generation checklist. "Properly support" means:

- the class exists in the generated `PySide6UiLibrary`
- the author-facing surface is ergonomic enough to use directly
- the mount/runtime behavior is stable
- native bridge requirements are explicit where pure generated support is not
  enough
- the support is covered by backend and Studio-level tests


## Short Answer

Most of these classes already exist in the generated
[PySide6UiLibrary](../src/pyrolyze/backends/pyside6/generated_library.py),
but they are not all "properly supported" for Studio authoring yet.

The biggest remaining gap is not widget breadth. It is root/window structure.

Today, the native host in
[pyrolyze_native_pyside6.py](../src/pyrolyze/pyrolyze_native_pyside6.py)
accepts exactly one root `UIElement` and therefore effectively assumes one
top-level window.

For Studio we should introduce a real top-level `Root` concept that can own
multiple top-level windows, including:

- the main `QMainWindow`
- a future inspector `QMainWindow`
- later dialogs or auxiliary tool windows

So the plan has two tracks:

1. harden the existing class surfaces for the main Studio shell
2. add a real multi-window root model above `QMainWindow`

Several of the requested classes are already implemented and in active use
today:

- the current authored shell in
  [studio_shell.py](../examples/studio/studio_shell.py)
  already uses `QMainWindow`, `QWidget`, `QVBoxLayout`, `QHBoxLayout`,
  `QMenuBar`, `QMenu`, `QAction`, `QLabel`, `QPushButton`, `QTreeView`,
  `QTextEdit`, and `QStatusBar`
- the native grid example in
  [grid_app_pyside6.py](../examples/grid_app_pyside6.py)
  proves `QMainWindow`, menu bar, menus, actions, labels, buttons, layouts,
  and explicit mounts end to end
- backend/native tests already cover menu bar mounting and visibility in
  [test_widget_engine.py](../tests/backends/pyside6/test_widget_engine.py),
  [test_pyside6_native_host.py](../tests/test_pyside6_native_host.py),
  and
  [test_examples_grid_app_pyside6_native.py](../tests/test_examples_grid_app_pyside6_native.py)

So the plan below is an analysis of what is already done versus what remains,
not a greenfield wishlist.


## Current State

### Analysis Summary

Current generated-spec analysis shows:

- `QMainWindow`
  - mounts: `central_widget`, `menu_bar`, `status_bar`, `layout`, `action`,
    `menu_widget`
  - default attach order:
    `('menu_bar', 'status_bar', 'layout', 'central_widget', 'action', 'menu_widget')`
- `QWidget`
  - mounts: `layout`, `action`
- `QVBoxLayout` / `QHBoxLayout`
  - mounts: `widget`, `layout`, `menu_bar`
- `QMenuBar`
  - mounts: `action`, `corner_widget`, `layout`
- `QMenu`
  - mounts: `action`, `layout`
- `QAction`
  - mount: `menu`
  - event: `on_triggered`
- `QPushButton`
  - mounts: `layout`, `menu`, `action`
  - event: `on_clicked`
- `QTreeView`
  - mounts: `viewport`, `layout`, `action`, `corner_widget`
- `QTextEdit`
  - mounts: `viewport`, `layout`, `action`, `corner_widget`
- `QStatusBar`
  - mounts: `widget`, `layout`, `action`

So the requested classes are largely present in the generated interface already.
The real question is whether the support is ergonomic and complete enough for
Studio authoring.

### Already Strong Enough

These are already close to usable for the Studio shell:

- `QWidget`
- `QVBoxLayout`
- `QHBoxLayout`
- `QMenuBar`
- `QMenu`
- `QAction`
- `QLabel`
- `QPushButton`
- `QTextEdit`
- `QStatusBar`

Evidence:

- the current authored shell in
  [studio_shell.py](../examples/studio/studio_shell.py)
  already uses most of them successfully
- the native grid/menu example in
  [grid_app_pyside6.py](../examples/grid_app_pyside6.py)
  already exercises `QMainWindow`, `QMenuBar`, `QMenu`, `QAction`, labels,
  buttons, layouts, and the native host
- the current recreation doc in
  [StudioAppRecreation.md](StudioAppRecreation.md)
  already treats them as feasible
- backend tests already cover menu bar mounting/replacement and native host
  visibility

### Present But Not Fully Solved

- `QMainWindow`
  - works today as the single native host root
  - does not yet live inside a true multi-window root container
- `QTreeView`
  - visual widget support exists
  - model attachment currently comes from a native bridge in
    [studio_native.py](../examples/studio/studio_native.py)
  - this is acceptable for phase 1, but the bridging story should be made
    explicit and tested
- `QStatusBar`
  - basic status bar support exists and the Studio bridge already calls
    `showMessage(...)`
  - permanent-widget style Studio authoring is not yet a documented authored
    pattern
- `QMenuBar` / `QMenu` / `QAction`
  - supported and in use
  - the current authored shape is slightly awkward because top-level menus are
    written as `QAction` owning `QMenu`
  - that pattern is valid today, but it should be documented as intentional
    rather than looking accidental

### Not Solved Yet

- multi-window root ownership
- declarative top-level window sets
- host reconciliation for add/remove/update of multiple top-level windows
- full non-widget model authoring for `QTreeView`
- a cleaner public top-level root story than "exactly one root `QMainWindow`"


## Target Support Contract

The Studio authoring target should look roughly like this:

```python
@pyrolyze
def studio_app() -> None:
    with Root():
        main_window()
        if inspector_open:
            inspector_window()
```

Where:

- `Root` is not a `QWidget`
- `Root` does not "take a `QMainWindow`"
- `Root` is a logical top-level container owned by the runtime host
- its children may be `CQMainWindow`, `CQDialog`, or other top-level widgets

This is the correct place to support multiple windows.

`QMainWindow` should remain an ordinary authored top-level widget, not the
special root itself.


## Per-Class Plan

### `QMainWindow`

Current state:

- generated and usable
- supports central widget, menu bar, and status bar mounts
- currently coupled to a single-root host assumption
- already used successfully by:
  - [grid_app_pyside6.py](../examples/grid_app_pyside6.py)
  - [studio_shell.py](../examples/studio/studio_shell.py)

Required work:

- keep current single-window support as-is
- decouple `QMainWindow` from "the one root window"
- allow multiple top-level `QMainWindow` instances under `Root`
- keep existing mounts stable:
  - `central_widget`
  - `menu_bar`
  - `status_bar`

Tests:

- native host single-window regression
- native host multi-window add/remove/update
- Studio shell main window smoke test

### `QWidget`

Current state:

- already the main shell workhorse
- default layout/action attach behavior works
- already used successfully in Studio shell title bars, explorer shells, and
  central shells

Required work:

- mostly documentation and regression coverage
- document it as the canonical structural shell widget
- ensure default attach ordering stays stable for:
  - layout child
  - action child where relevant
- verify constructor-only props and public props used in Studio shells

Tests:

- nested title-bar shell composition
- stretch-based child mounts inside box layouts

### `QVBoxLayout` / `QHBoxLayout`

Current state:

- generated and used successfully in Studio shell
- stretch-based mounting is already in use via explicit mount selection
- current Studio shell already uses them as the splitter substitute

Required work:

- mostly documentation and targeted regression coverage
- bless box-layout + stretch as the phase-1 splitter substitute
- verify ordered mount behavior under large shell updates
- ensure layout-owned children are reused rather than churned

Tests:

- Studio shell composition test
- focused mount-engine regression on reordered/stretched child groups

### `QMenuBar`

Current state:

- inline non-native menu bars work
- menu visibility needed explicit host support and now works
- already proven by:
  - [grid_app_pyside6.py](../examples/grid_app_pyside6.py)
  - [studio_shell.py](../examples/studio/studio_shell.py)
  - [test_pyside6_native_host.py](../tests/test_pyside6_native_host.py)

Required work:

- mostly documentation and guardrail coverage
- keep `nativeMenuBar=False` as the Studio default
- verify inline title-bar menu mounting and visibility
- verify top-level action ordering and submenu hookup

Tests:

- `QMainWindow.menuBar()` visibility test
- authored inline title-bar menu tree test

### `QMenu` / `QAction`

Current state:

- generated action/menu surfaces are good enough for Studio shells
- submenu mounting and separators are supported
- `QAction.on_triggered` already exists
- current authored menu trees are already working

Required work:

- document the recommended authored pattern explicitly:
  - `QMenuBar.action`
  - `QMenu.action`
  - `QAction.menu`
- ensure common action events remain stable:
  - `on_triggered`
- keep separator support in the generated surface

Tests:

- menu tree golden/example test
- action-trigger integration test

### `QLabel`

Current state:

- already suitable for captions and status fragments

Required work:

- none beyond coverage and documentation

Tests:

- title caption and status fragment smoke tests

### `QPushButton`

Current state:

- already suitable for window chrome and tab-strip buttons
- `on_clicked` works
- already exercised heavily in grid app and Studio shell

Required work:

- keep event handling stable under clean-skipped subtree updates
- verify checkable pseudo-tab-strip usage remains solid

Tests:

- checked-tab-strip regression
- title-bar chrome click regression

### `QTreeView`

Current state:

- widget support exists
- model support is not part of the generated `UiLibrary`
- current Studio path uses a native bridge with `QFileSystemModel`
- the current gap is not the `QTreeView` widget itself; it is the model story

Required work:

- explicitly bless the native model-bridge pattern for phase 1
- define the minimum bridge contract:
  - find tree by `objectName`
  - attach native model
  - set root index / hide columns / connect selection if needed
- do not expand full non-widget model authoring in the same change

Tests:

- native Studio bridge attaches a `QFileSystemModel`
- tree remains mounted and interactive after rerenders

### `QTextEdit`

Current state:

- already usable for editor and bottom pane bodies
- already used in the current authored Studio shell

Required work:

- verify authored `plainText`, `readOnly`, and style updates
- ensure large content changes do not remount unnecessarily

Tests:

- editor/body retained update regression

### `QStatusBar`

Current state:

- generated and mountable from `QMainWindow`
- already used in the current Studio shell
- native `show_status_message(...)` bridge already works for phase 1

Required work:

- document the current phase-1 support level explicitly
- make status message bridging explicit
- verify labels/messages can be attached and updated without churn

Tests:

- native bridge writes a status message
- authored status bar survives rerenders


## Root Plan

### Why We Need `Root`

The current host in
[pyrolyze_native_pyside6.py](../src/pyrolyze/pyrolyze_native_pyside6.py)
currently requires exactly one root `UIElement`.

That is too narrow for Studio because we want:

- a main window
- an inspector window
- future secondary windows without inventing a second host

### Recommendation

Introduce a public non-widget root container:

- name: `Root` for now
- semantics: owns an ordered set of top-level windows
- children: `QMainWindow`, dialogs, and other top-level widgets

Preferred behavior:

- host reconciles top-level windows by slot identity
- adding a new child creates and shows a new top-level native widget
- removing a child closes/disposes that window
- updating a child retains the existing native window when possible

### What `Root` Is Not

- not a `QWidget`
- not a special case of `QMainWindow`
- not specific to Studio

This should become the generic top-level multi-window story for native
backends.


## Phased Implementation Plan

### Phase 1: Harden the Existing Studio Shell Classes

Goal:

- make the current single-window Studio shell classes stable and documented

Scope:

- `QMainWindow`
- `QWidget`
- `QVBoxLayout`
- `QHBoxLayout`
- `QMenuBar`
- `QMenu`
- `QAction`
- `QLabel`
- `QPushButton`
- `QTextEdit`
- `QStatusBar`

Deliverables:

- backend regression tests
- Studio shell integration tests
- explicit authoring guidance in docs

Current analysis:

- this phase is partly complete already
- the remaining work here is mostly:
  - documentation
  - targeted guardrail tests
  - possibly small surface cleanups, not broad new generation work

### Phase 2: Define and Implement `Root`

Goal:

- support multiple top-level authored windows in one host

Scope:

- new runtime/root abstraction
- native PySide6 host multi-window reconciliation
- at least one second window proof, likely the inspector shell

Deliverables:

- `Root` design doc
- native host multi-window tests
- authored sample with main + inspector windows

### Phase 3: Bless the Native `QTreeView` Bridge

Goal:

- make explorer support explicit without over-expanding non-widget API surface

Scope:

- `QTreeView` widget usage
- native `QFileSystemModel` bridge
- optional selection/status wiring

Deliverables:

- bridge contract doc
- explorer integration test

### Phase 4: Studio Reconstruction Pass

Goal:

- rebuild the Studio shell on the supported surface

Scope:

- main window shell
- menus
- explorer column
- editor and bottom panes
- status bar
- optional inspector second window once `Root` exists

Deliverables:

- updated `examples/studio`
- a smoke test for the rendered shell


## Suggested Test Matrix

- generated backend library assertions for mounts and event surfaces
- native PySide6 host tests for:
  - single-window update retention
  - inline menu bar visibility
  - multi-window add/remove/update
- Studio shell integration tests for:
  - menu tree exists
  - title bar buttons exist
  - explorer tree bridge attaches
  - editor/output panes retain state
  - status bar updates


## Out of Scope for This Plan

These are still Studio-adjacent but belong to separate work:

- custom frameless drag/resize handles
- overlay painting
- screenshot annotation widgets
- live widget-tree introspection services
- full non-widget `QFileSystemModel` authoring surface
- generic pointer event support for arbitrary widgets


## Progress Table

| Step | Status | Notes |
| --- | --- | --- |
| Phase 1: shell class hardening | Pending | Existing classes already mostly generated |
| Phase 2: `Root` design | Pending | Needed for multiple top-level windows |
| Phase 2: native multi-window host | Pending | Current host is single-root only |
| Phase 3: `QTreeView` native bridge contract | Pending | Keep `QFileSystemModel` native for now |
| Phase 4: Studio shell reconstruction | Pending | Use the hardened class surface |
