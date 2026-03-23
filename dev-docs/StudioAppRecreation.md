# Studio App Recreation

## Purpose

This document specifies how to recreate the imperative
[studio_app.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/examples/studio_app.py)
example as a new `examples/studio` application using the current
`PySide6UiLibrary` surface where possible.

This is a design and feasibility document only.


## Short Answer

We can recreate most of the visible Studio shell and layout with the current
`PySide6UiLibrary`.

We cannot recreate the whole application as a pure `PySide6UiLibrary` tree
without imperative/native helper components.

The correct phase-1 target is a hybrid design:

- declarative shell/layout/menu/status/tab/splitter structure in `@pyrolyze`
  using `PySide6UiLibrary`
- a small set of native bridge/controller objects for behavior that the current
  interface does not model

The current `PySide6UiLibrary` is already strong enough for:

- `QMainWindow`
- inline `QMenuBar`, `QMenu`, `QAction`, submenu, separator, action handlers
- `QWidget` containers and box/grid layouts
- `QSplitter`
- `QTabWidget`
- `QToolBar`
- `QStatusBar`
- `QScrollArea`
- `QLabel`, `QPushButton`, `QTextEdit`, `QLineEdit`
- basic window props such as `windowFlags`, `windowState`, `geometry`,
  `visible`, `styleSheet`, `objectName`, `minimumSize`

The main missing area is not widget breadth. It is custom widget behavior:

- custom mouse-driven resize handles
- custom title-bar drag handling
- custom painting overlays
- drawing on screenshots
- widget-tree introspection services
- non-widget runtime objects such as `QFileSystemModel`, `QSettings`, `QTimer`


## Current Imperative App Inventory

The current imperative example contains these major subsystems.

### Shell and Windowing

- frameless root `QMainWindow`
- inline `QMenuBar` placed inside a custom title bar
- custom minimize / maximize / close buttons
- manual drag handling
- Windows-specific native move support
- eight `EdgeResizeHandle` widgets for custom resize

### Persistence and Runtime Services

- `WindowGeometryManager`
- `AppConfig`, `WindowSettings`, `InspectorWindowSettings`
- `QSettings` persistence
- `QTimer` driven asyncio integration

### Main Layout

- left explorer pane
- horizontal splitter
- editor tab area
- bottom output / terminal panel
- vertical splitter
- styled `QToolBar`
- styled `QStatusBar`

### Inspector

- separate inspector `QMainWindow`
- hierarchy tab
- XML dump of the live widget tree
- visual tree with hover / click interaction
- screenshot tab

### Overlay and Screenshot Tools

- `HighlightOverlay` with custom painting
- `DrawableScreenshotLabel` with freehand drawing
- screenshot capture via `widget.grab()`

### Explorer

- `QFileSystemModel`
- `QTreeView`
- file-system path binding and click handling


## Mapping to Current `PySide6UiLibrary`

### Directly Supported Now

These map cleanly to the current generated surface.

| Subsystem | Current imperative type | Current `PySide6UiLibrary` status | Notes |
| --- | --- | --- | --- |
| Root window | `QMainWindow` | Supported | `CQMainWindow` has `windowFlags`, `windowState`, `geometry`, `minimumSize`, `styleSheet` |
| Inline title-bar container | `QWidget` + `QHBoxLayout` | Supported | Straightforward composition |
| Inline menu bar | `QMenuBar` | Supported | Use `CQMenuBar(nativeMenuBar=False)` in the custom title bar |
| Menus and submenus | `QMenu`, `QAction` | Supported | `CQAction` now includes `separator` and `on_triggered` |
| Window buttons | `QPushButton` | Supported | `on_clicked` exists |
| Main container layout | `QWidget`, `QVBoxLayout`, `QHBoxLayout` | Supported | Normal default mount path |
| Explorer shell container | `QWidget`, `QLabel`, `QToolBar` | Supported | The shell maps; the file model does not |
| Splitters | `QSplitter` | Supported | `orientation`, `handleWidth`, `sizes` props exist |
| Editor tabs | `QTabWidget` | Supported | Tab shell maps cleanly |
| Bottom panel tabs | `QTabWidget` | Supported | Same |
| Output / terminal panes | `QTextEdit` | Supported | Styled read-only/editable panels are fine |
| Status bar | `QStatusBar` + labels | Supported | Direct |
| Inspector window shell | `QMainWindow`, `QTabWidget`, buttons, scroll areas, text edits | Supported | Most of inspector chrome maps directly |
| Screenshot display shell | `QScrollArea` + container widget | Supported | The shell maps; drawing behavior does not |
| Styling | `styleSheet` | Supported | The VS Code-like theme can be applied declaratively |

### Supported Only with Native Helpers

These are feasible, but not as pure generated widgets.

| Subsystem | Why pure `PySide6UiLibrary` is not enough | Recommended recreation strategy |
| --- | --- | --- |
| Frameless drag behavior | Current surface has no generic mouse press / move event hooks on arbitrary widgets | Native window controller attached to the root shell |
| Eight resize handles | Needs custom `QWidget` subclasses with pointer math | Native `ResizeHandleSet` bridge |
| Windows native move / resize integration | Requires platform API calls and `nativeEvent` support | Keep in a platform-specific controller |
| Dynamic title-bar sizing from font changes | Needs runtime measurement and recalculation | Controller/service, not authored directly in the UI tree |
| `WindowGeometryManager` | Uses `QApplication.screens()`, `QScreen`, `QSettings` | Keep as runtime/persistence helper |
| `QSettings` config | Not part of the UI interface | Keep outside the UI tree |
| Async loop integration | `QTimer` is not part of the generated UI surface | Keep as runtime host/controller logic |
| File explorer data model | `QFileSystemModel` is not in the UI interface | Use a native explorer bridge or future non-widget interface expansion |
| Hierarchy XML dump | Needs traversal of mounted native widgets and actions | Runtime inspector service over the live root widget |
| Visual tree hover / click labels | Needs hover and click events on custom labels | Native `InteractiveHierarchyLabel` bridge or future generic pointer events |
| Highlight overlay | Needs `WA_TransparentForMouseEvents`, translucent background, and custom painting | Native overlay widget |
| Drawable screenshot canvas | Needs custom paint + mouse drawing + `QPainterPath` retention | Native drawing widget |
| Smart splitter handle widening | Needs splitter move/resize observation; current `QSplitter` surface has no events | Runtime splitter behavior controller |
| Screenshot capture / save flow | Uses `grab()`, `QPixmap`, `QFileDialog`, merge logic | Runtime helper coordinated with declarative shell |

### Not a Good Pure-Declarative Target Right Now

These are the hard boundaries if the requirement is "only authored generated
widgets and no native bridge objects."

1. Custom paint widgets.
2. Generic pointer hover/press/move hooks on arbitrary widgets.
3. Native window event handling.
4. Non-widget runtime objects like `QFileSystemModel`, `QSettings`, and
   `QTimer`.
5. Live widget-tree introspection services.


## Concrete Mapping Decisions

### 1. Frameless Main Shell

The visible shell should be recreated declaratively:

- `CQMainWindow(windowFlags=Qt.FramelessWindowHint, ...)`
- central `CQWidget`
- title bar `CQWidget`
- title bar `CQHBoxLayout`
- inline `CQMenuBar(nativeMenuBar=False)`
- minimize/maximize/close `CQPushButton`s
- content area below the title bar

The following behavior remains native/controller-side:

- title-bar drag
- Windows native move support
- maximize-on-double-click if we want native-feeling behavior
- edge/corner resize handles

### 2. Menus

The current menu structure maps directly.

Use:

- `CQMenuBar`
- `CQMenu`
- `CQAction`
- submenu via the `QAction.menu` mount
- separators via `CQAction(separator=True)`

This part should be fully declarative in the recreation.

### 3. Explorer Pane

The visual shell maps:

- `CQWidget`
- `CQVBoxLayout`
- `CQToolBar`
- `CQTreeView`
- optional custom title bar row

The file-system model does not map:

- `QFileSystemModel` is not part of `PySide6UiLibrary`
- current generated `QTreeView` surface does not make model setup the primary
  authoring path

Decision:

- phase 1 uses a native `FileExplorerBridge` or a simplified placeholder tree
- do not expand the entire non-widget model surface as part of the Studio port

### 4. Splitters and Panel Layout

The static structure maps directly:

- horizontal `CQSplitter`
- vertical `CQSplitter`
- `CQTabWidget` for editor tabs
- `CQTabWidget` for bottom panel tabs

The smart-handle policy does not:

- the imperative app widens the splitter handle when one side collapses below
  50px
- current generated `QSplitter` surface has props such as `handleWidth` and
  `sizes`
- current generated `QSplitter` surface does not expose a movement event

Decision:

- initial recreation uses a fixed handle width
- smart handle widening is phase 2 behavior via a native splitter controller

### 5. Inspector Window

The inspector shell maps very well:

- separate `CQMainWindow`
- `CQTabWidget`
- hierarchy tab
- screenshot tab
- buttons
- `CQTextEdit`
- `CQScrollArea`

The inspector services do not map directly:

- live XML generation from native widget tree
- hover/click label interactions
- sticky highlight state across the live main window

Decision:

- inspector chrome should be declarative
- inspector behavior should be driven by a native `InspectorService`

### 6. Highlight Overlay

This should remain a dedicated native component.

Reasons:

- it relies on `WA_TransparentForMouseEvents`
- it relies on translucent background behavior
- it calculates target rectangles using `mapToGlobal()` and reverse mapping
- it paints a custom border in `paintEvent`

This is a strong example of "native bridge widget embedded in a declarative
shell."

### 7. Screenshot and Drawing

Split this into shell and behavior.

Declarative shell:

- screenshot tab
- take/save/clear buttons
- `CQScrollArea`

Native behavior:

- `main_window.grab()`
- `QPixmap` merge/save
- custom drawing canvas with `QPainterPath`

Decision:

- keep `DrawableScreenshotLabel` or an equivalent as a native bridge widget

### 8. Persistence and Async

Keep these outside the declarative UI tree.

That includes:

- `AppConfig`
- `QSettings`
- geometry restore/save
- `QTimer`-driven asyncio integration

These are application services, not `PySide6UiLibrary` authoring concerns.


## Recommended Recreation Architecture

The recreation should be organized around a declarative shell plus native
bridges.

### Declarative Pieces

- `StudioRootWindow`
- `StudioTitleBar`
- `StudioMenuBar`
- `StudioMainPanels`
- `StudioStatusBar`
- `StudioInspectorChrome`

These should be ordinary `@pyrolyze` components using `PySide6UiLibrary`.

### Native Bridge Pieces

- `FramelessWindowController`
- `ResizeHandleSet`
- `FileExplorerBridge`
- `InspectorService`
- `HighlightOverlayWidget`
- `DrawableScreenshotWidget`
- `AsyncLoopBridge`
- optional `SplitterBehaviorController`

These should be treated as runtime-only helpers or explicit native components.


## Phase Plan

### Phase 1: Shell Recreation

Goal:

- recreate the visible Studio shell in `examples/studio`

Includes:

- frameless root window flag
- inline title bar
- real menu bar
- window control buttons
- left explorer shell
- horizontal and vertical splitters
- editor tabs
- bottom output / terminal tabs
- status bar
- VS Code-like theme

Excludes:

- drag/resize behavior
- live file-system model
- inspector behavior
- screenshot drawing

### Phase 2: Shell Behavior

Goal:

- restore the custom shell feel

Includes:

- native drag
- resize handles
- maximize/restore polish
- geometry persistence
- optional smart splitter handle logic

### Phase 3: Inspector Services

Goal:

- restore hierarchy dump and highlight

Includes:

- live widget-tree traversal service
- visual tree population
- hover/sticky highlight coordination
- overlay bridge

### Phase 4: Screenshot Tools

Goal:

- restore capture and annotation flow

Includes:

- capture
- drawing
- merge and save

### Phase 5: Explorer and Async

Goal:

- restore the runtime services that are not pure widget composition

Includes:

- file-system model bridge
- async loop bridge


## What We Should Not Do in the First Port

1. Do not try to force custom-paint widgets into a pure generated-widget model.
2. Do not expand the whole non-widget Qt object surface just to support Studio.
3. Do not treat the current imperative helper classes as a failure of the UI
   library.
4. Do not block the Studio port on a future generic event system for arbitrary
   widgets.


## Decision

The Studio recreation is feasible now, but as a hybrid application.

We should proceed on this basis:

- declarative composition in `PySide6UiLibrary` for the shell and most visible
  structure
- imperative/native bridges for custom behavior and non-widget services

That is the correct mapping of
[studio_app.py](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/examples/studio_app.py)
onto the current `PySide6UiInterface` surface.
