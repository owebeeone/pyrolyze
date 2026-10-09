from __future__ import annotations

import importlib.util
from types import ModuleType, SimpleNamespace

import pytest

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


def test_fresh_loader_reuses_transformed_python_bytecode_without_compiling(
    monkeypatch,
    tmp_path,
) -> None:
    source = "#@pyrolyze\nVALUE = 1\n"
    path = tmp_path / "cached_example.py"
    path.write_text(source, encoding="utf-8")
    calls: list[str] = []

    def fake_compiler(src: str, *, module_name: str, filename: str) -> SimpleNamespace:
        del src, filename
        calls.append(module_name)
        return SimpleNamespace(transformed_source="VALUE = 42\n")

    monkeypatch.setattr(
        import_hook.kernel_loader,
        "active_transformer_fingerprint",
        lambda: "cache_schema=1;kernel=v3_14;transform_hash=stable",
    )
    monkeypatch.setattr("sys.dont_write_bytecode", False)

    for _ in range(2):
        loader = import_hook._PyRolyzeLoader(
            fullname="cached_example",
            path=str(path),
            delegate=_DelegateLoader(source),
            compiler_fn=fake_compiler,
            cache=BytecodeCache(),
        )
        module = ModuleType("cached_example")
        module.__file__ = str(path)
        loader.exec_module(module)
        assert module.VALUE == 42

    assert calls == ["cached_example"]


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


@pytest.mark.parametrize("reuse_module", [False, True])
def test_warm_bytecode_keeps_diagnostics_lazy_and_preserves_module_getattr(
    monkeypatch,
    tmp_path,
    reuse_module,
) -> None:
    source = (
        "#@pyrolyze\nVALUE = 1\n"
        "def __getattr__(name):\n"
        "    if name == 'extra':\n"
        "        return 'authored fallback'\n"
        "    raise AttributeError(name)\n"
    )
    path = tmp_path / "diagnostic_example.py"
    path.write_text(source, encoding="utf-8")
    calls: list[str] = []

    def fake_compiler(src: str, *, module_name: str, filename: str) -> SimpleNamespace:
        del filename
        calls.append(module_name)
        return SimpleNamespace(transformed_source=src.replace("VALUE = 1\n", "VALUE = 42\n"))

    monkeypatch.setattr(
        import_hook.kernel_loader, "active_transformer_fingerprint", lambda: "stable",
    )
    monkeypatch.setattr("sys.dont_write_bytecode", False)
    module = ModuleType("diagnostic_example")
    module.__file__ = str(path)
    for _ in range(2):
        loader = import_hook._PyRolyzeLoader(
            fullname="diagnostic_example", path=str(path), delegate=_DelegateLoader(source),
            compiler_fn=fake_compiler, cache=BytecodeCache(),
        )
        if not reuse_module:
            module = ModuleType("diagnostic_example")
            module.__file__ = str(path)
        loader.exec_module(module)

    assert len(calls) == 1
    assert "__pyrolyze_artifact__" not in vars(module)
    assert module.extra == "authored fallback"
    with pytest.raises(AttributeError, match="missing"):
        getattr(module, "missing")
    # Diagnostic data describes the imported source, not a later file edit.
    path.write_text("#@pyrolyze\nVALUE = 99\n", encoding="utf-8")
    artifact = module.__pyrolyze_artifact__
    assert "VALUE = 42" in artifact.transformed_source
    assert module.__pyrolyze_artifact__ is artifact
    assert len(calls) == 2


@pytest.mark.parametrize("invalidation", ["source", "transformer", "magic", "truncated"])
def test_warm_bytecode_invalidates_and_recompiles(monkeypatch, tmp_path, invalidation) -> None:
    source = "#@pyrolyze\nVALUE = 1\n"
    path = tmp_path / "invalidated_example.py"
    path.write_text(source, encoding="utf-8")
    calls: list[str] = []
    fingerprint = "first"

    def fake_compiler(src: str, *, module_name: str, filename: str) -> SimpleNamespace:
        del filename
        calls.append(module_name)
        return SimpleNamespace(transformed_source=src.replace("VALUE = 1\n", "VALUE = 42\n"))

    monkeypatch.setattr(
        import_hook.kernel_loader, "active_transformer_fingerprint", lambda: fingerprint,
    )
    monkeypatch.setattr("sys.dont_write_bytecode", False)
    for attempt in range(2):
        if attempt == 1:
            if invalidation == "source":
                source = "#@pyrolyze\nVALUE = 12345\n"
                path.write_text(source, encoding="utf-8")
            elif invalidation == "transformer":
                fingerprint = "second"
            else:
                pyc = importlib.util.cache_from_source(str(path))
                with open(pyc, "r+b") as stream:
                    if invalidation == "magic":
                        stream.write(b"BAD!")
                    else:
                        stream.truncate(4)
        loader = import_hook._PyRolyzeLoader(
            fullname="invalidated_example", path=str(path), delegate=_DelegateLoader(source),
            compiler_fn=fake_compiler, cache=BytecodeCache(),
        )
        module = ModuleType("invalidated_example")
        module.__file__ = str(path)
        loader.exec_module(module)
        assert module.VALUE == (12345 if attempt == 1 and invalidation == "source" else 42)
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
