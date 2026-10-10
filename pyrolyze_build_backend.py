"""Setuptools hooks with offline generated-directory admission."""

from __future__ import annotations

from pathlib import Path
from collections.abc import Callable, Mapping
from hashlib import sha256
import json
import tarfile
import tomllib
import zipfile
from typing import Any

from pyrolyze_tools.generated_library_publication import require_admitted_generation


def validate_generated_sources(root: Path) -> dict[str, str]:
    source = root / "src"
    for marker in source.rglob(".*.promotion.json"):
        raise RuntimeError(f"generated publication pending: {marker.relative_to(root)}")
    directories = {path.parent for path in source.rglob("inventory.json")}
    configuration = root / "pyproject.toml"
    if configuration.exists():
        project = tomllib.loads(configuration.read_text(encoding="utf-8"))
        for name in project.get("tool", {}).get("pyrolyze", {}).get("generated-package-directories", []):
            path = Path(name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("generated package directories must be repository-relative")
            directories.add(root / path)
    # Recognize generated trees even when the final inventory was never written.
    for facade in source.rglob("facade.py"):
        if "LazyLibraryCatalog" in facade.read_text(encoding="utf-8"):
            directories.add(facade.parent)
    return {directory.relative_to(source).as_posix(): require_admitted_generation(directory)
            for directory in sorted(directories)}


def _validate_archive(expected: Mapping[str, str], members: set[str],
                      read: Callable[[str], bytes], prefix: str) -> None:
    for directory, identity in expected.items():
        base = f"{prefix}{directory}/"
        inventory_name = base + "inventory.json"
        if inventory_name not in members:
            raise ValueError("artifact inventory mismatch: missing inventory")
        raw = read(inventory_name)
        if sha256(raw).hexdigest() != identity:
            raise ValueError("artifact inventory mismatch: mixed inventory")
        files = json.loads(raw)["files"]
        actual = {name[len(base):] for name in members if name.startswith(base)}
        if actual != {*files, "inventory.json"}:
            raise ValueError("artifact inventory mismatch: missing or obsolete files")
        for name, digest in files.items():
            if sha256(read(base + name)).hexdigest() != digest:
                raise ValueError(f"artifact inventory mismatch: {name}")


def validate_distribution(path: Path, expected: Mapping[str, str]) -> None:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            _validate_archive(expected, {item.filename for item in archive.infolist() if not item.is_dir()},
                              archive.read, "")
    else:
        with tarfile.open(path) as archive:
            members = archive.getmembers()
            prefix = members[0].name.split("/", 1)[0] + "/src/"
            def read(name: str) -> bytes:
                stream = archive.extractfile(name)
                if stream is None:
                    raise ValueError("artifact inventory mismatch: unreadable file")
                with stream:
                    return stream.read()
            _validate_archive(expected, {item.name for item in members if item.isfile()}, read, prefix)


def __getattr__(name: str) -> Any:
    from setuptools import build_meta

    hook = getattr(build_meta, name)
    if not name.startswith(("build_", "get_requires_for_build_", "prepare_metadata_for_build_")):
        return hook

    def admitted_hook(*args: Any, **kwargs: Any) -> Any:
        expected = validate_generated_sources(Path(__file__).resolve().parent)
        result = hook(*args, **kwargs)
        if name in {"build_wheel", "build_sdist"}:
            directory = args[0] if args else kwargs["wheel_directory" if name == "build_wheel" else "sdist_directory"]
            validate_distribution(Path(directory) / result, expected)
        return result

    return admitted_hook
