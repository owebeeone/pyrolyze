from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from pyrolyze_tools import generate_grouped_qt_library as command
from pyrolyze_tools.generate_grouped_native_library import write_grouped_library
from pyrolyze_tools.generate_semantic_library import DiscoveredWidgetClass
from pyrolyze_tools.generated_library_publication import validate_generation


def test_failed_generator_process_never_promotes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    widget = DiscoveredWidgetClass("builtins", "Button", "CButton", ())
    active = tmp_path / "active"
    stage = tmp_path / "stage"
    write_grouped_library("builtins", (widget,), families={"CButton": "controls"},
                          maximum_kinds=1, output_dir=active)
    old = validate_generation(active)
    monkeypatch.setattr(command, "discover_widget_classes", lambda _: [widget])
    monkeypatch.setattr(command, "load_learnings", lambda _: {})
    def fail(*args: object, **kwargs: object) -> None:
        raise subprocess.CalledProcessError(1, "generator")
    monkeypatch.setattr(subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError):
        command.main(["--maximum-kinds", "4", "--staging-dir", str(stage), "--promote-to", str(active)])
    assert validate_generation(active) == old
    assert not stage.exists()
