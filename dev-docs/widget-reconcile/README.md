# Widget reconcile extracts (Phase 0)

Mechanical catalogs for `dev-docs/WidgetReconcilePlan.md` Phase 0–1.

## Regenerate

From the **pyrolyze** repository root:

```bash
uv run python scripts/extract_widget_catalogs.py
uv run python scripts/analyze_unified_surfaces.py
```

This overwrites `widget_catalog_extract.json` and `surface_analysis.json`.

## Artifacts

| File | Contents |
| --- | --- |
| `widget_catalog_extract.json` | PySide6 + Tkinter `UiInterface` entries (`public_name`, `kind`); Dear PyGui `add_*` sets from **`generated_library.py` and `items.py`** plus union; optional `api_dump` slice when `scratch/dpg/dearpygui_api_dump.py` exists. |
| `surface_analysis.json` | Mount selector names, DPG factory set diff, wave-1 `WIDGET_SPECS` samples, `advertise_mount` rule summary (run `scripts/analyze_unified_surfaces.py`). |
| `AdditionalAnalysis.md` | Narrative for the above; read alongside JSON. |
| `RoleMatrix.md` | Initial **semantic role** triage (portable / best-effort / toolkit-only) with representative native ids per backend. |

## Schema (`widget_catalog_extract.json`)

- `schema_version` — **2** adds Dear PyGui `items.py` factory lists and union fields.
- `pyside6.entries` — one object per generated UI wrapper; `kind` is the reconcile kind string.
- `tkinter.entries` — same shape.
- `dearpygui.add_factories_generated_m_classes` — `M_*` classes in `generated_library.py`.
- `dearpygui.add_factories_items_py` — hand-written `Dpg*Item` factories in `items.py`.
- `dearpygui.add_factories_union` — sorted union (use for “what `add_*` names exist in-tree”).
- `dearpygui.only_in_*` — set difference helpers for codegen vs runtime items.
- `dearpygui.api_dump` — either `status: "missing"` or `status: "ok"` with `canonical_mountables` from the checked-in dump module.

## Dear PyGui dump

If `scratch/dpg/dearpygui_api_dump.py` is absent, `api_dump.status` is `missing`. The `add_factories` list is still useful but **does not** equal the full mountable surface implied by a complete dump; codegen may omit items until regen.
