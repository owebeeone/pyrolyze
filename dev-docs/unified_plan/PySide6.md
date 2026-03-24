# PySide6 — unified adapter implementation plan

## Analysis status

Done or in progress:

- `UiInterface` / `kind` inventory: `dev-docs/widget-reconcile/widget_catalog_extract.json`
  (`pyside6.entries`, 105 kinds).
- Initial role triage: `dev-docs/widget-reconcile/RoleMatrix.md` (Qt column).

Still to analyse (before locking adapter signatures):

- **Mount surface:** enumerate `PySide6UiLibrary.mounts` (or equivalent) and map to
  canonical mount keys; document grid / stack patterns used by examples.
- **Per-kind accessor profile:** sample `WIDGET_SPECS` for wave-1 kinds
  (`QPushButton`, `QLineEdit`, …) — `PropMode`, `AccessorKind`, remount rules.
- **Chrome vs content:** which kinds are valid **native container owners** for
  `advertise_mount` (align with runtime tests and grid example).

## Deliverables (this backend)

- Concrete **adapter class** (subclass of unified base) exporting the **same
  method names** as Tk and DPG adapters; holds / delegates to
  `PySide6UiLibrary` where needed.
- Reference layout or test proving canonical mount keys for a Qt window shell.
- Notes in `RoleMatrix.md` when Qt is **toolkit-only** or **best-effort** for a
  role.

## Implementation checklist

- [ ] Confirm package location and public import path.
- [ ] Wave 1: implement unified symbols agreed from `RoleMatrix.md` (subset).
- [ ] Mount key mapping documented (table in this file or `MountKeys.md`).
- [ ] App context: read policy keys in adapter paths for wave-1 widgets.
- [ ] Tests: generic backend or focused Qt tests per unified symbol.
- [ ] Remove any remaining dependency on `backends/common/` for Qt examples
      (Phase 5 cutover).

## Open questions

- Designer plugin kinds (`QDesigner*`) — exclude from unified API unless a role
  explicitly needs them.
- `QMainWindow` vs `QDialog` vs `QWidget` root — interaction with window proxy
  registry.
