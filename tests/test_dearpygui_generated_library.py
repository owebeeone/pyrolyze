"""Regression checks for the generated DearPyGui ``DearPyGuiUiLibrary``."""

from __future__ import annotations

from pyrolyze.backends.dearpygui.generated_library import DearPyGuiUiLibrary


def test_generated_library_covers_canonical_mountables() -> None:
    specs = DearPyGuiUiLibrary.WIDGET_SPECS
    assert len(specs) >= 180
    assert "DpgButton" in specs
    assert "DpgWindow" in specs
    assert "DpgDrawLayerDrawCmd" in specs
    assert specs["DpgButton"].mounted_type_name.endswith("DpgButtonItem")


def test_font_registry_mounts_hand_class() -> None:
    spec = DearPyGuiUiLibrary.WIDGET_SPECS["DpgFontRegistry"]
    assert spec.mounted_type_name.endswith("DpgFontRegistryItem")
    assert "standard" in spec.mount_points
