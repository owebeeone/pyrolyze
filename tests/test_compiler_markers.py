from __future__ import annotations

from pathlib import Path

from pyrolyze.compiler import compile_source
from pyrolyze.importer import should_transform


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


def test_compile_source_discovers_pyrolyse_decorated_components() -> None:
    source = """
from pyrolyze.api import pyrolyse, use_state

@pyrolyse
def profile_form():
    name, set_name = use_state("")
    return {"name": name, "set_name": set_name}
"""

    artifact = compile_source(source, module_name="profile_form")

    assert "profile_form" in artifact.components
    assert [hook.name for hook in artifact.metadata.hooks] == ["use_state"]


def test_compile_source_discovers_class_members_and_explicit_nested_pyrolyze_functions() -> None:
    source = """
from pyrolyze.api import pyrolyse, pyrolyze_slotted, use_state

class Panel:
    @pyrolyse
    def render(self):
        @pyrolyse
        def inner():
            count, set_count = use_state(0)
        inner()

    @classmethod
    @pyrolyse
    def build(cls):
        pass

    @staticmethod
    @pyrolyse
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
    assert [(hook.name, hook.component) for hook in artifact.metadata.hooks] == [
        ("use_state", "Panel.render.<locals>.inner")
    ]
