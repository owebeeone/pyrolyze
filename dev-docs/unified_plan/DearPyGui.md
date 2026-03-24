# Dear PyGui — unified adapter implementation plan

## Analysis status

Done or in progress:

- **Generated `M_*` factories:** `widget_catalog_extract.json` →
  `dearpygui.add_factories_generated_m_classes` (157 names).
- **Hand-written `items.py` factories:** same file →
  `dearpygui.add_factories_items_py` (16 names: `add_button`, `add_input_text`,
  `add_window`, menus, tables, plots, nodes, themes, …).
- **Union:** `dearpygui.add_factories_union` (166 in-tree `add_*` names).
- **Mount / spec sampling:** `dev-docs/widget-reconcile/surface_analysis.json`
  and `AdditionalAnalysis.md`.
- Initial role triage: `RoleMatrix.md` (DPG column).

Still to analyse (blocking several roles):

- **Checked-in API dump:** `scratch/dpg/dearpygui_api_dump.py` — run
  `scripts/extract_widget_catalogs.py` with dump present to populate
  `canonical_mountables` and `classification_counts`; reconcile dump
  classifications with the **generated vs items.py** split.
- **Viewport vs window:** DPG root is viewport-centric (`add_viewport_menu_bar`,
  etc.); map to canonical mount keys and to `ReactiveRootWindowProxy.md`
  semantics (child windows vs global viewport).
- **Immediate-mode vs retained:** which unified props map to per-frame DPG calls
  vs retained item state; document in adapter per role.

## Deliverables (this backend)

- Concrete **adapter class** (unified base subclass); **same method names** as Qt
  and Tk; bridges generated `M_*` specs and `items.py` helpers.
- Reference layout or test for canonical mount keys on a DPG viewport shell.
- Regenerated extract + `RoleMatrix.md` updates after dump-driven reconciliation.

## Implementation checklist

- [ ] Obtain or regenerate API dump; refresh `widget_catalog_extract.json`.
- [ ] Re-triage `text_line`, `pressable`, and layout roles with dump evidence.
- [ ] Confirm package location and public import path.
- [ ] Wave 1: implement unified symbols where DPG role is portable or
      best-effort with documented behavior.
- [ ] App context: map tokens to DPG theme/font hooks (best-effort).
- [ ] Tests: skip policy for environments without DPG display if applicable.
- [ ] Cutover: no `backends/common/` for DPG examples (Phase 5).

## Open questions

- When to **regenerate** `generated_library.py` so core widgets appear as `M_*`
  classes vs continuing to route through **`items.py`** helpers (both are valid
  if documented).
- Plot/series surface — remain **toolkit-only** for unified v1 unless scope
  expands.
