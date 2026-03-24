# Role triage matrix (Phase 1 — initial pass)

## Sources

- Counts and raw lists: `widget_catalog_extract.json` (regenerate via
  `scripts/extract_widget_catalogs.py`).
- This matrix **clusters** native kinds into **roles**. It is not exhaustive for
  every `QDesigner*` or Tix dialog; those default to **toolkit-only** until a
  role needs them.

## Mechanical summary (from extract)

| Backend | What was counted | Count |
| --- | --- | ---: |
| PySide6 | `UiInterface.entries` (`kind` values) | 105 |
| Tkinter | `UiInterface.entries` (`kind` values) | 105 |
| Dear PyGui | `add_*` on `M_*` classes in `generated_library.py` | 157 |
| Dear PyGui | `add_*` on `Dpg*Item` in `items.py` | 16 |
| Dear PyGui | Union (in-tree names) | 173 (`dearpygui.add_factories_union`; disjoint M_* vs items.py sets) |
| Dear PyGui | API dump (`canonical_mountables`) | *absent in this checkout* |

### Findings from Dear PyGui (generated + runtime items)

The **`M_*` generated file** includes **numeric** inputs (`add_input_int`, …)
and many plot/handler factories, but **does not** declare `FACTORY = "add_button"`
or `"add_input_text"` on `M_*` classes.

**Hand-written `backends/dearpygui/items.py`** *does* bind **`add_button`**,
**`add_input_text`**, **`add_window`**, menus, tables, plots, nodes, themes,
etc. (16 factories). Unified DPG adapters must treat **`items.py` as canonical**
for those operations alongside generated `M_*` specs.

Until `scratch/dpg/dearpygui_api_dump.py` is present, cross-check classifications
there against both sources.

PySide6’s 105 entries include **Qt Designer plugin interfaces** and other types
that are not typical app widgets; treat rare kinds as **toolkit-only** until
pulled into a role.

Tkinter’s 105 entries mix **classic tk**, **ttk**, and **tix**; unified roles
should prefer **ttk** where parity exists and leave tix-only widgets as
toolkit-only.


## Role glossary (initial)

| Role id | Meaning |
| --- | --- |
| `pressable` | Primary click target (command button, not radio/check). |
| `toggle` | Boolean bound control (check, switch). |
| `single_choice` | Exactly one of N (radio cluster). |
| `text_line` | Single-line editable text. |
| `text_block` | Multi-line editable or read-only text region. |
| `number_int` | Integer stepper / spin. |
| `number_float` | Floating-point input. |
| `choice_list` | Drop-down / list selection of discrete items. |
| `slider` | Bounded continuous or stepped range. |
| `progress` | Determinate or indeterminate progress display. |
| `label` | Static or formatted read-only text. |
| `image` | Bitmap/icon display. |
| `scroll_region` | Scrollable viewport hosting children. |
| `layout_box` | Non-leaf container (row/column/stack semantics). |
| `tabs` | Tab container with labeled pages. |
| `menu_bar` | Top-level menu strip (window chrome). |
| `window_shell` | Top-level or child window host (lifetime via proxy; see `ReactiveRootWindowProxy.md`). |
| `dialog_file` | File open/save surface. |
| `date_time` | Date or date-time picker. |
| `color_pick` | Color chooser. |
| `plot` | Plot, series, axes (heavy DPG/Qt; mostly toolkit-specific). |


## Triage table

**Triage:** `portable` = same unified name, acceptable parity; `best-effort` =
unified name with documented gaps; `toolkit-only` = no unified v1 API.

**Representatives** are examples, not exclusive mappings.

| Role id | Unified API name (proposal) | Triage | Dear PyGui (rep.) | PySide6 (rep.) | Tkinter (rep.) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `pressable` | `push_button` | best-effort | `add_button` via `DpgButtonItem` (`items.py`) | `QPushButton` | `ttk_Button` | Not on `M_*` FACTORY lines; use items layer or host `create_with_factory`. |
| `toggle` | `toggle` | portable | `add_checkbox` | `QCheckBox` | `ttk_Checkbutton` | DPG checkbox is immediate-mode; state model differs from Qt. |
| `single_choice` | `radio_group` | best-effort | `add_radio_button` | `QRadioButton` + layout | `tkinter_Radiobutton` / `ttk` | Grouping semantics differ; unified API may take `group_id`. |
| `text_line` | `text_field` | best-effort | `add_input_text` via `DpgInputTextItem` (`items.py`) | `QLineEdit` | `ttk_Entry` | Not on `M_*` FACTORY lines; merge `items.py` into catalog JSON. |
| `text_block` | `text_area` | best-effort | *TBD* | `QPlainTextEdit` / `QTextEdit` | `tkinter_Text` | Large behavior differences (rich text). |
| `number_int` | `int_field` | portable | `add_input_int` | `QSpinBox` | `tkinter_Spinbox` / ttk | |
| `number_float` | `float_field` | portable | `add_input_float` / `add_input_double` | `QDoubleSpinBox` | *partial ttk* | Tk float spin often classic `tkinter`. |
| `choice_list` | `combo_box` | portable | `add_combo` | `QComboBox` | `ttk_Combobox` | Present in generated `add_factories` list. |
| `slider` | `slider` | portable | `add_slider` | `QSlider` | `ttk_Scale` | |
| `progress` | `progress` | best-effort | `add_progress_bar` | `QProgressBar` | `ttk_Progressbar` | Indeterminate modes differ. |
| `label` | `label` | portable | `add_text` | `QLabel` | `ttk_Label` | DPG `add_text` is draw-list text; wiring vs widget label TBD. |
| `image` | `image` | best-effort | `add_image` | `QLabel` + pixmap / `QGraphicsView` | `PhotoImage` on `Label` | Very different capabilities. |
| `scroll_region` | `scroll_area` | best-effort | `add_child` + clipper patterns | `QScrollArea` | `Canvas` + scrollbars / `ScrolledText` | DPG uses composition; not 1:1. |
| `layout_box` | `box` / `row` / `column` | best-effort | `add_group`, `add_child_window` | `QBoxLayout`, `QGridLayout` | `ttk_Frame` + grid/pack | Unified layout API is high risk; may stay mount-driven only. |
| `tabs` | `tab_stack` | best-effort | `add_tab_bar` / tab items | `QTabWidget` | `ttk_Notebook` | |
| `menu_bar` | `menu_bar` | best-effort | `add_viewport_menu_bar` + `add_menu_bar` (`DpgMenuBarItem`) + `add_menu_item` | `QMenuBar` | `Menu` on `Tk` | DPG: viewport vs per-`add_window` menu bar. |
| `window_shell` | *proxy API* | best-effort | `add_window` (`DpgWindowItem`) + viewport / `add_child_window` | `QMainWindow` / `QDialog` | `Tk` / `Toplevel` | See `ReactiveRootWindowProxy.md`. |
| `dialog_file` | `file_dialog` | toolkit-only | *native dialog patterns differ* | `QFileDialog` | `filedialog` | Often modal OS dialog; unified async shape TBD. |
| `date_time` | `date_edit` | best-effort | *TBD* | `QDateEdit` / `QDateTimeEdit` | limited | Tk has no first-class date widget in core. |
| `color_pick` | `color_chooser` | best-effort | `add_color_edit` | `QColorDialog` | `colorchooser` | |
| `plot` | *none v1* | toolkit-only | many `add_*_series`, plots | `QChartView`, etc. | *rare* | Unified plot API deferred. |

## Next steps

1. Check in `scratch/dpg/dearpygui_api_dump.py` (or regenerate) and re-run the
   extract script so `canonical_mountables` populates.
2. Merge **`items.py` factories** into `widget_catalog_extract.json` (see
   `AdditionalAnalysis.md` §2).
3. Mark **wave 1** roles: `toggle`, `number_int`, `number_float`, `slider`,
   `label`, `combo_box` (after DPG combo confirmation), `progress`, `tab_stack`
   (subset).
4. Extend this table with **extra rows** only when a role is needed for
   examples or GRIP; avoid one-row-per-Qt-class explosion.
