from __future__ import annotations

import json
from pathlib import Path

from pyrolyze.compiler import (
    analyze_source,
    build_debug_artifacts_for_source,
    compile_source,
    emit_transformed_source,
    load_transformed_namespace,
)
from pyrolyze.compiler.debug import write_debug_artifacts


def test_analyze_source_returns_component_plan_for_pyrolyse_function() -> None:
    source = """
from pyrolyze.api import pyrolyse, pyrolyze_slotted

@pyrolyse
def profile_form():
    pass

@pyrolyze_slotted
def helper(value):
    return value
"""

    plan = analyze_source(source, module_name="example.profile_form")

    assert plan.module_name == "example.profile_form"
    assert [component.public_name for component in plan.component_plans] == ["profile_form"]
    assert not plan.diagnostics


def test_emit_transformed_source_returns_helper_mode_python() -> None:
    source = """
from pyrolyze.api import pyrolyse

@pyrolyse
def profile_form():
    pass
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.profile_form",
    )

    assert "def profile_form" in transformed
    assert "pyrolyse" in transformed


def test_load_transformed_namespace_executes_module_source() -> None:
    source = """
VALUE = 41

def plus_one(value):
    return value + 1
"""

    namespace = load_transformed_namespace(
        source,
        module_name="example.math",
        filename="/virtual/example/math.py",
    )

    assert namespace["VALUE"] == 41
    assert namespace["plus_one"](1) == 2
    assert namespace["__name__"] == "example.math"


def test_write_debug_artifacts_preserves_module_path_structure(tmp_path: Path) -> None:
    source = """
from pyrolyze.api import pyrolyse

@pyrolyse
def profile_form():
    pass
"""

    artifacts = build_debug_artifacts_for_source(
        source,
        module_name="pkg.sub.profile_form",
        filename="/workspace/pkg/sub/profile_form.py",
    )

    write_debug_artifacts(
        artifacts,
        out_dir=tmp_path,
        module_name="pkg.sub.profile_form",
    )

    transformed_path = tmp_path / "pkg" / "sub" / "profile_form.py"
    provenance_path = tmp_path / "pkg" / "sub" / "profile_form.pyrolyze.provenance.json"
    source_map_path = tmp_path / "pkg" / "sub" / "profile_form.pyrolyze.sourcemap.json"
    artifact_path = tmp_path / "pkg" / "sub" / "profile_form.pyrolyze.artifact.json"

    assert transformed_path.read_text(encoding="utf-8") == artifacts.transformed_source
    assert json.loads(provenance_path.read_text(encoding="utf-8"))["module_name"] == "pkg.sub.profile_form"
    assert json.loads(source_map_path.read_text(encoding="utf-8"))["module_name"] == "pkg.sub.profile_form"
    assert json.loads(artifact_path.read_text(encoding="utf-8"))["generated_relpath"] == "pkg/sub/profile_form.py"


def test_compile_source_dump_preserves_package_init_layout(
    monkeypatch,
    tmp_path: Path,
) -> None:
    source = """
from pyrolyze.api import pyrolyse

@pyrolyse
def init_component():
    pass
"""

    monkeypatch.setenv("PYROLYZE_DUMP_TRANSFORMED_PY", "1")
    monkeypatch.setenv("PYROLYZE_DUMP_TRANSFORMED_DIR", str(tmp_path))

    compile_source(
        source,
        module_name="pkg.sub",
        filename="/workspace/pkg/sub/__init__.py",
    )

    transformed_path = tmp_path / "pkg" / "sub" / "__init__.py"
    provenance_path = tmp_path / "pkg" / "sub" / "__init__.pyrolyze.provenance.json"
    source_map_path = tmp_path / "pkg" / "sub" / "__init__.pyrolyze.sourcemap.json"
    artifact_path = tmp_path / "pkg" / "sub" / "__init__.pyrolyze.artifact.json"

    assert transformed_path.exists()
    assert provenance_path.exists()
    assert source_map_path.exists()
    assert artifact_path.exists()


def test_compile_source_raw_fallback_still_writes_debug_artifacts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    source = """
from pyrolyze.api import pyrolyse

@pyrolyse
def unsupported_panel():
    exec("print('boom')")
"""

    monkeypatch.setenv("PYROLYZE_DUMP_TRANSFORMED_PY", "1")
    monkeypatch.setenv("PYROLYZE_DUMP_TRANSFORMED_DIR", str(tmp_path))

    artifact = compile_source(
        source,
        module_name="pkg.unsupported_panel",
        filename="/workspace/pkg/unsupported_panel.py",
        enable_raw_fallback=True,
    )

    assert artifact.non_reactive is True
    assert (tmp_path / "pkg" / "unsupported_panel.py").exists()
    assert (tmp_path / "pkg" / "unsupported_panel.pyrolyze.artifact.json").exists()
