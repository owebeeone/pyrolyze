from __future__ import annotations

from pathlib import Path

from tests.versioned_test_harness import (
    actual_results_dir,
    discover_supported_kernel_tags,
    kernel_tag_for_runtime,
    load_install_requirements,
    normalize_kernel_tag,
    runtime_tag,
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


def test_runtime_and_actual_results_paths_are_versioned() -> None:
    project_root = Path("/tmp/project")

    assert runtime_tag((3, 15)) == "py3_15"
    assert kernel_tag_for_runtime((3, 15), ("v3_14",)) == "v3_14"
    assert actual_results_dir(project_root, runtime_version=(3, 15), kernel_tag="v3_14") == (
        project_root / "tests" / "actual_test_results" / "py3_15" / "v3_14"
    )


def test_normalize_kernel_tag_accepts_multiple_spellings() -> None:
    assert normalize_kernel_tag("v3_14") == "v3_14"
    assert normalize_kernel_tag("3.14") == "v3_14"
    assert normalize_kernel_tag("3_14") == "v3_14"
