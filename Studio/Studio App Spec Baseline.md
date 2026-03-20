# Studio App Spec Baseline

Date: 2026-03-20  
Source analyzed: `examples/studio_app.py` (single-file implementation, ~3335 lines)

## 1. Purpose

This document captures a thorough feature and interaction baseline for the current
`studio_app.py` implementation so future PyRolyze-based work can measure parity,
identify missing capabilities, and prioritize framework improvements.

This is intentionally a source-truth analysis, not a target design proposal.

## 2. Analysis Scope and Method

Scope includes:

- All user-triggerable interactions found in source.
- Entry points from menus, shortcuts, toolbar buttons, mouse events, context menus,
  and inspector controls.
- Non-obvious behavior (platform branches, Win32 calls, restore/save behavior).
- Implemented vs partial vs placeholder/unimplemented features.

Method:

1. Enumerated interaction entry points (`QAction`, `clicked.connect`, event handlers).
2. Traced each interaction to behavior methods.
3. Traced startup/shutdown and settings persistence paths.
4. Cross-checked for dead code, stubs, and placeholders.

## 3. High-Level Baseline Summary

- App is a custom frameless `QMainWindow` shell with manual move/resize logic and
  custom title bar controls.
- There is a substantial Inspector subsystem with hierarchy XML dump, visual tree,
  hover/click highlighting overlay, screenshot capture, annotation drawing, and save.
- Persistent settings are implemented via `QSettings` with multi-screen-aware geometry
  restore logic.
- Many command surfaces exist but several are placeholders (`Open`, `Save`, Edit menu actions,
  explorer toolbar refresh/collapse, welcome panel).
- Several advanced behaviors are Windows-specific when available (Win32 `SendMessage` paths).

## 4. Feature Coverage Checklist (Requested Focus Areas)

| Requested Feature | Present? | Baseline Notes |
|---|---|---|
| Corner/edge manipulators | Yes | 8 resize handles (`EdgeResizeHandle`) with drag geometry updates. |
| Inspector graph dump | Yes | XML dump + visual tree generation from widget recursion. |
| Inspector screen capture | Yes | `QWidget.grab()` captures main window into screenshot tab. |
| Drawing on screenshot | Yes | `DrawableScreenshotLabel` tracks `QPainterPath` strokes with live preview. |
| Save drawing to file | Yes | Save dialog + pixmap export (`PNG/JPEG/All`). |
| Position/settings persistence | Yes | `QSettings` + `WindowGeometryManager` save/restore for main + inspector. |
| Borderless window | Yes | Frameless window flag is active. |
| Toggle border on/off | No | No runtime border toggle action/state found. |
| Fullscreen + F11 | Yes | `Toggle Fullscreen` action uses `QKeySequence.FullScreen` (typically F11). |
| Whole-app font-size change | Yes (partial vs request) | Global app font adjustment exists, but shortcuts are `Ctrl+Shift+=` and `Ctrl+Shift+-`, not plain `Ctrl+=`/`Ctrl+-`. |
| Help > About dialog | Yes | Help menu includes About action -> `QMessageBox.about(...)`. |

## 5. Interaction Baseline by Area

## 5.1 App Startup, Bootstrap, and CLI

### Interactions

- Launch app directly (`__main__` block).
- Optional CLI arg: `--dir`/`-d` initial folder.

### Implementation

- CLI parsing: `parse_args()` (`studio_app.py:3062`).
- Config load: `AppConfig.load()` + `QSettings` (`1258-1266`).
- If `--dir` exists and is a directory, it overrides `config.initial_dir` (`3079-3082`).
- Main window creation: `StudioMainWindow(config)` (`3327`).
- Customizer applies menus/tabs/status widgets: `customerizer.customise(window)` (`3328`).

### Non-obvious / Caveat

- `__main__` calls `asyncio.run(main(DefaultAppCustomizer()))` (`3335`) even though
  `main(...)` is a synchronous function, which is incorrect API usage for `asyncio.run`.
  This is a runtime bug risk in the example entrypoint.

## 5.2 Window Shell and Borderless Frame

### Interactions

- Frameless main window shell.
- Minimize/Maximize/Close controls.
- Title-bar drag.
- Double-click title bar to maximize/restore.
- Right-click title bar context menu.

### Implementation

- Frameless window: `super().__init__(None, Qt.FramelessWindowHint)` (`1768`).
- Custom title bar built in `setup_ui()` (`1875+`) with menu bar + control buttons.
- Button actions:
  - Minimize -> `showMinimized` (`1932`)
  - Maximize/restore -> `toggle_maximize` (`1938`)
  - Close -> `close` (`1944`)
- Drag initiation in `mousePressEvent(...)` (`2735+`) when clicking title bar background,
  excluding menu active actions and push buttons.
- Double-click maximize logic in `mouseDoubleClickEvent(...)` (`2905+`).

### Non-obvious / Caveat

- Window is frameless but still styled with a 1px border via stylesheet (`2258-2262`).
- No explicit user-facing "toggle border on/off" exists.

## 5.3 Corner and Edge Manipulators (Resize Handles)

### Interactions

- Drag any edge/corner to resize.
- Cursor shape changes when hovering each handle.

### Implementation

- 8 logical handle positions: enum `HandlePosition` (`157-165`).
- Handle widgets created by `_create_resize_handles()` (`2265-2276`).
- Handle geometry mapped around window rect in `update_geometry()` (`204-236`).
- Drag-to-resize implemented in:
  - `mousePressEvent` (`257-264`)
  - `mouseMoveEvent` (`266-326`)
  - `mouseReleaseEvent` (`328-335`)
- Resize handles refreshed on window resize event (`2279-2284`).

### APIs and mechanisms

- Uses direct `QWidget.setGeometry(...)` on the parent window.
- Uses `minimumSizeHint()` with fallback minimums (100x100) to prevent collapse.
- Cursor management via `Qt.Size*Cursor` on enter/leave.

## 5.4 Title-Bar Context Menu + Move/Size Operations

### Interactions

- Right-click title bar opens a context menu with:
  - Restore or Maximize
  - Move
  - Size (when not maximized)
  - Open Inspector
  - ViewMesh submenu: Open File, Open Folder, Settings
  - Minimize
  - Close

### Implementation

- Context menu wiring: `customContextMenuRequested.connect(self.show_title_bar_context_menu)` (`1882`).
- Menu action execution logic in `show_title_bar_context_menu(...)` (`2665-2733`).

### Non-obvious mechanisms

- "Move" starts a timer-driven drag mode:
  - sets override cursor `Qt.SizeAllCursor`
  - `grabMouse()`
  - updates position every 16ms via `_perform_context_menu_move()` (`2962-2969`)
- Move mode is canceled on next mouse press via `eventFilter(...)` (`3002-3015`).
- "Size" uses Win32 system command path when available:
  - `ReleaseCapture()`
  - `SendMessage(winId, WM_SYSCOMMAND, SC_SIZE+BOTTOMRIGHT, 0)` (`2718-2722`)

## 5.5 Mouse-Driven Drag/Resize Behavior (Main Window)

### Interactions

- Drag window by title bar background.
- Manual drag fallback when Win32 path unavailable.
- Manual edge cursor hints for non-Windows/fallback branch.

### Implementation

- Drag start decision and control-hit filtering: `mousePressEvent(...)` (`2735-2819`).
- Manual dragging in `mouseMoveEvent(...)` (`2825-2830`).
- Drag end in `mouseReleaseEvent(...)` (`2854-2863`).
- Edge direction helper: `get_resize_direction(...)` (`2865-2895`).
- Cursor shape helper: `get_resize_cursor(...)` (`2897-2903`).

### Platform behavior

- On Windows with Win32 functions loaded:
  - title-bar drag prefers system move via `SendMessage(...SC_MOVE...)` (`2792-2797`).
- Else:
  - falls back to manual drag calculations.

## 5.6 Menu Bar, Menu Commands, and Keyboard Shortcuts

Menu population is delegated to `DefaultAppCustomizer._populate_menus(...)` (`1597+`).

### File menu

| Command | Shortcut | Handler | Status |
|---|---|---|---|
| New | `QKeySequence.New` | `on_new_file` | Placeholder |
| Open File | `QKeySequence.Open` | `on_open_file` | Placeholder |
| Open Folder | none explicit | `on_open_folder` | Placeholder |
| Save | `QKeySequence.Save` | `on_save` | Placeholder |
| Save As | `QKeySequence.SaveAs` | `on_save_as` | Placeholder |
| Exit | `QKeySequence.Quit` | `close` | Implemented |

### Edit menu

| Command | Shortcut | Handler | Status |
|---|---|---|---|
| Undo | `QKeySequence.Undo` | `showMessage("Undo not implemented")` | Placeholder |
| Redo | `QKeySequence.Redo` | `showMessage("Redo not implemented")` | Placeholder |
| Cut | `QKeySequence.Cut` | `showMessage("Cut not implemented")` | Placeholder |
| Copy | `QKeySequence.Copy` | `showMessage("Copy not implemented")` | Placeholder |
| Paste | `QKeySequence.Paste` | `showMessage("Paste not implemented")` | Placeholder |

### View menu

| Command | Shortcut | Handler | Status |
|---|---|---|---|
| Toggle Explorer | none explicit | `toggle_explorer(bool)` | Implemented |
| Show Welcome | none explicit | `toggle_welcome_panel(bool)` | Disabled (no `welcome_dock`) |
| Increase Font Size | `Ctrl+Shift+=` | `increase_font_size` | Implemented |
| Decrease Font Size | `Ctrl+Shift+-` | `decrease_font_size` | Implemented |
| Toggle Fullscreen | `QKeySequence.FullScreen` (typically F11) | `toggle_fullscreen` | Implemented |

### Help menu

| Command | Shortcut | Handler | Status |
|---|---|---|---|
| About ViewMesh | none | `on_about` | Implemented |

### Non-obvious details

- Font actions also call `app_window.addAction(...)` to make shortcut handling global (`1571-1577`).
- Fullscreen action check-state is manually synchronized by finding action text `"Toggle &Fullscreen"` (`2984-2987`).
- Requested shortcut spec (`Ctrl+/-`) differs from implementation (`Ctrl+Shift+/-`).

## 5.7 Fullscreen and Maximization

### Interactions

- Trigger fullscreen from View menu or F11-equivalent shortcut.
- Toggle maximize/restore via title-bar button and title-bar double-click.

### Implementation

- Fullscreen: `toggle_fullscreen()` (`2971-2987`).
  - Records whether window was maximized before entering fullscreen.
  - Restores maximize icon text appropriately when leaving fullscreen.
- Maximize/restore: `toggle_maximize()` (`2930-2937`) and double-click path (`2920`).

## 5.8 Whole-App Font Size Adjustments

### Interactions

- Increase/decrease app-wide font size from View menu or keyboard shortcuts.

### Implementation

- State: `self.global_font_size_adjust` persisted in settings (`1788`, `2548`, `1153-1168`).
- Apply function: `_apply_global_font_change()` (`2323-2346`):
  - Computes point size relative to initial app font.
  - Calls `QApplication.setFont(...)`.
  - Ensures menu bar font catches up.
  - Recomputes title bar height.
  - Reapplies VS Code dark theme and processes events.

### Caveat

- Shortcuts are `Ctrl+Shift+=` and `Ctrl+Shift+-`, not plain `Ctrl+=`/`Ctrl+-`.

## 5.9 Explorer Panel and File Tree Interactions

### Interactions

- Browse file system via `QTreeView`.
- Double-click file emits `file_selected` signal.
- Toggle explorer visibility via View menu.
- Explorer toolbar buttons (Open Folder / Refresh / Collapse).

### Implementation

- `FileExplorerWidget` with `QFileSystemModel` and `QTreeView` (`1276+`).
- Root set from `initial_dir` (`1292-1299`).
- Double-click handler emits `file_selected` only for files (`1329-1333`).
- Explorer visibility toggle: `toggle_explorer(...)` (`2595-2597`).

### Caveats

- `file_selected` signal is not connected anywhere in `studio_app.py`.
- Single-click handler stores path but does nothing (`1325-1327`).
- Toolbar refresh/collapse actions have no connected handlers (`2022-2028`).
- `on_open_folder()` is placeholder (`2580-2583`).

## 5.10 Editor Tabs and Bottom Panel

### Interactions

- Editor tabs are movable and closable UI-wise.
- Bottom panel has Output and Terminal tabs.

### Implementation

- Editor tab widget config: `setTabsClosable(True)`, `setMovable(True)` (`2097-2099`).
- Placeholder tabs added by customizer (`1729-1731`).
- Bottom panel tabs configured at `2141+`, with placeholder text widgets.

### Caveats

- No `tabCloseRequested` signal handling found, so close button behavior is not wired.
- No editor document model/file loading implementation.

## 5.11 Status Bar (Bottom Status Line)

### Interactions

- Displays static/updated labels:
  - status message (`Ready` initially)
  - UTF-8
  - line/column
  - indentation mode
- `showMessage(...)` can update and optionally timeout-clear message text.

### Implementation

- Status bar setup: `setup_status_bar()` (`2626-2647`).
- Widgets added in customizer (`1733-1753`).
- Message API: `showMessage(...)` (`2613-2624`).

### Caveats

- Line/column and indent labels are static placeholders (no editor integration).

## 5.12 Inspector Window Interactions

Inspector open path currently comes from title-bar context menu "Open Inspector" (`2683`, `2726`).

### 5.12.1 Inspector open/close lifecycle

- Open:
  - `on_open_inspector()` creates singleton window if absent (`2989-2994`).
  - Calls inspector geometry restore after show.
- Close:
  - Inspector `closeEvent(...)` hides overlay, saves geometry/config, clears main pointer (`969-977`).
  - Main window close also closes inspector first (`2555-2558`).

### 5.12.2 Hierarchy tab

- Buttons:
  - "Refresh XML Hierarchy" -> `_refresh_xml_hierarchy_view()` (`583-585`, `668-672`)
  - "Show Visual Tree" -> `_refresh_visual_tree_view()` (`587-589`, `674-693`)
- XML generation:
  - `_generate_widget_hierarchy_xml()` + recursive `_build_widget_xml_string(...)` (`816-920`).
  - Captures class name, object name, text, title, geometry, and tab metadata.

### 5.12.3 Visual tree interactions

- Visual tree builds clickable/hoverable labels (`InteractiveHierarchyLabel`) for widget nodes.
- Hover enter/leave and click callbacks:
  - hover highlight: `_on_hierarchy_label_hover_enter/leave` (`930-955`)
  - sticky selection toggle on click: `_on_hierarchy_label_clicked` (`957-967`)

### Non-obvious mechanisms

- Overlay highlight is separate transparent child widget (`HighlightOverlay`) over main window.
- Coordinates mapped global->main local before drawing highlight rectangle (`412-415`).
- Sticky highlight state is preserved unless force-cleared.

### Caveats

- Visual tree line-art indentation logic is explicitly unfinished (`pass` markers around `763`, `807`).
- XML and child traversal emit debug prints unconditionally in several paths (`830`, `894`, `896`, and skip logs `745`, `747`), which can spam stdout.

## 5.13 Inspector Screenshot, Drawing, and Save-to-File

### Interactions

- "Take Screenshot"
- Draw with left mouse on screenshot
- "Clear Drawings"
- "Save Screenshot"

### Implementation

- Capture:
  - `main_app_window.grab()` in `_take_screenshot()` (`988`)
  - scales to viewport if needed (`994-1000`)
  - enables save/clear buttons on success (`1001-1002`)
- Drawing:
  - `DrawableScreenshotLabel` maintains `drawing_paths` and `current_path`.
  - Mouse handlers add path points (`519-547`).
  - Paint event overlays paths (`549-563`).
- Save:
  - file dialog via `QFileDialog.getSaveFileName(...)` (`1027-1032`)
  - persisted image created with base pixmap + translated paths (`502-517`)
  - write via `QPixmap.save(...)` with warning/critical dialogs on failures (`1020`, `1037`)

### Non-obvious / Caveats

- Screenshot saving includes annotation paths translated by an `offset`.
- Offset is computed with negative division in capture path (`996`, `999`), so save alignment
  behavior depends on that transform; this is non-trivial and potentially brittle.

## 5.14 Persistence and Restore Behavior

### Interactions

- On app exit: save window/settings state.
- On next run: restore geometry and selected state.

### Implementation

- `WindowGeometryManager` handles robust multi-screen geometry restore/save (`41-154`):
  - screen-name match
  - absolute-point containment fallback
  - relative-position fallback
  - boundary clamping into available geometry
- Main settings dataclass: `WindowSettings` (`1052+`)
- Inspector settings dataclass: `InspectorWindowSettings` (`1173+`)
- App config wrapper: `AppConfig.load/save` (`1258-1273`)

Main window restore sequence (`1802-1829`):

1. show window with opacity 0
2. restore geometry
3. process events
4. opacity back to 1
5. restore maximized state
6. restore saved Qt window state bytes if present
7. apply saved global font adjustment

Main window save sequence (`2536-2551`, `2553-2567`):

- save geometry
- save maximized flag
- save explorer width
- save `QMainWindow.saveState()` bytes
- save initial directory
- save global font adjust
- persist via `config.save()`

Inspector save on close (`969-977`) includes own geometry and config flush.

### Caveats

- `restore_window_state()` method itself is stubbed (`2529-2534`); restore logic moved elsewhere.
- `explorer_width` is persisted (`2544`) but explicit width reapply lines are commented out (`1815-1816`), so restoration relies on other state and may be incomplete.

## 5.15 Async Loop Integration

### Interactions

- No direct UI trigger in this file, but async scheduling helpers are present.

### Implementation

- Creates dedicated event loop + timer pump every 10ms (`2494-2502`).
- Each timer tick schedules one loop iteration (`2504-2514`).
- `schedule_async_task(...)` submits coroutines thread-safely (`2524-2527`).

### Caveats

- Async methods are not wired to user-facing commands in current implementation.

## 6. Implemented vs Partial vs Unimplemented Inventory

## 6.1 Implemented (core interactions)

- Frameless custom shell, title bar controls, title-bar dragging.
- Edge/corner resize handles.
- Context menu window commands incl. inspector open.
- Fullscreen toggle (F11 path via `QKeySequence.FullScreen`).
- Global font scaling actions and persisted font delta.
- Inspector:
  - XML hierarchy dump
  - visual tree labels
  - hover/sticky highlight overlay
  - screenshot capture
  - draw annotations
  - save annotated image
- About dialog.
- Main + inspector geometry/settings persistence.

## 6.2 Partial / Incomplete

- Visual tree branch-line rendering logic (explicit deferred `pass` sections).
- Explorer width persistence restore behavior likely incomplete (save exists, explicit restore commented).
- Tab closable UI enabled but no close signal handling implemented.
- Async framework present but no user workflows invoking it.
- Border present by stylesheet, but no runtime border toggle.

## 6.3 Unimplemented / Placeholder

- File operations: New/Open/Save/Save As handlers only show status message + TODO.
- Edit operations: Undo/Redo/Cut/Copy/Paste only show "not implemented".
- Explorer toolbar:
  - Refresh action has no trigger handler.
  - Collapse action has no trigger handler.
- Inspector Console tab is placeholder label only.
- Context-menu "Settings" shows "Settings not implemented yet".
- Welcome panel toggle references `welcome_dock`, which is absent; action disabled.
- `FileExplorerWidget.file_selected` is emitted but unused in this file.
- `InspectorWindow._restore_geometry_and_position` and `_save_geometry_and_position` are stubs.

## 7. Non-Obvious Technical Mechanisms (API-Level Notes)

- Win32 integration:
  - `ReleaseCapture`, `SendMessageW`, `PostMessageW` loaded on Windows (`1842-1845`).
  - System-drag and system-size commands use WM_SYSCOMMAND values (`2795-2797`, `2721-2722`).
- Highlight overlay:
  - Child overlay widget with `WA_TransparentForMouseEvents` and translucent background.
  - Rectangle painting via `QPainter` + `QPen`.
- Screenshot and drawing:
  - Main window capture via `QWidget.grab()`.
  - Drawing model via `QPainterPath`.
  - Save path uses `QStandardPaths.PicturesLocation` default suggestion.
- Persistence:
  - Uses `QSettings(org_name, app_name)`.
  - Serializes tuple-like values as strings for robustness (`window/relative_position`, `window/screen_geometry` etc.).
- Font scaling:
  - Global font set with `QApplication.setFont`.
  - Menu bar height recalculated to keep custom title bar sized correctly.

## 8. Requested Requirement Delta Notes

These are specific deltas relative to requested expectations in your prompt:

1. Border toggle: not present.
2. Font shortcuts: implemented, but with `Ctrl+Shift` modifier, not plain `Ctrl`.
3. Fullscreen F11: present via `QKeySequence.FullScreen`.
4. Help > About: present and wired.
5. Inspector graph/screenshot/drawing/save: present and substantially implemented.
6. Persistence/restore: present and non-trivial (multi-screen aware).

## 9. Baseline Conclusions for PyRolyze Migration Planning

- The current app already demonstrates rich interaction surfaces and persistence behavior
  that must be preserved in migration.
- The highest-value parity surfaces are:
  - frameless window interactions (move/resize/context commands),
  - inspector highlight/screenshot tooling,
  - settings restore/save.
- Many editor/file workflow commands are placeholders, so parity can preserve current
  placeholder behavior before introducing new functionality.

## 10. Exhaustive Interaction Matrix

Legend:

- Implemented = behavior exists and is wired.
- Partial = wired but incomplete, constrained, or only cosmetic.
- Placeholder = wired to message/stub without functional outcome.
- Dead/Unused = code exists but no active trigger path in this file.

| ID | Interaction Surface | Trigger | Handler/Path | Status | Notes |
|---|---|---|---|---|---|
| I-001 | CLI initial directory | launch arg `--dir` | `parse_args` -> `main` | Implemented | Only applies if path exists. |
| I-002 | Main window create | app launch | `StudioMainWindow.__init__` | Implemented | Frameless via `Qt.FramelessWindowHint`. |
| I-003 | Restore main geometry | startup | `geometry_manager.restore_geometry` | Implemented | Multi-screen aware with fallback + clamping. |
| I-004 | Restore maximized state | startup | `if settings.is_maximized: showMaximized` | Implemented | Applied after geometry. |
| I-005 | Restore Qt state blob | startup | `restoreState(settings.state)` | Partial | May not cover custom splitter state semantics. |
| I-006 | Restore global font adjust | startup | `_apply_global_font_change` | Implemented | Persists integer delta. |
| I-007 | Minimize button | click | `showMinimized` | Implemented | Custom title bar button. |
| I-008 | Maximize button | click | `toggle_maximize` | Implemented | Updates icon glyph. |
| I-009 | Close button | click | `close` | Implemented | Triggers state save sequence. |
| I-010 | Title-bar drag | left click + move on non-control area | `mousePressEvent`/`mouseMoveEvent` | Implemented | Win32 system move preferred when available. |
| I-011 | Title-bar double-click | double-click on non-control area | `mouseDoubleClickEvent` | Implemented | Toggles maximize/restore. |
| I-012 | Title-bar context menu open | right click title bar | `show_title_bar_context_menu` | Implemented | Uses `QMenu.exec` at global mapped pos. |
| I-013 | Context restore | menu item click | `showNormal` + icon update | Implemented | Only appears if maximized. |
| I-014 | Context maximize | menu item click | `showMaximized` + icon update | Implemented | Only appears if not maximized. |
| I-015 | Context move mode | menu item click | timer + `grabMouse` + `_perform_context_menu_move` | Implemented | Ends on next mouse press via `eventFilter`. |
| I-016 | Context size mode | menu item click | Win32 `SendMessage(...SC_SIZE...)` | Partial | Windows-only path; no non-Windows fallback. |
| I-017 | Context open inspector | menu item click | `on_open_inspector` | Implemented | Primary entrypoint to Inspector. |
| I-018 | Context open file | menu item click | `on_open_file` | Placeholder | Status message only. |
| I-019 | Context open folder | menu item click | `on_open_folder` | Placeholder | Status message only. |
| I-020 | Context settings | menu item click | `showMessage("Settings not implemented yet")` | Placeholder | No settings dialog. |
| I-021 | Context minimize | menu item click | `showMinimized` | Implemented | Standard behavior. |
| I-022 | Context close | menu item click | `close` | Implemented | Standard behavior. |
| I-023 | Edge resize cursor hints | hover on handle widgets | `EdgeResizeHandle.enterEvent/leaveEvent` | Implemented | Cursor set on parent window. |
| I-024 | Edge/corner resize | drag edge handles | `EdgeResizeHandle.mouse*Event` | Implemented | 8 handles, geometry math per direction. |
| I-025 | Window resize fallback cursor logic | mouse move near edges | `get_resize_direction/get_resize_cursor` | Partial | Cursor hints only; resize action is handle-driven. |
| I-026 | File menu New | click or shortcut | `on_new_file` | Placeholder | Displays "Creating new file...". |
| I-027 | File menu Open File | click or shortcut | `on_open_file` | Placeholder | Displays "Opening file...". |
| I-028 | File menu Open Folder | click | `on_open_folder` | Placeholder | Displays "Opening folder...". |
| I-029 | File menu Save | click or shortcut | `on_save` | Placeholder | Displays "Saving file...". |
| I-030 | File menu Save As | click or shortcut | `on_save_as` | Placeholder | Displays "Saving file as...". |
| I-031 | File menu Exit | click or shortcut | `close` | Implemented | Initiates closeEvent save path. |
| I-032 | Edit menu Undo | click or shortcut | lambda -> `showMessage` | Placeholder | "Undo not implemented". |
| I-033 | Edit menu Redo | click or shortcut | lambda -> `showMessage` | Placeholder | "Redo not implemented". |
| I-034 | Edit menu Cut | click or shortcut | lambda -> `showMessage` | Placeholder | "Cut not implemented". |
| I-035 | Edit menu Copy | click or shortcut | lambda -> `showMessage` | Placeholder | "Copy not implemented". |
| I-036 | Edit menu Paste | click or shortcut | lambda -> `showMessage` | Placeholder | "Paste not implemented". |
| I-037 | View menu toggle explorer | click | `toggle_explorer` | Implemented | Shows/hides explorer container. |
| I-038 | View menu show welcome | click | `toggle_welcome_panel` | Dead/Unused | Disabled because `welcome_dock` absent. |
| I-039 | Increase font size | click or shortcut `Ctrl+Shift+=` | `increase_font_size` | Implemented | Global app font + relayout. |
| I-040 | Decrease font size | click or shortcut `Ctrl+Shift+-` | `decrease_font_size` | Implemented | Lower-bounded to point size >= 1. |
| I-041 | Toggle fullscreen | click or `QKeySequence.FullScreen` | `toggle_fullscreen` | Implemented | F11 on common platforms. |
| I-042 | Help About | click | `on_about` -> `QMessageBox.about` | Implemented | Modal HTML content dialog. |
| I-043 | Explorer toolbar Open Folder | click icon | `on_open_folder` | Placeholder | Same placeholder path as File menu. |
| I-044 | Explorer toolbar Refresh | click icon | no trigger connection | Dead/Unused | Tooltip only. |
| I-045 | Explorer toolbar Collapse | click icon | no trigger connection | Dead/Unused | Tooltip only. |
| I-046 | Explorer tree single-click | click row | `_on_item_clicked` | Partial | Resolves path but no effect. |
| I-047 | Explorer tree double-click file | double click row | `_on_item_double_clicked` -> `file_selected.emit` | Partial | Signal emitted but not connected in file. |
| I-048 | Editor tab reorder | drag tab | `QTabWidget.setMovable(True)` | Partial | Visual behavior, no persistence semantics. |
| I-049 | Editor tab close icon | click tab close | `setTabsClosable(True)` without close signal handler | Partial | No custom close handling wired. |
| I-050 | Splitter drag (left/right) | drag handle | `QSplitter` native behavior | Implemented | Handle width auto-adjusts on splitterMoved. |
| I-051 | Splitter width auto-adjust | splitter moved | `_adjust_splitter_handle_width` | Implemented | Wider handle when one side nearly hidden. |
| I-052 | Bottom panel tab switch | click Output/Terminal tabs | `QTabWidget` native behavior | Implemented | Content is placeholder text widgets. |
| I-053 | Status message update | code path calls `showMessage` | `showMessage` | Implemented | Optional timeout clear via `QTimer.singleShot`. |
| I-054 | Inspector open | context menu "Open Inspector" | `on_open_inspector` | Implemented | Singleton behavior. |
| I-055 | Inspector reopen focus | open when existing | `show` + `activateWindow` | Implemented | Reuses existing instance. |
| I-056 | Inspector refresh XML | click button | `_refresh_xml_hierarchy_view` | Implemented | Populates read-only `QTextEdit`. |
| I-057 | Inspector show visual tree | click button | `_refresh_visual_tree_view` | Partial | Functional tree list; line-art indentation unfinished. |
| I-058 | Visual tree node hover enter | hover label | `InteractiveHierarchyLabel.enterEvent` | Implemented | Emits signal to inspector hover handler. |
| I-059 | Visual tree node hover leave | leave label | `InteractiveHierarchyLabel.leaveEvent` | Implemented | Restores sticky or clears highlight. |
| I-060 | Visual tree node click | click label | `InteractiveHierarchyLabel.mousePressEvent` | Implemented | Toggles sticky highlight state. |
| I-061 | Overlay highlight draw | hover/click interactions | `HighlightOverlay.paintEvent` | Implemented | Draws red rect around target widget bounds. |
| I-062 | Inspector screenshot capture | click button | `_take_screenshot` | Implemented | Captures main window and scales to viewport. |
| I-063 | Inspector screenshot draw stroke start | left mouse down on image | `DrawableScreenshotLabel.mousePressEvent` | Implemented | Starts `QPainterPath`. |
| I-064 | Inspector screenshot draw stroke continue | mouse move with button | `DrawableScreenshotLabel.mouseMoveEvent` | Implemented | Live path update/repaint. |
| I-065 | Inspector screenshot draw stroke end | left mouse release | `DrawableScreenshotLabel.mouseReleaseEvent` | Implemented | Commits path to `drawing_paths`. |
| I-066 | Inspector clear drawings | click button | `_clear_drawings_on_label` | Implemented | Clears path list only. |
| I-067 | Inspector save screenshot | click button | `_save_screenshot` | Implemented | File dialog + save; warning/critical dialogs on failure. |
| I-068 | Inspector console tab | click tab | static label only | Placeholder | No console integration. |
| I-069 | Main close saves state | window close | `closeEvent` -> `save_window_state` | Implemented | Saves geometry, flags, state bytes, dir, font adjust. |
| I-070 | Inspector close saves state | inspector close | `InspectorWindow.closeEvent` | Implemented | Saves inspector geometry and clears main ref. |
| I-071 | Async task schedule API | programmatic call | `schedule_async_task` | Partial | API exists; no user-facing command uses it. |
| I-072 | CustomWindowFrame interaction model | class methods and mouse handler | `CustomWindowFrame` | Dead/Unused | Declared but not instantiated in current app setup. |

## 11. Captured Graph Dump Snapshot (User-Provided)

This is the exact runtime graph/XML snapshot you provided from the app's graph
dump feature.

```xml
<StudioMainWindow name="ViewMeshAppMainWindow" windowTitle="ViewMesh" geometry="(39,135,2171,1200)">
  <QWidget geometry="(0,0,2171,1162)">
    <QWidget name="custom_title_bar_widget" geometry="(1,1,2169,35)">
      <QLabel text="🪟" geometry="(0,8,18,18)" />
      <QMenuBar name="title_bar_menu_bar_widget" geometry="(21,0,2028,35)">
        <QToolButton name="qt_menubar_ext_button" geometry="(2015,0,12,24)" />
        <QMenu geometry="(66,167,280,236)" />
        <QMenu geometry="(0,0,100,30)" />
        <QMenu geometry="(193,156,166,196)" />
        <QMenu geometry="(248,156,358,193)" />
        <QMenu geometry="(236,167,199,45)" />
      </QMenuBar>
      <QPushButton text="─" geometry="(2049,7,40,20)" />
      <QPushButton text="□" geometry="(2089,7,40,20)" />
      <QPushButton name="close_button" text="✕" geometry="(2129,7,40,20)" />
    </QWidget>
    <QWidget geometry="(1,36,2169,1125)">
      <QSplitter geometry="(0,0,2169,1125)">
        <QWidget geometry="(545,0,1624,1125)">
          <QSplitter geometry="(0,0,1624,1125)">
            <QWidget geometry="(0,820,1624,305)">
              <QTabWidget geometry="(0,0,1624,305)">
                <Tab index="0" title="Output" />
                <Tab index="1" title="Terminal" />
                <QStackedWidget name="qt_tabwidget_stackedwidget" geometry="(1,36,1622,268)">
                  <QWidget geometry="(0,0,1622,268)">
                    <QTextEdit geometry="(8,8,1606,252)">
                      <QWidget name="qt_scrollarea_viewport" geometry="(0,0,1606,252)" />
                      <QWidget name="qt_scrollarea_hcontainer" geometry="(0,0,100,30)">
                        <QScrollBar geometry="(0,0,100,30)" />
                      </QWidget>
                      <QWidget name="qt_scrollarea_vcontainer" geometry="(0,0,100,30)">
                        <QScrollBar geometry="(0,0,100,30)" />
                      </QWidget>
                    </QTextEdit>
                  </QWidget>
                  <QWidget geometry="(0,0,1622,268)">
                    <QTextEdit geometry="(8,8,1606,252)">
                      <QWidget name="qt_scrollarea_viewport" geometry="(0,0,1606,252)" />
                      <QWidget name="qt_scrollarea_hcontainer" geometry="(0,0,100,30)">
                        <QScrollBar geometry="(0,0,100,30)" />
                      </QWidget>
                      <QWidget name="qt_scrollarea_vcontainer" geometry="(0,0,100,30)">
                        <QScrollBar geometry="(0,0,100,30)" />
                      </QWidget>
                    </QTextEdit>
                  </QWidget>
                </QStackedWidget>
                <QTabBar name="qt_tabwidget_tabbar" geometry="(0,0,192,36)">
                  <QToolButton name="ScrollLeftButton" geometry="(113,0,16,26)" />
                  <QToolButton name="ScrollRightButton" geometry="(128,0,16,26)" />
                </QTabBar>
              </QTabWidget>
            </QWidget>
            <QWidget geometry="(0,0,1624,815)">
              <QTabWidget geometry="(0,0,1624,815)">
                <Tab index="0" title="Editor 1" />
                <Tab index="1" title="Editor 2" />
                <Tab index="2" title="Welcome" />
                <QStackedWidget name="qt_tabwidget_stackedwidget" geometry="(0,40,1624,775)">
                  <QWidget geometry="(0,0,1624,775)">
                    <QLabel text="Welcome to ViewMesh" geometry="(0,0,1624,67)" />
                  </QWidget>
                  <QWidget geometry="(0,0,1624,775)">
                    <QLabel text="Editor Tab 2 Content" geometry="(9,9,1606,757)" />
                  </QWidget>
                  <QWidget geometry="(0,0,1624,775)">
                    <QLabel text="Editor Tab 1 Content" geometry="(9,9,1606,757)" />
                  </QWidget>
                </QStackedWidget>
                <QTabBar name="qt_tabwidget_tabbar" geometry="(0,0,1624,40)">
                  <CloseButton geometry="(338,12,16,16)" />
                  <CloseButton geometry="(211,12,16,16)" />
                  <CloseButton geometry="(97,12,16,16)" />
                  <QToolButton name="ScrollLeftButton" geometry="(0,0,100,30)" />
                  <QToolButton name="ScrollRightButton" geometry="(0,0,100,30)" />
                </QTabBar>
              </QTabWidget>
            </QWidget>
            <QSplitterHandle name="qt_splithandle_" geometry="(0,0,100,30)" />
            <QSplitterHandle name="qt_splithandle_" geometry="(0,814,1624,7)" />
          </QSplitter>
        </QWidget>
        <QWidget geometry="(0,0,542,1125)">
          <QToolBar name="explorer_toolbar" windowTitle="Explorer Toolbar" geometry="(0,0,542,46)">
            <QToolBarExtension name="qt_toolbar_ext_button" geometry="(0,0,100,30)">
              <QMenu geometry="(0,0,100,30)" />
            </QToolBarExtension>
            <QToolButton text="📂" geometry="(2,2,53,42)" />
            <QToolButton text="🔄" geometry="(57,2,53,42)" />
            <QToolButton text="◀" geometry="(112,2,35,42)" />
          </QToolBar>
          <QWidget geometry="(0,46,542,1079)">
            <CustomTitleBar geometry="(0,0,542,24)">
              <QLabel text="📁" geometry="(8,2,20,20)" />
              <QLabel text="EXPLORER" geometry="(32,2,99,20)" />
            </CustomTitleBar>
            <FileExplorerWidget geometry="(0,24,542,1055)">
              <QTreeView geometry="(0,0,542,1055)">
                <QWidget name="qt_scrollarea_viewport" geometry="(2,2,538,1051)" />
                <QWidget name="qt_scrollarea_hcontainer" geometry="(0,0,100,30)">
                  <QScrollBar geometry="(0,0,100,30)" />
                </QWidget>
                <QWidget name="qt_scrollarea_vcontainer" geometry="(0,0,100,30)">
                  <QScrollBar geometry="(0,0,100,30)" />
                </QWidget>
                <QHeaderView geometry="(2,2,538,0)">
                  <QWidget name="qt_scrollarea_viewport" geometry="(0,0,538,0)" />
                  <QWidget name="qt_scrollarea_hcontainer" geometry="(0,0,100,30)">
                    <QScrollBar geometry="(0,0,100,30)" />
                  </QWidget>
                  <QWidget name="qt_scrollarea_vcontainer" geometry="(0,0,100,30)">
                    <QScrollBar geometry="(0,0,100,30)" />
                  </QWidget>
                </QHeaderView>
              </QTreeView>
            </FileExplorerWidget>
          </QWidget>
        </QWidget>
        <QSplitterHandle name="qt_splithandle_" geometry="(0,0,100,30)" />
        <QSplitterHandle name="qt_splithandle_" geometry="(540,0,7,1125)" />
      </QSplitter>
    </QWidget>
  </QWidget>
  <QStatusBar name="status_bar" geometry="(0,1162,2171,38)">
    <QLabel name="encoding_label" text="UTF-8" geometry="(1851,3,79,33)" />
    <QLabel name="line_col_label" text="Ln 1, Col 1" geometry="(1936,3,118,33)" />
    <QLabel name="indent_label" text="Spaces: 4" geometry="(2060,3,111,33)" />
    <QLabel name="status_message" text="Opening folder..." geometry="(2,3,172,33)" />
  </QStatusBar>
  <QMenu geometry="(791,136,185,276)">
    <QMenu geometry="(0,0,100,30)" />
  </QMenu>
  <HighlightOverlay geometry="(0,0,2171,1200)" />
  <EdgeResizeHandle name="" geometry="(0,0,5,5)" position="TOP_LEFT" />
  <EdgeResizeHandle name="" geometry="(5,0,2161,5)" position="TOP" />
  <EdgeResizeHandle name="" geometry="(2166,0,5,5)" position="TOP_RIGHT" />
  <EdgeResizeHandle name="" geometry="(0,5,5,1190)" position="LEFT" />
  <EdgeResizeHandle name="" geometry="(2166,5,5,1190)" position="RIGHT" />
  <EdgeResizeHandle name="" geometry="(0,1195,5,5)" position="BOTTOM_LEFT" />
  <EdgeResizeHandle name="" geometry="(5,1195,2161,5)" position="BOTTOM" />
  <EdgeResizeHandle name="" geometry="(2166,1195,5,5)" position="BOTTOM_RIGHT" />
  <QMenu geometry="(515,151,185,276)">
    <QMenu geometry="(694,302,171,122)" />
  </QMenu>
  <QMenu geometry="(541,150,185,276)">
    <QMenu geometry="(720,301,171,122)" />
  </QMenu>
  <QMenu geometry="(533,149,185,276)">
    <QMenu geometry="(712,300,171,122)" />
  </QMenu>
  <QMenu geometry="(420,158,185,276)">
    <QMenu geometry="(0,0,100,30)" />
  </QMenu>
  <QMenu geometry="(387,151,185,276)">
    <QMenu geometry="(566,302,171,122)" />
  </QMenu>
  <HighlightOverlay geometry="(0,0,2171,1200)" />
</StudioMainWindow>
```

### 11.1 Notes on the Snapshot

- Confirms the custom frameless shell structure with `custom_title_bar_widget`,
  title-bar menu bar, and custom minimize/maximize/close buttons.
- Confirms splitter-based main workspace composition:
  - left explorer region
  - right editor+bottom panel split.
- Confirms status-bar labels present (`encoding_label`, `line_col_label`,
  `indent_label`, `status_message`) and shows a live placeholder message.
- Confirms edge-resize handles exist for all 8 directions/corners.
- Confirms `HighlightOverlay` appears in dump output (twice in this capture),
  matching overlay/highlight subsystem behavior noted in the baseline.
