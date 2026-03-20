# Studio PyRolyze Implementation Directory Structure

## Purpose

This document defines the recommended `Studio/` directory layout for implementing
Studio with `@pyrolyse` + `PySide6`, with clear ownership boundaries and test
separation.

## Proposed Structure

```text
Studio/
  README.md
  Studio_System_Requirements.md
  Studio_Directory_Structure.md

  architecture/
    Studio_Architecture.md
    decisions/
      ADR-001-host-shell-boundary.md
      ADR-002-node-contracts.md
      ADR-003-inspector-ownership.md

  host/
    __init__.py
    app_host.py
    main_window.py
    window_chrome.py
    menu_bridge.py
    status_bar_bridge.py

  app/
    __init__.py
    models.py
    state.py
    actions.py
    reducers.py
    selectors.py
    commands.py

  services/
    __init__.py
    settings_service.py
    filesystem_service.py
    hierarchy_service.py
    screenshot_service.py
    async_service.py

  ui/
    __init__.py
    studio_root.py
    node_contracts.py
    theme.py
    components/
      __init__.py
      workspace.py
      explorer_panel.py
      editor_tabs.py
      bottom_panel.py
      inspector_panel.py
      status_widgets.py

  bridges/
    __init__.py
    host_widget_bridge.py
    qtree_bridge.py
    tabs_bridge.py
    splitter_bridge.py

  runtime_ext/
    __init__.py
    pyside6_bindings.py
    ui_descriptors.py
    reconcile_helpers.py
    event_threading.py

  tests/
    unit/
      test_state_reducers.py
      test_selectors.py
      test_services_settings.py
      test_services_filesystem.py
    integration/
      test_host_mount_points.py
      test_explorer_flow.py
      test_tabs_flow.py
      test_inspector_flow.py
      test_persistence_flow.py
    perf/
      test_reconcile_large_tree.py
      test_tabs_reorder_scale.py
      test_inspector_hover_scale.py

  scripts/
    run_studio.py
    run_studio_tests.py
```

## Ownership Guidelines

- `host/`: Native PySide6 window shell and platform-specific behavior only.
- `app/`: Pure application state and action logic, no direct widget mutation.
- `services/`: IO and external side effects.
- `ui/`: PyRolyze declarative components and theme composition.
- `bridges/`: Integration points between host widgets and declarative state.
- `runtime_ext/`: PyRolyze node/binding extensions required by Studio.
- `tests/`: Split by unit/integration/performance for clear execution scope.

## Implementation Notes

- Keep `studio_root.py` as the declarative entrypoint for app content.
- Keep all platform-specific code (`ctypes`, Win32 calls) under `host/`.
- Add new semantic node contracts in `runtime_ext/ui_descriptors.py`.
- Add bridge lifecycle tests before enabling bridge-backed components in UI.
