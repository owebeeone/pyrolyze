from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path


_VERSION_DIR_RE = re.compile(r"^v(?P<major>\d+)_(?P<minor>\d+)$")


def load_ast_kernel(version_info: tuple[int, int] | None = None):
    major_minor = version_info or (sys.version_info.major, sys.version_info.minor)
    selected = select_kernel_version(major_minor)
    module_name = f"{__package__}.kernels.v{selected[0]}_{selected[1]}.kernel"
    return importlib.import_module(module_name)


def select_kernel_version(
    version_info: tuple[int, int],
    *,
    available_versions: list[tuple[int, int]] | None = None,
) -> tuple[int, int]:
    versions = available_versions if available_versions is not None else _available_kernel_versions()
    if not versions:
        raise RuntimeError("No AST compiler kernels are available.")
    if version_info in versions:
        return version_info
    return max(versions)


def _available_kernel_versions() -> list[tuple[int, int]]:
    kernels_dir = Path(__file__).with_name("kernels")
    versions: list[tuple[int, int]] = []
    if not kernels_dir.exists():
        return versions
    for entry in kernels_dir.iterdir():
        if not entry.is_dir():
            continue
        match = _VERSION_DIR_RE.match(entry.name)
        if match is None:
            continue
        versions.append((int(match.group("major")), int(match.group("minor"))))
    versions.sort()
    return versions
