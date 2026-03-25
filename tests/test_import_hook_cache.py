from __future__ import annotations

from types import ModuleType

from pyrolyze import import_hook
from pyrolyze.importer import BytecodeCache


class _DelegateLoader:
    def __init__(self, source: str) -> None:
        self._source = source

    def get_source(self, fullname: str) -> str:
        del fullname
        return self._source

    def exec_module(self, module: ModuleType) -> None:
        exec(compile(self._source, module.__file__ or "<module>", "exec"), module.__dict__)


def test_import_loader_cache_misses_when_transformer_fingerprint_changes(
    monkeypatch,
    tmp_path,
) -> None:
    source = "#@pyrolyze\nVALUE = 1\n"
    path = tmp_path / "example_module.py"
    path.write_text(source, encoding="utf-8")

    cache = BytecodeCache()
    calls: list[tuple[str, str]] = []

    def fake_compiler(src: str, *, module_name: str, filename: str) -> dict[str, str]:
        calls.append((module_name, filename))
        return {"module_name": module_name, "filename": filename, "source": src}

    fingerprints = iter(
        [
            "cache_schema=1;kernel=v3_14;transform_hash=first",
            "cache_schema=1;kernel=v3_14;transform_hash=second",
        ]
    )
    monkeypatch.setattr(
        import_hook.kernel_loader,
        "active_transformer_fingerprint",
        lambda: next(fingerprints),
    )

    loader = import_hook._PyRolyzeLoader(
        fullname="example_module",
        path=str(path),
        delegate=_DelegateLoader(source),
        compiler_fn=fake_compiler,
        cache=cache,
    )

    first_module = ModuleType("example_module")
    first_module.__file__ = str(path)
    loader.exec_module(first_module)

    second_module = ModuleType("example_module")
    second_module.__file__ = str(path)
    loader.exec_module(second_module)

    assert len(calls) == 2


def test_cache_mtime_changes_when_transformer_fingerprint_changes() -> None:
    stat_mtime_ns = 1_234_567_890

    first = import_hook._cache_mtime_with_transformer_fingerprint(
        stat_mtime_ns=stat_mtime_ns,
        transformer_fingerprint="cache_schema=1;kernel=v3_14;transform_hash=first",
    )
    second = import_hook._cache_mtime_with_transformer_fingerprint(
        stat_mtime_ns=stat_mtime_ns,
        transformer_fingerprint="cache_schema=1;kernel=v3_14;transform_hash=second",
    )

    assert first != second


def test_cache_mtime_is_stable_when_transformer_fingerprint_is_unchanged() -> None:
    stat_mtime_ns = 1_234_567_890
    fingerprint = "cache_schema=1;kernel=v3_14;transform_hash=stable"

    first = import_hook._cache_mtime_with_transformer_fingerprint(
        stat_mtime_ns=stat_mtime_ns,
        transformer_fingerprint=fingerprint,
    )
    second = import_hook._cache_mtime_with_transformer_fingerprint(
        stat_mtime_ns=stat_mtime_ns,
        transformer_fingerprint=fingerprint,
    )

    assert first == second
