from __future__ import annotations

import hashlib
import importlib
from functools import lru_cache
import re
import sys
from pathlib import Path


_VERSION_DIR_RE = re.compile(r"^v(?P<major>\d+)_(?P<minor>\d+)$")
TRANSFORMER_CACHE_SCHEMA = 1


def load_ast_kernel(version_info: tuple[int, int] | None = None):
    major_minor = version_info or (sys.version_info.major, sys.version_info.minor)
    selected = select_kernel_version(major_minor)
    module_name = f"{__package__}.kernels.v{selected[0]}_{selected[1]}.kernel"
    return importlib.import_module(module_name)


def active_transformer_fingerprint(version_info: tuple[int, int] | None = None) -> str:
    major_minor = version_info or (sys.version_info.major, sys.version_info.minor)
    selected = select_kernel_version(major_minor)
    transform_hash = _transform_hash_for_selected_kernel(selected)
    return (
        f"cache_schema={TRANSFORMER_CACHE_SCHEMA};"
        f"kernel=v{selected[0]}_{selected[1]};"
        f"transform_hash={transform_hash}"
    )


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


@lru_cache(maxsize=None)
def _transform_hash_for_selected_kernel(version: tuple[int, int]) -> str:
    compiler_dir = Path(__file__).resolve().parent
    kernel_dir = compiler_dir / "kernels" / f"v{version[0]}_{version[1]}"

    digest = hashlib.sha256()
    digest.update(f"schema:{TRANSFORMER_CACHE_SCHEMA}".encode("utf-8"))
    digest.update(f"kernel:v{version[0]}_{version[1]}".encode("utf-8"))

    for path in _fingerprint_files(compiler_dir=compiler_dir, kernel_dir=kernel_dir):
        try:
            payload = path.read_bytes()
        except OSError:
            payload = b"<missing>"
        digest.update(str(path.relative_to(compiler_dir)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\0")

    return digest.hexdigest()[:16]


def _fingerprint_files(*, compiler_dir: Path, kernel_dir: Path) -> list[Path]:
    shared_files = [
        path
        for path in compiler_dir.glob("*.py")
        if path.is_file()
    ]
    kernel_files = [
        path
        for path in kernel_dir.rglob("*.py")
        if path.is_file() and "__pycache__" not in path.parts
    ]
    return sorted([*shared_files, *kernel_files])
