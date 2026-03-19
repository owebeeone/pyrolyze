from __future__ import annotations

from io import StringIO
from pathlib import Path

from tests.versioned_test_harness import (
    actual_results_dir,
    build_run_tests_invocation,
    data_golden_dir,
    data_gold_src_dir,
    discover_supported_kernel_tags,
    kernel_tag_for_runtime,
    load_install_requirements,
    load_golden_cases,
    load_supported_runtime_specs,
    normalize_kernel_tag,
    report_run_tests_all_results,
    resolve_requested_runtime_specs,
    runtime_tag,
    should_passthrough_run_tests_all_output,
)


def test_discover_supported_kernel_tags_reads_version_directories(tmp_path: Path) -> None:
    kernels_dir = tmp_path / "src" / "pyrolyze" / "compiler" / "kernels"
    (kernels_dir / "v3_14").mkdir(parents=True)
    (kernels_dir / "v3_15").mkdir()
    (kernels_dir / "not_a_kernel").mkdir()

    assert discover_supported_kernel_tags(tmp_path) == ("v3_14", "v3_15")


def test_load_install_requirements_reads_project_and_test_dependencies(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[build-system]
requires = ["setuptools>=68", "wheel"]

[project]
dependencies = ["PySide6>=6.7,<7"]

[project.optional-dependencies]
test = ["pytest>=8", "pytest-cov>=5"]
""".strip(),
        encoding="utf-8",
    )

    assert load_install_requirements(pyproject) == [
        "setuptools>=68",
        "wheel",
        "PySide6>=6.7,<7",
        "pytest>=8",
        "pytest-cov>=5",
    ]


def test_load_golden_cases_reads_manifest_mapping(tmp_path: Path) -> None:
    manifest = tmp_path / "tests" / "data" / "gold_cases.toml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        """
[cases]
"phase3_greeting.py" = "golden.phase3.greeting"
"phase4_stats_panel.py" = "golden.phase4.stats_panel"
""".strip(),
        encoding="utf-8",
    )

    assert load_golden_cases(tmp_path) == {
        "phase3_greeting.py": "golden.phase3.greeting",
        "phase4_stats_panel.py": "golden.phase4.stats_panel",
    }


def test_load_supported_runtime_specs_reads_pyproject_matrix(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[tool.pyrolyze.test-matrix]
python = ["3.12", "3.13", "3.14", "3.15"]
""".strip(),
        encoding="utf-8",
    )

    assert load_supported_runtime_specs(pyproject) == ("3.12", "3.13", "3.14", "3.15")


def test_resolve_requested_runtime_specs_defaults_to_supported_matrix(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[tool.pyrolyze.test-matrix]
python = ["3.12", "3.13", "3.14", "3.15"]
""".strip(),
        encoding="utf-8",
    )

    assert resolve_requested_runtime_specs(pyproject, requested=None) == (
        "3.12",
        "3.13",
        "3.14",
        "3.15",
    )
    assert resolve_requested_runtime_specs(pyproject, requested=["3.13", "3.15"]) == (
        "3.13",
        "3.15",
    )


def test_build_run_tests_invocation_preserves_pytest_args() -> None:
    script_path = Path("/tmp/project/tests/versioned_test_harness.py")

    assert build_run_tests_invocation(
        script_path=script_path,
        python_executable="/tmp/project/.venv/bin/python",
        python_spec="3.15",
        venv_root="tests/.uv-venvs",
        recreate=True,
        pytest_args=["tests/test_ast_goldens.py", "-q"],
    ) == [
        "/tmp/project/.venv/bin/python",
        str(script_path),
        "run-tests",
        "--python",
        "3.15",
        "--venv-root",
        "tests/.uv-venvs",
        "--recreate",
        "--pytest-args",
        "tests/test_ast_goldens.py",
        "-q",
    ]


def test_report_run_tests_all_results_can_show_passing_output_serially() -> None:
    stdout = StringIO()
    stderr = StringIO()

    report_run_tests_all_results(
        [
            ("3.12", 0, "alpha out\n", ""),
            ("3.13", 0, "beta out\n", "beta err\n"),
        ],
        show_output=True,
        stdout=stdout,
        stderr=stderr,
    )

    assert stdout.getvalue() == (
        "3.12: PASS\n"
        "--- 3.12 stdout ---\n"
        "alpha out\n"
        "3.13: PASS\n"
        "--- 3.13 stdout ---\n"
        "beta out\n"
    )
    assert stderr.getvalue() == (
        "--- 3.13 stderr ---\n"
        "beta err\n"
    )


def test_should_passthrough_run_tests_all_output_only_for_single_selected_version() -> None:
    assert should_passthrough_run_tests_all_output(show_output=False, runtime_specs=("3.12",)) is False
    assert should_passthrough_run_tests_all_output(show_output=True, runtime_specs=("3.12",)) is True
    assert should_passthrough_run_tests_all_output(show_output=True, runtime_specs=("3.12", "3.13")) is False


def test_runtime_and_actual_results_paths_are_versioned() -> None:
    project_root = Path("/tmp/project")

    assert runtime_tag((3, 15)) == "py3_15"
    assert kernel_tag_for_runtime((3, 15), ("v3_14",)) == "v3_14"
    assert data_gold_src_dir(project_root) == project_root / "tests" / "data" / "gold_src"
    assert data_golden_dir(project_root, kernel_tag="v3_14") == (
        project_root / "tests" / "data" / "v3_14" / "goldens"
    )
    assert actual_results_dir(project_root, runtime_version=(3, 15), kernel_tag="v3_14") == (
        project_root / "tests" / "actual_test_results" / "py3_15" / "v3_14"
    )


def test_normalize_kernel_tag_accepts_multiple_spellings() -> None:
    assert normalize_kernel_tag("v3_14") == "v3_14"
    assert normalize_kernel_tag("3.14") == "v3_14"
    assert normalize_kernel_tag("3_14") == "v3_14"
