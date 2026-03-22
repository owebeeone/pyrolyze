from __future__ import annotations

from pathlib import Path

import pytest

from pyrolyze.compiler import compile_source
from pyrolyze.compiler import PyRolyzeCompileError, emit_transformed_source
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.importer import should_transform
from pyrolyze.runtime import RenderContext, dirtyof


def test_should_transform_when_marker_is_first_line(tmp_path: Path) -> None:
    module_path = tmp_path / "first_line_example.py"
    source = "#@pyrolyze\nprint('hello')\n"
    module_path.write_text(source, encoding="utf-8")

    assert should_transform(
        module_name="first_line_example",
        file_path=str(module_path),
        source_text=source,
    )


def test_should_transform_when_marker_is_second_line(tmp_path: Path) -> None:
    module_path = tmp_path / "second_line_example.py"
    source = "#!/usr/bin/env python3\n#@pyrolyze\nprint('hello')\n"
    module_path.write_text(source, encoding="utf-8")

    assert should_transform(
        module_name="second_line_example",
        file_path=str(module_path),
        source_text=source,
    )


def test_should_not_transform_when_marker_is_not_in_first_two_lines(tmp_path: Path) -> None:
    module_path = tmp_path / "third_line_example.py"
    source = "#!/usr/bin/env python3\n# generated file\n#@pyrolyze\nprint('hello')\n"
    module_path.write_text(source, encoding="utf-8")

    assert not should_transform(
        module_name="third_line_example",
        file_path=str(module_path),
        source_text=source,
    )


def test_compile_source_discovers_pyrolyze_decorated_components() -> None:
    source = """
from pyrolyze.api import pyrolyze, use_state

@pyrolyze
def profile_form():
    name, set_name = use_state("")
    return {"name": name, "set_name": set_name}
"""

    artifact = compile_source(source, module_name="profile_form")

    assert "profile_form" in artifact.components
    assert artifact.metadata.hooks == []


def test_compile_source_discovers_class_members_and_explicit_nested_pyrolyze_functions() -> None:
    source = """
from pyrolyze.api import pyrolyze, pyrolyze_slotted, use_state

class Panel:
    @pyrolyze
    def render(self):
        @pyrolyze
        def inner():
            count, set_count = use_state(0)
        inner()

    @classmethod
    @pyrolyze
    def build(cls):
        pass

    @staticmethod
    @pyrolyze
    def show():
        pass

    @pyrolyze_slotted
    def helper(self, value):
        return value
"""

    artifact = compile_source(source, module_name="panel_module")

    assert "Panel.render" in artifact.components
    assert "Panel.build" in artifact.components
    assert "Panel.show" in artifact.components
    assert "Panel.render.<locals>.inner" in artifact.components
    assert "Panel.helper" not in artifact.components
    assert artifact.metadata.hooks == []


def test_pyrolyze_module_rejects_late_imports_after_executable_code() -> None:
    source = """
#@pyrolyze
value = 1
from demo.widgets import badge
"""

    with pytest.raises(PyRolyzeCompileError, match="top-of-file import prelude"):
        emit_transformed_source(
            source,
            module_name="late_import_example",
            filename="/virtual/late_import_example.py",
        )


def test_imported_ui_library_alias_does_not_capture_same_named_local_helper() -> None:
    source = """
#@pyrolyze
from pyrolyze.api import pyrolyze
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt

CALLS = []

def CQPushButton():
    CALLS.append("plain-helper")

@pyrolyze
def demo():
    CQPushButton()
"""

    namespace = load_transformed_namespace(
        source,
        module_name="collision_example",
        filename="/virtual/collision_example.py",
    )
    ctx = RenderContext()

    namespace["demo"]._pyrolyze_meta._func(ctx, dirtyof())

    assert namespace["CALLS"] == ["plain-helper"]
