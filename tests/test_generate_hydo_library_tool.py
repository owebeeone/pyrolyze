from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

from pyrolyze_tools.generate_hydo_library import (
    generate_hydo_library_source,
    write_generated_hydo_library,
)


def test_generate_hydo_library_source_renders_mountable_specs_and_ui_interface() -> None:
    source = generate_hydo_library_source()

    assert "@ui_interface" in source
    assert "class HydoUiLibrary:" in source
    assert "MOUNTABLE_SPECS: ClassVar[frozendict[str, UiWidgetSpec]]" in source
    assert "WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = MOUNTABLE_SPECS" in source
    assert '"main_widget": MountPointSpec(' in source
    assert '"title_bar_widget": MountPointSpec(' in source
    assert '"standard": MountPointSpec(' in source
    assert "def CHydoWindow(" in source
    assert "def CHydoWidget(" in source
    assert "def CHydoMenu(" in source
    assert "name: str" in source
    assert "title: str = ''" in source
    assert "geometry_x: int | MissingType = MISSING" in source


def test_write_generated_hydo_library_writes_importable_module(tmp_path: Path) -> None:
    output_file = write_generated_hydo_library(output_dir=tmp_path)

    assert output_file.name == "generated_hydo_library.py"
    assert output_file.exists()

    spec = importlib.util.spec_from_file_location("generated_hydo_library", output_file)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["generated_hydo_library"] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop("generated_hydo_library", None)

    assert hasattr(module, "HydoUiLibrary")
    assert "HydoWindow" in module.HydoUiLibrary.MOUNTABLE_SPECS
