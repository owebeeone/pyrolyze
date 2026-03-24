#!/usr/bin/env python3
"""Build ``unified_native_coverage.json`` (Phase 0) from ``widget_catalog_extract.json``.

Run from the pyrolyze repository root::

    uv run python scripts/build_unified_coverage.py

Reads ``dev-docs/widget-reconcile/widget_catalog_extract.json`` and writes
``dev-docs/widget-reconcile/unified_native_coverage.json``.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXTRACT = REPO_ROOT / "dev-docs" / "widget-reconcile" / "widget_catalog_extract.json"
OUT = REPO_ROOT / "dev-docs" / "widget-reconcile" / "unified_native_coverage.json"

# Qt / Tk kinds -> (unified_method, triage) or None if deferred to rule-based path.
_QT_KIND_MAP: dict[str, tuple[str, str]] = {
    "QPushButton": ("push_button", "best-effort"),
    "QCheckBox": ("toggle", "portable"),
    "QLineEdit": ("text_field", "best-effort"),
    "QLabel": ("static_text", "best-effort"),
    "QPlainTextEdit": ("text_area", "best-effort"),
    "QSpinBox": ("int_field", "portable"),
    "QDoubleSpinBox": ("float_field", "portable"),
    "QComboBox": ("combo_box", "portable"),
    "QSlider": ("slider", "portable"),
    "QProgressBar": ("progress", "best-effort"),
    "QTabWidget": ("tab_stack", "best-effort"),
    "QRadioButton": ("radio_button", "best-effort"),
    "QMenuBar": ("menu_bar", "best-effort"),
    "QToolBar": ("tool_bar", "best-effort"),
    "QScrollArea": ("scroll_panel", "best-effort"),
    "QWidget": ("spacer", "best-effort"),
}

_TK_KIND_MAP: dict[str, tuple[str, str]] = {
    "ttk_Button": ("push_button", "best-effort"),
    "ttk_Checkbutton": ("toggle", "portable"),
    "ttk_Entry": ("text_field", "best-effort"),
    "Text": ("text_area", "best-effort"),
    "ttk_Label": ("static_text", "best-effort"),
    "tkinter_Spinbox": ("int_field", "portable"),
    "ttk_Spinbox": ("int_field", "portable"),
    "Combobox": ("combo_box", "portable"),
    "ttk_Scale": ("slider", "portable"),
    "Progressbar": ("progress", "best-effort"),
    "Notebook": ("tab_stack", "best-effort"),
    "ttk_Radiobutton": ("radio_button", "best-effort"),
    "tkinter_Radiobutton": ("radio_button", "best-effort"),
    "Menu": ("menu_bar", "best-effort"),
    "Separator": ("separator", "best-effort"),
    "Canvas": ("scroll_panel", "best-effort"),
    "ttk_Frame": ("tool_bar", "best-effort"),
}


def _classify_qt(kind: str) -> tuple[str, str, str | None, str | None]:
    if "QDesigner" in kind:
        return "excluded", "toolkit-only", None, "Qt Designer plugin or designer-only type"
    if kind.startswith("QAbstract") and kind != "QAbstractButton":
        return "grouped", "toolkit-only", None, "Abstract base; use concrete subtype for unified mapping"
    hit = _QT_KIND_MAP.get(kind)
    if hit:
        method, triage = hit
        return "unified", triage, method, None
    return "deferred", "toolkit-only", None, "No Wave A unified method assigned yet"


def _classify_tk(kind: str) -> tuple[str, str, str | None, str | None]:
    hit = _TK_KIND_MAP.get(kind)
    if hit:
        method, triage = hit
        return "unified", triage, method, None
    if kind in ("Balloon", "CObjView") or kind.startswith("tix_"):
        return "excluded", "toolkit-only", None, "Tix / legacy auxiliary surface"
    return "deferred", "toolkit-only", None, "No Wave A unified method assigned yet"


_ADD_FACTORY_MAP: dict[str, tuple[str, str]] = {
    "add_button": ("push_button", "best-effort"),
    "add_checkbox": ("toggle", "portable"),
    "add_input_text": ("text_field", "best-effort"),
    "add_input_int": ("int_field", "portable"),
    "add_input_float": ("float_field", "portable"),
    "add_input_double": ("float_field", "portable"),
    "add_combo": ("combo_box", "portable"),
    "add_slider_int": ("slider", "portable"),
    "add_slider_float": ("slider", "portable"),
    "add_progress_bar": ("progress", "best-effort"),
    "add_tab_bar": ("tab_stack", "best-effort"),
    "add_radio_button": ("radio_button", "best-effort"),
    "add_text": ("static_text", "best-effort"),
    "add_menu_bar": ("menu_bar", "best-effort"),
    "add_group": ("tool_bar", "best-effort"),
    "add_separator": ("separator", "best-effort"),
    "add_child_window": ("scroll_panel", "best-effort"),
    "add_spacer": ("spacer", "best-effort"),
}


def _classify_dpg_factory(name: str) -> tuple[str, str, str | None, str | None]:
    # name is e.g. "add_input_int"
    hit = _ADD_FACTORY_MAP.get(name)
    if hit:
        method, triage = hit
        return "unified", triage, method, None
    if re.match(r"^add_.*_(series|handler)$", name) or "plot" in name:
        return "deferred", "toolkit-only", None, "Plot/handler family; defer unified v1"
    if name.startswith("add_draw_"):
        return "deferred", "toolkit-only", None, "Draw-list primitive; defer"
    return "deferred", "best-effort", None, "Not yet mapped to a unified method"


def main() -> None:
    if not EXTRACT.is_file():
        print(f"Missing {EXTRACT.relative_to(REPO_ROOT)}; run scripts/extract_widget_catalogs.py first", file=sys.stderr)
        sys.exit(1)

    extract = json.loads(EXTRACT.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []

    for ent in extract["pyside6"]["entries"]:
        kind = str(ent["kind"])
        bucket, triage, method, reason = _classify_qt(kind)
        rows.append(
            {
                "backend": "pyside6",
                "native_id": kind,
                "public_name": ent["public_name"],
                "bucket": bucket,
                "triage": triage,
                "unified_method": method,
                "note": reason,
            }
        )

    for ent in extract["tkinter"]["entries"]:
        kind = str(ent["kind"])
        bucket, triage, method, reason = _classify_tk(kind)
        rows.append(
            {
                "backend": "tkinter",
                "native_id": kind,
                "public_name": ent["public_name"],
                "bucket": bucket,
                "triage": triage,
                "unified_method": method,
                "note": reason,
            }
        )

    dpg_union = extract["dearpygui"]["add_factories_union"]
    for factory in dpg_union:
        bucket, triage, method, reason = _classify_dpg_factory(factory)
        rows.append(
            {
                "backend": "dearpygui",
                "native_id": factory,
                "public_name": factory,
                "bucket": bucket,
                "triage": triage,
                "unified_method": method,
                "note": reason,
            }
        )

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_extract": str(EXTRACT.relative_to(REPO_ROOT)),
        "row_count": len(rows),
        "entries": rows,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO_ROOT)} ({len(rows)} rows)", file=sys.stderr)


if __name__ == "__main__":
    main()
