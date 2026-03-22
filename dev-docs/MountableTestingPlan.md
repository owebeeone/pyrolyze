# Mountable Testing Plan

## Purpose

This document defines the verification plan for the mountable-based generic
reconciler work.

It replaces the older widget-spec-centered testing direction and should be the
reference for:

- extraction and learnings validation
- generated surface validation
- mount-point validation
- backend conformance validation
- Studio-shaped integration validation


## Principles

- prefer TDD for behavior changes
- keep extraction tests deterministic and narrow
- isolate live-toolkit crash risk in subprocesses
- verify both generated API shape and runtime behavior
- test learnings overlays as first-class authoritative inputs


## Test Layers

## 1. Generated UI Interface Surface

Goal:

- verify generated `UiLibrary` classes expose the intended author-facing API

Coverage:

- `@ui_interface` manifest contents
- generated callable names
- explicit public parameter lists
- packed-`kwds` behavior
- `UI_INTERFACE.build_element(...)`
- future produced-type metadata on component metadata


## 2. Raw Extraction Tests

Goal:

- verify toolkit discovery captures raw constructor, property, method, and
  mount-point candidates correctly

Coverage:

- PySide6 `.pyi` parsing
- `QMetaObject` property extraction
- tkinter constructor/config/option extraction
- raw object-attachment API discovery
- grouped setter/method discovery


## 3. Learnings Overlay Tests

Goal:

- verify `learnings.py` is authoritative and stable across reruns

Coverage:

- inclusion/exclusion overrides
- public API shaping overrides
- keyed vs non-keyed mount param overrides
- mount-point naming overrides
- method `source_props` overrides
- `constructor_equivalent` overrides
- fill-policy overrides
- produced-type overrides where needed

These tests should be direct and narrow. The generator should not be trusted
implicitly here.


## 4. Generated Mountable Spec Tests

Goal:

- verify generated mountable metadata reflects raw extraction plus learnings

Coverage:

- `MountableSpec`
- `UiPropSpec`
- `UiMethodSpec`
- `MountPointSpec`
- `MountParamSpec`
- `accepted_produced_type`
- `min_children` / `max_children`

These tests should assert on generated data structures directly.


## 5. Adapter Tests

Goal:

- verify portable `UiLibrary` surfaces map correctly into backend-native
  mountable surfaces

Coverage:

- prop-name remapping
- event mapping
- unsupported prop failures
- produced-type compatibility through adapters


## 6. Mountable Engine Unit Tests

Goal:

- verify backend engine behavior independent of the full reconciler

Coverage:

- create -> mounted node + identity
- update -> prop/setter/method application
- remount -> preserve placement and replace cleanly
- built-in `standard` mount point application
- explicit mount-point application
- duplicate mount-instance rejection
- rollback on mount-point application failure
- snapshot/restore rollback when the adapter exposes snapshot hooks
- re-apply-old-state rollback when snapshot hooks are absent
- mount adapter contract failure when no rollback path exists


## 7. Mount Point Conformance Tests

Goal:

- verify mount points actually behave correctly against the live toolkit

Coverage:

- single attachment sites
- ordered attachment sites
- keyed attachment sites
- non-keyed mount-time values
- `max_children=1` enforcement
- ordered reapply/reorder behavior
- backend-native `sync(...)` fast path where implemented
- fallback `apply(...)` behavior where direct `sync(...)` is absent
- rollback leaves the live parent identical to the last committed mount state


## 8. Mountable Matrix Tests

Goal:

- verify real live-toolkit behavior across the discovered/generated mountable
  surface

Coverage:

- constructor inputs
- writable props
- grouped methods
- mount points
- readable getters where available

Each case should report:

- mountable kind
- operation type
- operation name
- argument payload
- pass / fail / crash


## 9. Crash-Isolated Toolkit Tests

Goal:

- keep Qt/Tk crashes from taking down the full test run

Coverage:

- suspicious or crash-prone mountables
- suspicious mount points
- constructor/property combinations known to be fragile

Implementation rule:

- execute these cases in subprocesses
- collect structured result records
- fail with precise case identifiers


## 10. Reconciler Integration Tests

Goal:

- verify the full path from `UiLibrary` source call to live backend result

Coverage:

- direct generated toolkit library path
- portable `CoreUiLibrary` + adapter path
- mount-point application through reconciliation
- remount rules through reconciliation
- event-driven rerender correctness
- rollback on failure


## 11. Studio-Shaped Integration Tests

Goal:

- verify the mountable architecture can actually support the intended Studio
  shell class of applications

Coverage:

- main window shell
- menu bar / menus / actions
- toolbar actions
- splitters
- tabs and tab reorder
- model-backed tree view
- secondary inspector window root
- custom/native overlay bridge

These are not meant to be pixel-perfect UI tests. They are lifecycle and
reactivity tests for Studio-shaped trees.


## Immediate Priority

The first tests to build after the terminology/model rename should be:

1. learnings overlay tests for mount-point classification
2. generated mountable-spec tests
3. mountable-engine tests for `standard` mount and one explicit mount point
4. crash-isolated matrix harness
5. one Studio-shaped integration scenario with a secondary inspector root


## File Layout

Suggested layout:

```text
tests/backends/
    pyside6/
        test_generated_library_surface.py
        test_mountable_spec_generation.py
        test_mount_point_generation.py
        test_adapter_mapping.py
        test_mountable_engine.py
        test_mount_point_conformance.py
        test_mountable_matrix.py
        test_mountable_matrix_subprocess.py
        test_studio_shell_integration.py
    tkinter/
        test_generated_library_surface.py
        test_mountable_spec_generation.py
        test_mount_point_generation.py
        test_adapter_mapping.py
        test_mountable_engine.py
        test_mount_point_conformance.py
        test_mountable_matrix.py
```


## Backlog Hooks

Backlog items that still refer to the removed `AdvancedTestingPlan.md` should
now point at this document instead.
