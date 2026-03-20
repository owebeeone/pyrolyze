# Studio System Requirements Specification

Document ID: `SRS-STUDIO-001`  
Version: `1.1`  
Date: `2026-03-20`  
Project Root: `Studio/`  
Primary Target Stack: `PyRolyze (@pyrolyse) + PySide6`

## 1. Purpose

This document defines the system requirements for recreating `examples/studio_app.py`
as a maintainable Studio implementation rooted in `Studio/`, using:

- PyRolyze for declarative UI/state rendering
- PySide6 for native host windowing and platform integration

The requirements in this document are the implementation contract for Studio work.

## 2. Scope

### 2.1 In Scope

- Functional parity (or intentional superset) of `studio_app.py` core UX:
  - main window shell
  - explorer/content/panel workspace layout
  - tabs and status/menu actions
  - inspector workflow (hierarchy, visual tree, screenshot workflow)
  - persisted user settings
- A clean architecture that separates:
  - host window chrome/native behavior
  - declarative PyRolyze content
  - app services/state management
- Required PyRolyze capabilities needed to implement Studio without reverting to monolithic imperative UI construction.

### 2.2 Out of Scope (Initial Delivery)

- Full IDE feature set (language servers, debugger integration, terminal emulation, etc.)
- Plugin marketplace/runtime
- Multi-user collaboration features
- Cloud synchronization

## 3. Goals and Quality Objectives

1. Deliver a Studio implementation that preserves user-visible behavior while reducing architectural coupling.
2. Enforce clear separation of concerns between host shell, declarative UI, and domain/service logic.
3. Ensure reconciliation/runtime performance is adequate for large trees without UI freezing.
4. Keep development TDD-first in line with repository process rules.

## 4. Baseline Reference

Current behavior reference implementation:  
[`examples/studio_app.py`](C:/Users/adria/Documents/Projects/py-rolyze-wip/examples/studio_app.py)

Source-truth baseline analysis:  
[`Studio App Spec Baseline.md`](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/Studio%20App%20Spec%20Baseline.md)

### 4.1 Baseline Intent Rules

- Migration SHALL treat the baseline document as behavior truth for current app semantics.
- Delivery SHALL distinguish:
  - `baseline parity` (match current behavior, including placeholders where they exist),
  - `intentional improvements` (explicitly tracked as deltas).
- Work items SHALL not silently convert baseline placeholders into assumed completed features.

## 5. System Context and Architecture Boundaries

## 5.1 Target Logical Components

1. `Studio Host Shell` (PySide6 native)
2. `Studio Declarative UI` (PyRolyze components)
3. `Studio State + Actions` (pure application logic)
4. `Studio Services` (filesystem, screenshot, hierarchy capture, settings)
5. `PyRolyze Runtime/Compiler` extensions required by Studio

## 5.2 Boundary Rules

- Native window frame/chrome concerns SHALL remain in the host shell.
- App content composition SHOULD be expressed declaratively in PyRolyze components.
- Business/state logic SHALL be independent from widget classes and Qt event objects where feasible.
- Platform-specific behavior (Win32 drag/resize semantics) SHALL be encapsulated in host adapters.

## 6. Functional Requirements (Product)

### 6.1 Window Shell and Chrome

- `FR-SHELL-001`: The system SHALL provide a frameless main window with custom title bar controls (minimize, maximize/restore, close).
- `FR-SHELL-002`: The system SHALL support mouse-driven window move behavior from non-control title-bar regions.
- `FR-SHELL-003`: The system SHALL support edge/corner resize behavior for frameless mode.
- `FR-SHELL-004`: The system SHALL preserve platform-safe fallback behavior when native APIs are unavailable.
- `FR-SHELL-005`: The system SHALL provide title-bar context menu actions including move/size/maximize/restore/minimize/close and inspector open.

### 6.2 Main Workspace Layout

- `FR-LAYOUT-001`: The system SHALL provide a left explorer panel and right content panel split horizontally.
- `FR-LAYOUT-002`: The right content panel SHALL contain editor tabs and a bottom panel split vertically.
- `FR-LAYOUT-003`: The bottom panel SHALL provide at least Output and Terminal tabs.
- `FR-LAYOUT-004`: Splitter positions SHALL be user-adjustable and persisted.
- `FR-LAYOUT-005`: Explorer visibility SHALL be toggleable via menu action.

### 6.3 Explorer

- `FR-EXPLORER-001`: The system SHALL display a file-tree explorer rooted at a configurable directory.
- `FR-EXPLORER-002`: Double-clicking a file entry SHALL emit/open file intent.
- `FR-EXPLORER-003`: The explorer root path SHALL be changeable at runtime.
- `FR-EXPLORER-004`: Explorer toolbar actions SHALL be available for open/refresh/collapse intents.

### 6.4 Editor and Panel Tabs

- `FR-TABS-001`: The system SHALL support add, close, reorder, and activate behaviors for editor tabs.
- `FR-TABS-002`: The system SHALL preserve tab-local UI state across reorder operations when identity is unchanged.
- `FR-TABS-003`: Bottom panel tabs SHALL support switching without remounting unrelated content.

### 6.5 Menus, Actions, and Status Bar

- `FR-CMD-001`: File/Edit/View/Help menus SHALL be supported with action wiring.
- `FR-CMD-002`: The system SHALL expose font-size increase/decrease commands.
- `FR-CMD-003`: The system SHALL support fullscreen toggle command with consistent action state.
- `FR-CMD-004`: Status bar SHALL expose primary message area plus permanent widgets (encoding, cursor position, indentation or equivalent).

### 6.6 Inspector

- `FR-INSP-001`: The system SHALL provide an inspector window linked to the main window.
- `FR-INSP-002`: Inspector SHALL include hierarchy and visual-tree presentation modes.
- `FR-INSP-003`: Hovering hierarchy rows SHALL highlight target widgets in the main window.
- `FR-INSP-004`: Clicking a hierarchy row SHALL toggle sticky highlighting state.
- `FR-INSP-005`: Inspector SHALL include screenshot capture of main window content.
- `FR-INSP-006`: Users SHALL be able to draw annotations over captured screenshots.
- `FR-INSP-007`: Annotated screenshot SHALL be savable to user-selected path.

### 6.7 Persistence and Startup/Shutdown

- `FR-PERSIST-001`: Main window position/size/maximize state SHALL persist across sessions.
- `FR-PERSIST-002`: Multi-screen restore SHALL place windows on valid visible screens with safe fallback logic.
- `FR-PERSIST-003`: Explorer width/root-path and relevant UI state SHALL persist.
- `FR-PERSIST-004`: Inspector geometry/state SHALL persist independently from main window.
- `FR-PERSIST-005`: On close, window and app state SHALL be saved before process exit.

### 6.8 Async Task Integration

- `FR-ASYNC-001`: The system SHALL support scheduling asynchronous operations from UI actions.
- `FR-ASYNC-002`: Async completion SHALL update UI through approved UI-thread-safe invalidation/reconciliation flow.

### 6.9 Baseline Conformance and Gap Closure

- `FR-BASE-001`: The implementation SHALL maintain a traceable mapping from baseline interaction IDs (`I-*`) to Studio implementation status.
- `FR-BASE-002`: Placeholder behavior in the baseline (for example File/Edit command stubs) SHALL be explicitly marked as either:
  - parity-preserved placeholder, or
  - upgraded behavior with acceptance criteria.
- `FR-BASE-003`: The implementation SHALL resolve baseline-known correctness defects before milestone freeze, including:
  - invalid sync entrypoint use via `asyncio.run(...)` pattern in source baseline,
  - non-portable title-bar size behavior without fallback,
  - persistence stub methods identified in baseline analysis.
- `FR-BASE-004`: Keyboard shortcut decisions SHALL be explicit (for example plain `Ctrl+=/-` vs `Ctrl+Shift+=/-`) and test-covered.
- `FR-BASE-005`: Border/chrome behavior SHALL specify whether runtime border-toggle is in scope; if out of scope, this SHALL be documented as a deferred delta.

## 7. PyRolyze Enablement Requirements (Framework Prerequisites)

These requirements are blockers for implementing Studio content declaratively.

### 7.1 Semantic Node Model Extensions

- `PR-NODE-001`: PyRolyze SHALL support semantic nodes required by Studio layouts:
  - `splitter` (horizontal, vertical)
  - `tabs`
  - `tab_page`
  - `toolbar_row`
  - `text_area`
  - `container`
- `PR-NODE-002`: Each new node kind SHALL be implemented across:
  - descriptor contract/normalization
  - reconciliation behavior
  - PySide6 bindings

### 7.2 Tree/Model Binding Support

- `PR-TREE-001`: PyRolyze SHALL support model-backed tree rendering suitable for explorer/hierarchy use cases.
- `PR-TREE-002`: Tree semantics SHALL expose stable row identity keys for selection/activation consistency.
- `PR-TREE-003`: Tree bindings SHALL support runtime root-path or model-source updates without full unrelated remount.

### 7.3 Host Shell Interop

- `PR-HOST-001`: PyRolyze integration SHALL define a stable mount-point contract for host-managed `QMainWindow` regions.
- `PR-HOST-002`: Host shell actions (menu/status/title-bar commands) SHALL dispatch into declarative state/action boundaries via explicit adapters.
- `PR-HOST-003`: Host-native and declarative ownership boundaries SHALL be documented and test-covered.

### 7.4 Custom Widget Bridge

- `PR-BRIDGE-001`: PyRolyze SHALL provide a supported bridge pattern for host-owned custom widgets participating in declarative flows.
- `PR-BRIDGE-002`: Bridge contract SHALL define create/update/dispose lifecycle semantics.
- `PR-BRIDGE-003`: Bridge implementation SHALL prevent remount leaks under repeated reconciliation passes.

### 7.5 Tab Lifecycle and Identity

- `PR-TABS-001`: Reconciliation SHALL preserve tab widget identity when stable keys remain unchanged.
- `PR-TABS-002`: Reorder-heavy tab operations SHALL not trigger unnecessary widget reconstruction.
- `PR-TABS-003`: Active-tab state changes SHALL be diffed/applied without remounting sibling tabs.

### 7.6 Async/UI Boundary

- `PR-ASYNC-001`: PyRolyze runtime SHALL provide a first-class UI-thread-safe post-completion invalidation pathway.
- `PR-ASYNC-002`: Off-thread UI mutation attempts SHALL fail fast or be marshalled safely to UI thread.

## 8. Non-Functional Requirements

### 8.1 Performance

- `NFR-PERF-001`: Typical UI interactions (tab switch, splitter drag, explorer expand) SHOULD remain visually responsive on mid-range hardware.
- `NFR-PERF-002`: Reconciliation for reorder/replace-heavy updates SHALL avoid known O(n^2) hotspots where practical.
- `NFR-PERF-003`: Inspector hover/highlight operations SHALL avoid UI freezes in large widget trees.
- `NFR-PERF-004`: Performance regression tests for Studio-shaped trees SHALL be added before Studio feature lock.
- `NFR-PERF-005`: Performance acceptance SHALL include measurable guardrails:
  - tab reorder on 100 tabs: p95 reconcile commit under 25 ms,
  - inspector hover transitions on 2,000-node tree: p95 update under 40 ms,
  - explorer refresh on 2,000 entries (model update path): no UI stall over 100 ms on test baseline hardware.

### 8.2 Reliability

- `NFR-REL-001`: The system SHALL degrade safely when optional platform APIs (e.g., Win32 calls) are unavailable.
- `NFR-REL-002`: Persisted settings parsing SHALL be robust to invalid/missing values with deterministic fallback.

### 8.3 Maintainability

- `NFR-MNT-001`: Studio implementation SHALL separate host shell, declarative UI, and services into distinct modules under `Studio/`.
- `NFR-MNT-002`: New behavior SHALL be implemented with strict red/green/refactor cycle and relevant tests first.
- `NFR-MNT-003`: Requirement IDs in this document SHOULD be referenced in implementation planning and PR descriptions.

### 8.4 Testability

- `NFR-TST-001`: Every new Studio-required node or bridge behavior SHALL have unit/integration test coverage.
- `NFR-TST-002`: Reconciliation identity behavior SHALL be validated by reuse/reorder/removal tests.
- `NFR-TST-003`: Focused tests SHALL pass before full-suite execution.
- `NFR-TST-004`: Baseline parity tests SHALL exist for key interactions (window shell, explorer activation intent, menu/status actions, inspector hover/screenshot/save flow, persistence restore).

## 9. Data and Configuration Requirements

- `CFG-001`: Existing user settings keys SHOULD remain backward compatible where practical.
- `CFG-002`: New Studio settings keys SHALL be namespace-prefixed to avoid collisions.
- `CFG-003`: Configuration defaults SHALL permit first-run startup without user input.
- `CFG-004`: Saved paths SHALL be normalized for platform consistency.

## 10. Implementation Structure Requirements (Studio Root)

All Studio implementation assets SHALL be organized under `Studio/`.

Minimum expected structure:

```text
Studio/
  Studio_System_Requirements.md
  Studio App Spec Baseline.md
  architecture/
    Studio_Architecture.md
  host/
    app_host.py
    window_chrome.py
    menu_bridge.py
    status_bar_bridge.py
  app/
    models.py
    state.py
    actions.py
    reducers.py
    selectors.py
    commands.py
  services/
    settings_service.py
    filesystem_service.py
    hierarchy_service.py
    screenshot_service.py
    async_service.py
  ui/
    studio_root.py
    node_contracts.py
    theme.py
    components/
      workspace.py
      explorer_panel.py
      editor_tabs.py
      bottom_panel.py
      inspector_panel.py
      status_widgets.py
  bridges/
    host_widget_bridge.py
    qtree_bridge.py
    tabs_bridge.py
    splitter_bridge.py
  runtime_ext/
    pyside6_bindings.py
    ui_descriptors.py
    reconcile_helpers.py
    event_threading.py
  docs/
    baseline_parity_map.md
  tests/
    unit/test_*.py
    integration/test_*.py
    perf/test_*.py
```

Notes:

- Names above are normative targets, not strict final filenames.
- Any deviation SHALL preserve the same responsibility split.

## 11. Verification and Acceptance Criteria

### 11.1 TDD Gate (Repository Process Compliance)

- `AC-TDD-001`: For each behavior change, tests SHALL be added/updated first and shown failing before implementation.
- `AC-TDD-002`: After minimal implementation, focused tests SHALL pass.
- `AC-TDD-003`: Full regression suite SHALL pass before Studio milestone completion.

### 11.2 Product Acceptance

- `AC-PROD-001`: Main shell/window interactions satisfy `FR-SHELL-*`.
- `AC-PROD-002`: Workspace layout and tab behavior satisfy `FR-LAYOUT-*` and `FR-TABS-*`.
- `AC-PROD-003`: Explorer and command surfaces satisfy `FR-EXPLORER-*` and `FR-CMD-*`.
- `AC-PROD-004`: Inspector and screenshot behaviors satisfy `FR-INSP-*`.
- `AC-PROD-005`: Persistence behavior satisfies `FR-PERSIST-*`.
- `AC-PROD-006`: Baseline conformance requirements satisfy `FR-BASE-*`.

### 11.3 Framework Enablement Acceptance

- `AC-FW-001`: Required node set (`PR-NODE-*`) is implemented and test-covered.
- `AC-FW-002`: Host interop and custom widget bridge (`PR-HOST-*`, `PR-BRIDGE-*`) are implemented and test-covered.
- `AC-FW-003`: Async/UI boundary and performance safeguards (`PR-ASYNC-*`, `NFR-PERF-*`) are implemented and validated.

## 12. Risks and Constraints

### 12.1 Technical Risks

- Frameless cross-platform behavior differs across OS/window managers.
- Complex tree and tab reconciliation can regress into high-order runtime costs if identity rules are weak.
- Mixing host-owned widgets and declarative ownership without strict lifecycle contracts can cause leaks/remount churn.

### 12.2 Constraint Summary

- Studio content migration depends on PyRolyze framework capabilities listed in Section 7.
- Development SHALL prioritize framework prerequisites before deep feature migration.

## 13. Traceability Summary

- App behavior requirements: Section 6 (`FR-*`)
- Framework prerequisites: Section 7 (`PR-*`)
- Quality and test constraints: Sections 8 and 11 (`NFR-*`, `AC-*`)

This traceability map SHALL be used to plan and sequence Studio implementation tasks and TODO entries.
