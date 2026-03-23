# Generated UI reference (multi-backend)

This folder holds **machine-generated** Markdown per toolkit.

| Backend   | Generator | Output |
|-----------|-----------|--------|
| **PySide6** | `pyrolyze_tools/generate_semantic_library.py … --gen-docs` | `pyside6/entities.md`, `pyside6/properties.md` |
| **Tkinter** | `pyrolyze_tools/generate_semantic_library.py tkinter` or `tkinter.ttk` … `--gen-docs` | `tkinter/entities.md`, `tkinter/properties.md` |
| **Dear PyGui** | `pyrolyze_tools/generate_dearpygui_library.py --gen-docs` | `dearpygui/entities.md`, `dearpygui/properties.md` |

Regenerate PySide6 docs from the repo root, for example:

```bash
# From workspace root; `--output-dir` is where the tool writes `<package>.py` (default `pyside6.py`).
uv run python py-rolyze/pyrolyze_tools/generate_semantic_library.py PySide6.QtWidgets \
  --output-dir py-rolyze/src/pyrolyze/backends/pyside6 \
  --gen-docs
```

Tkinter (classic + ttk share one output folder unless you pass `--docs-out` per run):

```bash
uv run python py-rolyze/pyrolyze_tools/generate_semantic_library.py tkinter \
  --output-dir py-rolyze/src/pyrolyze/backends/tkinter \
  --gen-docs
```

Dear PyGui (from checked-in `DearPyGuiUiLibrary.WIDGET_SPECS`):

```bash
uv run python py-rolyze/pyrolyze_tools/generate_dearpygui_library.py --gen-docs
```

See [Generated UI Library Reference Doc Spec](../Generated_UI_Library_Reference_Doc_Spec.md).
