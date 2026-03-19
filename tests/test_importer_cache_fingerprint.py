from __future__ import annotations

from pathlib import Path

from pyrolyze.compiler import kernel_loader
from pyrolyze.importer import compute_source_fingerprint


def test_source_fingerprint_changes_when_transformer_fingerprint_changes() -> None:
    source = "#@pyrolyze\nVALUE = 1\n"

    first = compute_source_fingerprint(
        source,
        mtime=123.0,
        python_magic="aabbccdd",
        transformer_fingerprint="kernel=v3_14;schema=1",
    )
    second = compute_source_fingerprint(
        source,
        mtime=123.0,
        python_magic="aabbccdd",
        transformer_fingerprint="kernel=v3_15;schema=1",
    )

    assert first != second


def test_active_transformer_fingerprint_includes_selected_kernel_and_cache_schema(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        kernel_loader,
        "_available_kernel_versions",
        lambda: [(3, 12), (3, 14)],
    )

    fingerprint = kernel_loader.active_transformer_fingerprint((3, 99))

    assert fingerprint.startswith("cache_schema=1;kernel=v3_14;transform_hash=")
    assert len(fingerprint.rsplit("=", 1)[-1]) == 16


def test_persistent_cache_path_changes_with_transformer_fingerprint(tmp_path: Path) -> None:
    source = "#@pyrolyze\nVALUE = 1\n"
    first_key = compute_source_fingerprint(
        source,
        mtime=123.0,
        python_magic="aabbccdd",
        transformer_fingerprint="kernel=v3_14;cache_schema=1",
    )
    second_key = compute_source_fingerprint(
        source,
        mtime=123.0,
        python_magic="aabbccdd",
        transformer_fingerprint="kernel=v3_15;cache_schema=1",
    )

    assert first_key != second_key
