# Unified native methods (Waves A–D)

This lists **`UnifiedNativeLibrary`** methods implemented through **Phase 4
Waves A–D** (see `dev-docs/UnifiedComplete.md`). Each method exists on **Qt**,
**Tk**, and **DPG** adapters with the **same name**; emitted `UIElement.kind`
and `props` differ per backend.

## Wave A — controls

| Method | Role | Notes |
| --- | --- | --- |
| `push_button` | Primary action | |
| `toggle` | Checkbox-style boolean | |
| `text_field` | Single-line text | |
| `label` | Shared `Label` (not native kind) | |
| `int_field` | Integer spin | DPG ignores `step` today. |
| `float_field` | Float spin | |
| `combo_box` | List selection | `items`, `current_index`. |
| `slider` | Int range | Horizontal bias on Qt. |
| `progress` | Bar | Unified `value` is **0.0..1.0**; Qt/Tk use `maximum=100`. |
| `tab_stack` | Tab container | DPG uses `DpgTabBar` (subset). |
| `radio_button` | One-of group member | Grouping is toolkit-specific. |

## Waves B–D — text, chrome, layout

| Method | Role | Notes |
| --- | --- | --- |
| `text_area` | Multiline **plain** text | Not rich text; `read_only` maps per toolkit. |
| `static_text` | Native static line | Use `label()` when the shared `Label` kind is enough; DPG uses `DpgText` / `default_value`. |
| `menu_bar` | Menu bar shell | Attach menus per toolkit; Tk uses `Menu` with `tearoff=0`. |
| `tool_bar` | Toolbar / action row | Tk: `ttk.Frame` (title ignored); DPG: horizontal `DpgGroup`. |
| `separator` | H/V rule | DPG: `DpgSeparator` (orientation not parameterized). |
| `scroll_panel` | Scrollable viewport | Tk: `Canvas` best-effort; DPG: `DpgChildWindow` with scrollbar flags. |
| `spacer` | Fixed gap | Qt: `QWidget` min/max from nonzero width/height. |

**Version:** `pyrolyze.unified.UNIFIED_NATIVE_API_VERSION`

**Mount keys:** `pyrolyze.unified.mount_keys` and `dev-docs/MountKeys.md`

**Parameter mapping:** `dev-docs/widget-reconcile/wave_a_param_mapping.json` (Wave A),
`dev-docs/widget-reconcile/waves_bcd_param_mapping.json` (Waves B–D).

**Coverage index:** `dev-docs/widget-reconcile/unified_native_coverage.json` (regenerate via `scripts/build_unified_coverage.py` after `scripts/extract_widget_catalogs.py`).
