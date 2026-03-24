"""Phase 0–2 artifacts: mount key constants and coverage JSON schema."""

from __future__ import annotations

import json
from pathlib import Path

from pyrolyze.unified import UNIFIED_NATIVE_API_VERSION, mount_keys


def test_unified_native_api_version_is_non_empty() -> None:
    assert UNIFIED_NATIVE_API_VERSION
    assert UNIFIED_NATIVE_API_VERSION[0].isdigit()


def test_mount_key_constants_are_stable_strings() -> None:
    assert mount_keys.SHELL_BODY == "shell.body"
    assert mount_keys.SHELL_MENU_BAR == "shell.menu_bar"
    assert mount_keys.DIALOG_ACTIONS == "dialog.actions"


def test_unified_native_coverage_json_schema() -> None:
    root = Path(__file__).resolve().parents[2]
    path = root / "dev-docs" / "widget-reconcile" / "unified_native_coverage.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["row_count"] == len(data["entries"])
    for row in data["entries"]:
        assert row["backend"] in ("pyside6", "tkinter", "dearpygui")
        assert row["bucket"] in ("unified", "excluded", "deferred", "grouped")
        assert row["triage"] in ("portable", "best-effort", "toolkit-only")


def test_wave_a_param_mapping_json() -> None:
    root = Path(__file__).resolve().parents[2]
    path = root / "dev-docs" / "widget-reconcile" / "wave_a_param_mapping.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert "combo_box" in data["methods"]
