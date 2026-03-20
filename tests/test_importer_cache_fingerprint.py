from __future__ import annotations

from pathlib import Path

from pyrolyze.compiler import kernel_loader
from pyrolyze.importer import compute_source_fingerprint


def _build_fake_compiler_tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    compiler_dir = tmp_path / "compiler"
    compiler_dir.mkdir()
    shared_file = compiler_dir / "shared.py"
    shared_file.write_text("VALUE = 1\n", encoding="utf-8")
    kernel_dir = compiler_dir / "kernels" / "v3_14"
    kernel_dir.mkdir(parents=True)
    kernel_file = kernel_dir / "kernel.py"
    kernel_file.write_text("KERNEL = 1\n", encoding="utf-8")
    return compiler_dir, shared_file, kernel_file


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


def test_active_transformer_fingerprint_invalidates_when_transformer_source_changes(
    monkeypatch,
    tmp_path: Path,
) -> None:
    compiler_dir, _, kernel_file = _build_fake_compiler_tree(tmp_path)
    monkeypatch.setattr(kernel_loader, "_compiler_dir", lambda: compiler_dir)
    monkeypatch.setattr(kernel_loader, "_available_kernel_versions", lambda: [(3, 14)])
    kernel_loader.invalidate_transformer_fingerprint_cache()

    first = kernel_loader.active_transformer_fingerprint((3, 14))
    kernel_file.write_text("KERNEL = 2\n# in-process edit\n", encoding="utf-8")
    second = kernel_loader.active_transformer_fingerprint((3, 14))

    assert first != second


def test_active_transformer_fingerprint_invalidates_when_transformer_file_set_changes(
    monkeypatch,
    tmp_path: Path,
) -> None:
    compiler_dir, _, _ = _build_fake_compiler_tree(tmp_path)
    monkeypatch.setattr(kernel_loader, "_compiler_dir", lambda: compiler_dir)
    monkeypatch.setattr(kernel_loader, "_available_kernel_versions", lambda: [(3, 14)])
    kernel_loader.invalidate_transformer_fingerprint_cache()

    first = kernel_loader.active_transformer_fingerprint((3, 14))
    extra_file = compiler_dir / "added.py"
    extra_file.write_text("EXTRA = 1\n", encoding="utf-8")
    second = kernel_loader.active_transformer_fingerprint((3, 14))
    extra_file.unlink()
    third = kernel_loader.active_transformer_fingerprint((3, 14))

    assert first != second
    assert second != third


def test_transform_hash_cache_hits_when_source_state_is_unchanged(
    monkeypatch,
    tmp_path: Path,
) -> None:
    compiler_dir, _, _ = _build_fake_compiler_tree(tmp_path)
    monkeypatch.setattr(kernel_loader, "_compiler_dir", lambda: compiler_dir)
    monkeypatch.setattr(kernel_loader, "_available_kernel_versions", lambda: [(3, 14)])
    kernel_loader.invalidate_transformer_fingerprint_cache()

    first = kernel_loader.active_transformer_fingerprint((3, 14))
    before = kernel_loader._transform_hash_for_selected_kernel.cache_info()
    second = kernel_loader.active_transformer_fingerprint((3, 14))
    after = kernel_loader._transform_hash_for_selected_kernel.cache_info()

    assert first == second
    assert after.hits > before.hits
