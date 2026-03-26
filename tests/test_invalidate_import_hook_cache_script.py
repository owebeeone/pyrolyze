from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "invalidate_import_hook_cache.py"
)
SPEC = importlib.util.spec_from_file_location("invalidate_import_hook_cache", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_remove_module_pycache_only_removes_matching_entries(tmp_path: Path) -> None:
    module_path = tmp_path / "demo.py"
    module_path.write_text("VALUE = 1\n", encoding="utf-8")

    pycache = tmp_path / "__pycache__"
    pycache.mkdir()
    victim = pycache / "demo.cpython-312.pyc"
    survivor = pycache / "other.cpython-312.pyc"
    victim.write_bytes(b"pyc")
    survivor.write_bytes(b"pyc")

    results = MODULE.remove_module_pycache(module_path)

    assert not victim.exists()
    assert survivor.exists()
    assert any(result.action == "remove" and result.path == victim for result in results)


def test_touch_file_updates_mtime(tmp_path: Path) -> None:
    path = tmp_path / "touch_me.py"
    path.write_text("VALUE = 1\n", encoding="utf-8")
    before = path.stat().st_mtime_ns

    result = MODULE.touch_file(path)

    after = path.stat().st_mtime_ns
    assert after >= before
    assert result.action == "touch"
    assert result.path == path


def test_remove_persistent_cache_removes_directory(tmp_path: Path) -> None:
    cache_dir = tmp_path / ".pyrolyze_cache"
    cache_dir.mkdir()
    (cache_dir / "entry.pyrolyze-cache").write_bytes(b"cache")

    result = MODULE.remove_persistent_cache(cache_dir)

    assert not cache_dir.exists()
    assert result.action == "remove"
    assert result.path == cache_dir


def test_main_defaults_to_transformer_command(tmp_path: Path, monkeypatch) -> None:
    touch_path = tmp_path / "compiler.py"
    touch_path.write_text("VALUE = 1\n", encoding="utf-8")

    calls: list[Path] = []

    def fake_touch(path: Path):
        calls.append(path)
        return MODULE.InvalidateResult("touch", path, "updated mtime")

    monkeypatch.setattr(MODULE, "touch_file", fake_touch)

    exit_code = MODULE.main(["--touch-file", str(touch_path)])

    assert exit_code == 0
    assert calls == [touch_path.resolve()]
