# Canonical mount keys (unified shell)

## Purpose

Stable **string keys** for `advertise_mount` / `mount` so cross-backend examples
share the same vocabulary. Values are defined in code as
`pyrolyze.unified.mount_keys`.

For a **tree diagram**, expanded per-backend **`target=` selector** guidance, and
checklist for reference tests, see **`dev-docs/ReferenceShellLayout.md`**.

## Keys

| Key constant | Value | Meaning |
| --- | --- | --- |
| `SHELL_BODY` | `shell.body` | Primary document / content region. |
| `SHELL_CHROME` | `shell.chrome` | Window chrome area (toolbars, title-adjacent strips) when distinct from menu bar. |
| `SHELL_MENU_BAR` | `shell.menu_bar` | Top menu strip (Qt `QMenuBar`, Tk `Menu`, DPG viewport or window menu bar). |
| `SHELL_STATUS` | `shell.status` | Status line / footer strip. |
| `DIALOG_CONTENT` | `dialog.content` | Main body inside a dialog surface. |
| `DIALOG_ACTIONS` | `dialog.actions` | Action row (OK / Cancel) in a dialog. |

## Per-backend selector recipes (sketch)

Full detail: **`dev-docs/ReferenceShellLayout.md`**. Summary below.

Authors still target **native** selectors from the generated `*UiLibrary.mounts`
where they exist (Qt). Tk’s generated `mounts` are **geometry** slots; DPG
often has **no** `mounts` class — use **`MountSelector.named(...)`** and bind in
bootstrap (see reference doc). Also see `UnifiedMountBasedNativeApi.md` for
mount-first composition.

| Key | Qt (typical) | Tk (typical) | DPG (typical) |
| --- | --- | --- | --- |
| `shell.body` | `PySide6UiLibrary.mounts.central_widget` or layout under main window | `Frame` / `ttk.Frame` + `grid`/`pack` host | `add_child` / window client area patterns |
| `shell.menu_bar` | `mounts.menu_bar` | menu attached to `Tk` / `Toplevel` | `add_viewport_menu_bar` or per-window menu |
| `shell.status` | `QStatusBar` slot if used | `ttk.Label` in bottom frame | text + draw or widget row |
| `dialog.content` | `QDialog` layout body | `Toplevel` inner frame | `add_window` children |
| `dialog.actions` | button row `QDialogButtonBox` | button frame | same as row of buttons |

Exact adverts belong in **reference layout** tests (`tests/unified/`).

## Versioning

Bump this document when adding or renaming keys; keep `mount_keys.py` in sync.
