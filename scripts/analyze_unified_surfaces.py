#!/usr/bin/env python3
"""Emit mount-surface and wave-1 widget-spec analysis for the unified API plan.

Run from the pyrolyze repository root:

    uv run python scripts/analyze_unified_surfaces.py

Writes ``dev-docs/widget-reconcile/surface_analysis.json``.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
OUT = REPO_ROOT / "dev-docs" / "widget-reconcile" / "surface_analysis.json"
DPG_GEN = REPO_ROOT / "src" / "pyrolyze" / "backends" / "dearpygui" / "generated_library.py"
DPG_ITEMS = REPO_ROOT / "src" / "pyrolyze" / "backends" / "dearpygui" / "items.py"


def _factories_from_generated_dpg() -> set[str]:
    text = DPG_GEN.read_text(encoding="utf-8")
    return set(re.findall(r'FACTORY = "(add_[a-z0-9_]+)"', text))


def _factories_from_items_py() -> set[str]:
    text = DPG_ITEMS.read_text(encoding="utf-8")
    return set(re.findall(r'FACTORY = "(add_[a-z0-9_]+)"', text))


def _mount_selector_names(ns: Any) -> list[str]:
    import inspect

    m = ns.mounts
    return sorted(
        name for name, _ in inspect.getmembers(m) if not name.startswith("_")
    )


def _summarize_widget_spec(spec: Any) -> dict[str, Any]:
    from pyrolyze.backends.model import PropMode

    props = spec.props
    modes: Counter[PropMode] = Counter(p.mode for p in props.values())
    setter_kinds: Counter[str] = Counter()
    for p in props.values():
        if p.setter_kind is not None:
            setter_kinds[str(p.setter_kind)] += 1
    return {
        "kind": spec.kind,
        "mounted_type_name": spec.mounted_type_name,
        "child_policy": str(spec.child_policy),
        "prop_count": len(props),
        "prop_modes": {k.name: v for k, v in modes.items()},
        "setter_kind_counts": dict(setter_kinds),
        "mount_point_names": sorted(spec.mount_points.keys()),
        "default_child_mount_point_name": spec.default_child_mount_point_name,
        "default_attach_mount_point_names": list(spec.default_attach_mount_point_names),
    }


def main() -> None:
    sys.path.insert(0, str(SRC))
    from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt
    from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary as Tk

    dpg_gen = _factories_from_generated_dpg()
    dpg_items = _factories_from_items_py()
    only_generated = sorted(dpg_gen - dpg_items)
    only_items = sorted(dpg_items - dpg_gen)

    qt_wave = [
        "QPushButton",
        "QLineEdit",
        "QCheckBox",
        "QComboBox",
        "QSlider",
        "QMainWindow",
        "QGridLayout",
        "QScrollArea",
        "QTabWidget",
    ]
    tk_wave = [
        "ttk_Button",
        "ttk_Entry",
        "ttk_Checkbutton",
        "Combobox",
        "ttk_Scale",
        "ttk_Frame",
        "tkinter_Frame",
    ]

    qt_specs = Qt.WIDGET_SPECS
    tk_specs = Tk.WIDGET_SPECS

    qt_summaries = {}
    for k in qt_wave:
        if k in qt_specs:
            qt_summaries[k] = _summarize_widget_spec(qt_specs[k])
        else:
            qt_summaries[k] = {"error": "missing_kind"}

    tk_summaries = {}
    for k in tk_wave:
        if k in tk_specs:
            tk_summaries[k] = _summarize_widget_spec(tk_specs[k])
        else:
            tk_summaries[k] = {"error": "missing_kind"}

    child_policies_qt = Counter(str(s.child_policy) for s in qt_specs.values())
    child_policies_tk = Counter(str(s.child_policy) for s in tk_specs.values())

    advertise_note = {
        "source": "runtime/context.py advertise_mount()",
        "rule": "Parent slot must have expects_native_root or committed_native_root True.",
        "mechanism": "_NativeContainerCallHandle and _PyrolyzeContainerCallHandle set expects_native_root while native container helper runs; author must emit exactly one root UIElement.",
        "implication": "advertise_mount is valid inside call_native(UIElement) container components, not arbitrary leaf widgets.",
    }

    window_proxy = {
        "qt": {
            "primary_types": ["QMainWindow", "QWidget", "QDialog"],
            "notes": "QApplication single process; Toplevel-style behavior via QDialog or secondary QMainWindow.",
        },
        "tkinter": {
            "primary_types": ["tkinter.Tk", "tkinter.Toplevel"],
            "notes": "Root is Tk; extra windows are Toplevel; maps to ReactiveRootWindowProxy.md.",
        },
        "dearpygui": {
            "primary_types": ["viewport (global)", "add_window", "add_child_window"],
            "notes": "DpgWindowItem uses add_window; viewport menu bar is separate from per-window chrome; reconcile with proxy registry.",
            "handwritten_item_factories": sorted(dpg_items),
        },
    }

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mount_selectors": {
            "pyside6": _mount_selector_names(Qt),
            "tkinter": _mount_selector_names(Tk),
            "dearpygui": {
                "note": "No DearPyGuiUiLibrary.mounts namespace; placement uses host move_item and UiWidgetSpec.mount_points on generated M_* classes where present.",
                "mount_selector_count": 0,
            },
        },
        "dearpygui_factory_sets": {
            "generated_m_classes_count": len(dpg_gen),
            "items_py_count": len(dpg_items),
            "only_in_generated_m_classes": only_generated,
            "only_in_items_py": only_items,
            "interpretation": "Hand-written items.py binds core widgets (button, input_text, window) not represented as M_* FACTORY entries in generated_library.py; unified DPG adapters must consult both.",
        },
        "child_policy_distribution": {
            "pyside6": dict(child_policies_qt),
            "tkinter": dict(child_policies_tk),
            "note": "Current codegen sets ChildPolicy.NONE for all kinds; children attach via mount_points, not child_policy ordered/single.",
        },
        "wave1_widget_spec_samples": {
            "pyside6": qt_summaries,
            "tkinter": tk_summaries,
        },
        "advertise_mount_container_rule": advertise_note,
        "window_shell_sketch": window_proxy,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO_ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    main()
