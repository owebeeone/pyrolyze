from __future__ import annotations

import importlib
from pathlib import Path
import sys

import pytest

from pyrolyze_tools.generate_grouped_native_library import write_grouped_library
from pyrolyze_tools.generate_semantic_library import DiscoveredWidgetClass


@pytest.mark.parametrize("damage", ("pending", "missing_inventory", "missing_group"))
def test_package_import_refuses_unadmitted_generation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, damage: str
) -> None:
    package = "admission_fixture"
    root = tmp_path / package
    widget = DiscoveredWidgetClass("builtins", "Button", "CButton", ())
    write_grouped_library("builtins", (widget,), families={"CButton": "controls"},
                          maximum_kinds=1, output_dir=root)
    if damage == "pending":
        (tmp_path / f".{package}.promotion.json").write_text("{}")
    elif damage == "missing_inventory":
        (root / "inventory.json").unlink()
    else:
        next(root.glob("family_*.py")).unlink()
    monkeypatch.syspath_prepend(str(tmp_path))
    try:
        with pytest.raises((RuntimeError, ValueError, FileNotFoundError)):
            importlib.import_module(f"{package}.index")
        assert f"{package}.index" not in sys.modules
    finally:
        for name in tuple(sys.modules):
            if name == package or name.startswith(package + "."):
                sys.modules.pop(name, None)
