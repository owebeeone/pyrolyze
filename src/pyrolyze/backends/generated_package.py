"""Lightweight completeness checks; builds validate hashes, resolution checks groups."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath


def admit_generated_package(package_file: str, generation: str | None = None) -> None:
    root = Path(package_file).parent
    marker = root.parent / f".{root.name}.promotion.json"
    if marker.exists() or marker.is_symlink():
        raise RuntimeError("generated publication pending; recover before import")
    if root.is_symlink() or (root / "inventory.json").is_symlink():
        raise ValueError("generated package and inventory must not be symlinks")
    inventory = json.loads((root / "inventory.json").read_bytes())
    if not isinstance(inventory, dict) or inventory.get("schema_revision") != 1:
        raise ValueError("invalid generated inventory")
    files = inventory.get("files")
    if not isinstance(files, dict) or not {"__init__.py", "index.py", "facade.py", "facade.pyi"}.issubset(files):
        raise ValueError("incomplete generated inventory")
    if generation is not None and inventory.get("generation") != generation:
        raise ValueError("generated index inventory mismatch")
    for name in files:
        if not isinstance(name, str) or not name:
            raise ValueError("invalid generated artifact name")
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != name or "\\" in name:
            raise ValueError("invalid generated artifact name")
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing generated artifact: {name}")
