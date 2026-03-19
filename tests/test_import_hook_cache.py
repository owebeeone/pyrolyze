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
