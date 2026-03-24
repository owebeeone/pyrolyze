#!/usr/bin/env python3
"""Emit mechanical widget catalog extracts (Widget Reconcile Plan, Phase 0).

Run from the pyrolyze repository root:

    uv run python scripts/extract_widget_catalogs.py

Writes ``dev-docs/widget-reconcile/widget_catalog_extract.json`` (schema v2:
Dear PyGui merges ``generated_library.py`` and ``items.py`` factory sets).
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
OUT_DIR = REPO_ROOT / "dev-docs" / "widget-reconcile"
OUT_FILE = OUT_DIR / "widget_catalog_extract.json"
DPG_GENERATED = REPO_ROOT / "src" / "pyrolyze" / "backends" / "dearpygui" / "generated_library.py"
DPG_ITEMS = REPO_ROOT / "src" / "pyrolyze" / "backends" / "dearpygui" / "items.py"


def _dearpygui_add_factories_from_generated() -> list[str]:
    text = DPG_GENERATED.read_text(encoding="utf-8")
    return sorted(set(re.findall(r'FACTORY = "(add_[a-z0-9_]+)"', text)))


def _dearpygui_add_factories_from_items_py() -> list[str]:
    text = DPG_ITEMS.read_text(encoding="utf-8")
    return sorted(set(re.findall(r'FACTORY = "(add_[a-z0-9_]+)"', text)))


def _dearpygui_dump_payload() -> dict:
    sys.path.insert(0, str(SRC))
    from pyrolyze.backends.dearpygui.discovery import (
        dearpygui_default_dump_path,
        iter_canonical_mountables,
        load_dearpygui_dump,
    )

    path = dearpygui_default_dump_path()
    try:
        loaded = load_dearpygui_dump()
    except FileNotFoundError:
        return {
            "status": "missing",
            "expected_path_relative_to_repo": "scratch/dpg/dearpygui_api_dump.py",
            "note": "Install checked-in dump to populate mountable_factory slice and classification_counts.",
        }

    mountables = iter_canonical_mountables(loaded)
    return {
        "status": "ok",
        "dump_path_relative_to_repo": str(path.relative_to(REPO_ROOT)),
        "dearpygui_version": loaded.dearpygui_version,
        "function_count": loaded.function_count,
        "classification_counts": dict(loaded.classification_counts),
        "canonical_mountable_count": len(mountables),
        "canonical_mountables": [
            {
                "factory_name": m.factory_name,
                "kind_name": m.kind_name,
                "classification": m.record.classification,
                "alias_count": len(m.context_alias_names),
            }
            for m in mountables
        ],
    }


def main() -> None:
    sys.path.insert(0, str(SRC))
    from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary
    from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary

    qt_entries = [
        {"public_name": pub, "kind": ent.kind}
        for pub, ent in sorted(
            PySide6UiLibrary.UI_INTERFACE.entries.items(),
            key=lambda kv: (kv[1].kind, kv[0]),
        )
    ]
    tk_entries = [
        {"public_name": pub, "kind": ent.kind}
        for pub, ent in sorted(
            TkinterUiLibrary.UI_INTERFACE.entries.items(),
            key=lambda kv: (kv[1].kind, kv[0]),
        )
    ]

    dpg_add = _dearpygui_add_factories_from_generated()
    dpg_items_add = _dearpygui_add_factories_from_items_py()
    dpg_union = sorted(set(dpg_add) | set(dpg_items_add))
    dump = _dearpygui_dump_payload()

    payload = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_note": "Paths in this file are relative to the pyrolyze package repository root.",
        "pyside6": {
            "source_module": "src/pyrolyze/backends/pyside6/generated_library.py",
            "ui_interface_entry_count": len(qt_entries),
            "entries": qt_entries,
        },
        "tkinter": {
            "source_module": "src/pyrolyze/backends/tkinter/generated_library.py",
            "ui_interface_entry_count": len(tk_entries),
            "entries": tk_entries,
        },
        "dearpygui": {
            "generated_library_module": "src/pyrolyze/backends/dearpygui/generated_library.py",
            "items_py_module": "src/pyrolyze/backends/dearpygui/items.py",
            "unique_add_factory_count_generated_m_classes": len(dpg_add),
            "add_factories_generated_m_classes": dpg_add,
            "unique_add_factory_count_items_py": len(dpg_items_add),
            "add_factories_items_py": dpg_items_add,
            "unique_add_factory_count_union": len(dpg_union),
            "add_factories_union": dpg_union,
            "only_in_generated_m_classes": sorted(set(dpg_add) - set(dpg_items_add)),
            "only_in_items_py": sorted(set(dpg_items_add) - set(dpg_add)),
            "api_dump": dump,
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    main()
