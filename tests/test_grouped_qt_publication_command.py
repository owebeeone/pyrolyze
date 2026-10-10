from __future__ import annotations

from pathlib import Path
from collections.abc import Callable
import subprocess

import pytest

from pyrolyze_tools import generate_grouped_qt_library as command
from pyrolyze_tools import generate_grouped_tk_library as tk_command
from pyrolyze_tools.generate_grouped_native_library import write_grouped_library
from pyrolyze_tools.generate_semantic_library import DiscoveredWidgetClass
from pyrolyze_tools.generated_library_publication import validate_generation


@pytest.mark.parametrize("entry_point", [command.main, tk_command.main], ids=["qt", "tk"])
def test_failed_generator_process_never_promotes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                               entry_point: Callable[[list[str]], int]) -> None:
    widget = DiscoveredWidgetClass("builtins", "Button", "CButton", ())
    active = tmp_path / "active"
    stage = tmp_path / "stage"
    write_grouped_library("builtins", (widget,), families={"CButton": "controls"},
                          maximum_kinds=1, output_dir=active)
    old = validate_generation(active)
    def fail(*args: object, **kwargs: object) -> None:
        raise subprocess.CalledProcessError(1, "generator")
    monkeypatch.setattr(subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError):
        entry_point(["--maximum-kinds", "4", "--staging-dir", str(stage), "--promote-to", str(active)])
    assert validate_generation(active) == old
    assert not stage.exists()
