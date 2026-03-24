# Additional analysis (mounts, specs, DPG split, advert rules)

This pass implements the “still to analyse” items from
`dev-docs/unified_plan/*.md`: mount selector inventory, wave-1 `WIDGET_SPECS`
sampling, `advertise_mount` container semantics, and window-shell sketches.

**Machine-readable output:** `surface_analysis.json` (regenerate with
`uv run python scripts/analyze_unified_surfaces.py`).


## 1. Mount selector surfaces

| Backend | Mechanism | Names (families) |
| --- | --- | --- |
| **PySide6** | `PySide6UiLibrary.mounts.*` → `MountSelector.named(...)(**kwargs)` | `action`, `central_widget`, `corner_widget`, `layout`, `menu`, `menu_bar`, `menu_widget`, `status_bar`, `title_bar_widget`, `viewport`, `widget` |
| **Tkinter** | `TkinterUiLibrary.mounts.*` | `grid`, `pack`, `pane`, `tab` |
| **Dear PyGui** | No `mounts` namespace on `DearPyGuiUiLibrary` | Placement = `DpgRuntimeHost.move_item` + per-kind `UiWidgetSpec.mount_points` on **generated** `M_*` classes where codegen attached mount metadata; **plus** hand-written `items.py` containers (`DpgWindowItem`, `DpgTableItem`, …). |

Canonical mount keys (Phase 2) should map **onto** these families—for Qt,
`widget(row=, column=)` aligns with grid-style examples; for Tk, `grid`/`pack`
selectors; for DPG, expect **per-container** mount point names from specs rather
than a single global selector table.


## 2. Dear PyGui: generated `M_*` vs `items.py`

Two overlapping sets of `add_*` factories:

- **`generated_library.py`:** 157 unique `FACTORY = "add_*"` strings on `M_*`
  classes (plots, handlers, inputs, etc.).
- **`items.py`:** 16 hand-written `FACTORY` strings on `Dpg*Item` classes.

**Only in `items.py` (not on generated `M_*` FACTORY lines):**

`add_button`, `add_input_text`, `add_window`, `add_menu`, `add_menu_bar`,
`add_table`, `add_table_column`, `add_table_row`, `add_plot`, `add_plot_axis`,
`add_node`, `add_node_editor`, `add_node_link`, `add_theme`,
`add_theme_component`, `add_font_registry`.

**Implication:** Unified DPG adapters for **push button**, **text line**, **window
shell**, and several **container** shapes must target **`items.py` types** (or
the underlying DearPyGui APIs they wrap), not assume every operation appears in
the `M_*` codegen file. The earlier `widget_catalog_extract.json` slice is
**incomplete for DPG** until it merges both sources (see README).


## 3. `ChildPolicy` in codegen

For both Qt and Tk, **all 105** `UiWidgetSpec` rows use `ChildPolicy.NONE`.
Ordered / single-child semantics are expressed through **mount points** and the
mountable engine, not through `child_policy` today. Unified docs should not rely
on `child_policy` until or unless codegen starts populating it.


## 4. Wave-1 `WIDGET_SPECS` samples

`surface_analysis.json` → `wave1_widget_spec_samples` documents, per kind:

- `prop_count`, `PropMode` histogram, `AccessorKind` usage counts on props,
- `mount_point_names`, default attach mount point fields.

Use it to compare **update vs remount** pressure (`CREATE_ONLY_REMOUNT`, etc.)
across backends before freezing unified prop names.


## 5. `advertise_mount` container ownership

From `runtime/context.py`:

- `advertise_mount()` requires a parent that is a **native container owner**:
  `parent.expects_native_root or parent.committed_native_root`.
- Those flags are set while **`_NativeContainerCallHandle`** /
  **`_PyrolyzeContainerCallHandle`** run—i.e. inside native **container**
  component helpers that must emit **exactly one** root `UIElement`.

So: **mount advertisement is structurally tied to `call_native(UIElement)`
container components**, not to arbitrary leaves. Unified shell components should
be authored as native containers that advertise canonical keys.


## 6. Window shell vs proxy (per backend)

Sketched in `surface_analysis.json` → `window_shell_sketch`:

- **Qt:** `QMainWindow`, `QWidget`, `QDialog` as primary top-level patterns.
- **Tk:** `Tk` + `Toplevel`.
- **DPG:** Global **viewport** vs `add_window` / `add_child_window`; `DpgWindowItem`
  uses `add_window` and custom `attach_menu_bar`.

Align with `dev-docs/ReactiveRootWindowProxy.md` when defining proxy attach/detach.


## 7. API dump

`scratch/dpg/dearpygui_api_dump.py` is still **absent** in this checkout.
`widget_catalog_extract.json` → `dearpygui.api_dump.status` remains `missing`.
Once the dump exists, re-run `scripts/extract_widget_catalogs.py` to reconcile
**classification_counts** and **canonical_mountables** with the hand-written
`items.py` set.


## 8. Suggested next actions

1. Extend `extract_widget_catalogs.py` (or post-process) to union **DPG
   `items.py` factories** into the published catalog JSON.
2. Draft **`MountKeys.md`** under `dev-docs/unified_plan/`: map canonical public
   keys → Qt `mounts.*` / Tk `mounts.*` / DPG mount point names per host kind.
3. Update **wave-1** rows in `RoleMatrix.md` using §2 (button/text/window now have
   explicit DPG targets in `items.py`).
