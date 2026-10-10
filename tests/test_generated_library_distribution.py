from __future__ import annotations

import importlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile

import pytest

from pyrolyze_tools.generate_grouped_native_library import write_grouped_library
from pyrolyze_tools.generate_semantic_library import DiscoveredWidgetClass


def _project(root: Path) -> Path:
    package = root / "src" / "fixture"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    generated = package / "generated"
    widget = DiscoveredWidgetClass("builtins", "Button", "CButton", ())
    write_grouped_library("builtins", (widget,), families={"CButton": "controls"},
                          maximum_kinds=1, output_dir=generated)
    return generated


@pytest.mark.parametrize("damage", ("pending", "modified", "no_inventory", "missing_tree"))
def test_build_rejects_unadmitted_sources(tmp_path: Path, damage: str) -> None:
    backend = importlib.import_module("pyrolyze_build_backend")
    generated = _project(tmp_path)
    if damage == "pending":
        (generated.parent / ".generated.promotion.json").write_text("{}")
    elif damage == "modified":
        (generated / "facade.py").write_text("changed = True\n")
    elif damage == "no_inventory":
        (generated / "inventory.json").unlink()
    else:
        (tmp_path / "pyproject.toml").write_text(
            '[tool.pyrolyze]\ngenerated-package-directories = ["src/fixture/generated"]\n')
        shutil.rmtree(generated)
    with pytest.raises((RuntimeError, ValueError, FileNotFoundError)):
        backend.validate_generated_sources(tmp_path)


def test_distributions_include_every_generated_artifact(tmp_path: Path) -> None:
    repository = Path(__file__).resolve().parents[1]
    generated = _project(tmp_path)
    shutil.copy2(repository / "pyrolyze_build_backend.py", tmp_path)
    shutil.copytree(repository / "pyrolyze_tools", tmp_path / "pyrolyze_tools",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(repository / "MANIFEST.in", tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["setuptools>=68", "wheel"]\n'
        'build-backend = "pyrolyze_build_backend"\nbackend-path = ["."]\n'
        '[project]\nname = "generated-fixture"\nversion = "0.0.0"\n'
        '[tool.setuptools]\npackage-dir = {"" = "src"}\n'
        '[tool.setuptools.packages.find]\nwhere = ["src"]\n'
        '[tool.setuptools.package-data]\n"*" = ["*.pyi", "inventory.json"]\n'
    )
    subprocess.run([sys.executable, "-c", "import pyrolyze_build_backend as b; "
                    "b.build_sdist('dist'); b.build_wheel('dist')"],
                   cwd=tmp_path, check=True, capture_output=True, text=True)
    files = set(json.loads((generated / "inventory.json").read_bytes())["files"])
    files.add("inventory.json")
    with zipfile.ZipFile(next((tmp_path / "dist").glob("*.whl"))) as archive:
        assert {f"fixture/generated/{name}" for name in files}.issubset(archive.namelist())
    with tarfile.open(next((tmp_path / "dist").glob("*.tar.gz"))) as archive:
        members = archive.getnames()
        prefix = members[0].split("/", 1)[0]
        assert {f"{prefix}/src/fixture/generated/{name}" for name in files}.issubset(members)
        assert f"{prefix}/pyrolyze_build_backend.py" in members
        assert f"{prefix}/pyrolyze_tools/generated_library_publication.py" in members
        unpacked = tmp_path / "unpacked"
        archive.extractall(unpacked, filter="data")
    subprocess.run([sys.executable, "-c", "import pyrolyze_build_backend as b; b.build_wheel('rebuilt')"],
                   cwd=unpacked / prefix, check=True, capture_output=True, text=True)
    with zipfile.ZipFile(next((unpacked / prefix / "rebuilt").glob("*.whl"))) as archive:
        assert {f"fixture/generated/{name}" for name in files}.issubset(archive.namelist())
    (tmp_path / "build" / "lib" / "fixture" / "generated" / "stale.py").write_text("obsolete = True\n")
    rejected = subprocess.run([sys.executable, "-c", "import pyrolyze_build_backend as b; b.build_wheel('bad')"],
                              cwd=tmp_path, capture_output=True, text=True)
    assert rejected.returncode != 0
    assert "artifact inventory mismatch" in rejected.stderr
