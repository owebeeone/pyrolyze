"""Import-hook integration for PyRolyze source transformation."""

from __future__ import annotations

import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import os
import sys
from pathlib import Path
from typing import Any, Callable

from .compiler import compile_source_with_env, kernel_loader
from .importer import BytecodeCache, PersistentArtifactCache, compute_source_fingerprint, should_transform


_ENABLE_IMPORT_HOOK_ENV = "PYROLYZE_ENABLE_IMPORT_HOOK"
_ENABLE_CACHE_ENV = "PYROLYZE_ENABLE_CACHE"
_CACHE_DIR_ENV = "PYROLYZE_CACHE_DIR"
_INSTALLED_FINDER: "PyRolyzeFinder | None" = None


def _raw_source_has_pyrolyze_marker(source: str) -> bool:
    """Match the first-two-lines ``#@pyrolyze`` eligibility rule."""

    marker_window = source.splitlines()[:2]
    return any(line.strip() == "#@pyrolyze" for line in marker_window)


class _PyRolyzeLoader(importlib.abc.SourceLoader):
    def __init__(
        self,
        *,
        fullname: str,
        path: str,
        delegate: importlib.abc.Loader,
        compiler_fn: Callable[..., Any],
        cache: BytecodeCache | PersistentArtifactCache,
    ) -> None:
        self._fullname = fullname
        self._path = path
        self._delegate = delegate
        self._compiler_fn = compiler_fn
        self._cache = cache
        self._prepared_source: str | None = None
        self._prepared_path: str | None = None
        self._prepared_artifact: Any | None = None

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> Any:
        if hasattr(self._delegate, "create_module"):
            return self._delegate.create_module(spec)  # type: ignore[call-arg]
        return None

    def get_filename(self, fullname: str) -> str:
        del fullname
        return self._path

    def get_data(self, path: str) -> bytes:
        return Path(path).read_bytes()

    def path_stats(self, path: str) -> dict[str, Any]:
        stat = os.stat(path)
        return {
            "mtime": stat.st_mtime,
            "size": stat.st_size,
        }

    def set_data(self, path: str, data: bytes) -> None:
        try:
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        except OSError:
            return

    def source_to_code(self, data: bytes, path: str, *, _optimize: int = -1) -> Any:
        del _optimize
        source = importlib.util.decode_source(data)
        artifact = self._consume_prepared_artifact(source=source, file_path=path)
        if artifact is None:
            artifact = self._resolve_artifact(source, file_path=path)
        transformed_source = getattr(artifact, "transformed_source", None)
        source_to_compile = transformed_source if isinstance(transformed_source, str) else source
        return compile(source_to_compile, path, "exec")

    def exec_module(self, module: Any) -> None:
        source = self.get_source(module.__name__)
        file_path = getattr(module, "__file__", None) or self._path
        if source is not None and should_transform(
            module_name=self._fullname,
            file_path=str(file_path),
            source_text=source,
        ):
            artifact = self._resolve_artifact(source, file_path=str(file_path))
            self._prepared_source = source
            self._prepared_path = str(file_path)
            self._prepared_artifact = artifact
            setattr(
                module,
                "__pyrolyze_artifact__",
                artifact,
            )
        super().exec_module(module)

    def _resolve_artifact(self, source: str, *, file_path: str) -> Any:
        mtime = _safe_mtime(self._path)
        python_magic = importlib.util.MAGIC_NUMBER.hex()
        transformer_fingerprint = kernel_loader.active_transformer_fingerprint()
        cache_key = compute_source_fingerprint(
            source,
            mtime=mtime,
            python_magic=python_magic,
            transformer_fingerprint=transformer_fingerprint,
        )
        artifact = self._cache.get(module_name=self._fullname, cache_key=cache_key)
        if artifact is None:
            artifact = _invoke_compiler(
                self._compiler_fn,
                source,
                module_name=self._fullname,
                filename=str(file_path),
            )
            self._cache.put(module_name=self._fullname, cache_key=cache_key, payload=artifact)
        return artifact

    def _consume_prepared_artifact(self, *, source: str, file_path: str) -> Any | None:
        if self._prepared_source == source and self._prepared_path == file_path:
            artifact = self._prepared_artifact
            self._prepared_source = None
            self._prepared_path = None
            self._prepared_artifact = None
            return artifact
        return None


class PyRolyzeFinder(importlib.abc.MetaPathFinder):
    """Meta-path finder that wraps eligible source modules with PyRolyze compilation."""

    def __init__(
        self,
        *,
        compiler_fn: Callable[..., Any] = compile_source_with_env,
        cache: BytecodeCache | PersistentArtifactCache | None = None,
    ) -> None:
        self._compiler_fn = compiler_fn
        self._cache = cache or BytecodeCache()

    def find_spec(
        self,
        fullname: str,
        path: list[str] | None = None,
        target: Any = None,
    ) -> importlib.machinery.ModuleSpec | None:
        del target
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is None or spec.loader is None:
            return None

        if not spec.origin or not spec.origin.endswith(".py"):
            return None

        source = _get_source_from_loader(spec.loader, fullname)
        if source is None:
            return None

        if not should_transform(
            module_name=fullname,
            file_path=spec.origin,
            source_text=source,
        ):
            return None

        spec.loader = _PyRolyzeLoader(
            fullname=fullname,
            path=spec.origin,
            delegate=spec.loader,
            compiler_fn=self._compiler_fn,
            cache=self._cache,
        )
        return spec


def _install_finder(
    *,
    compiler_fn: Callable[..., Any] = compile_source_with_env,
    cache: BytecodeCache | PersistentArtifactCache | None = None,
) -> PyRolyzeFinder:
    global _INSTALLED_FINDER

    if _INSTALLED_FINDER is None:
        effective_cache = cache
        if effective_cache is None and _is_truthy(os.getenv(_ENABLE_CACHE_ENV, "")):
            cache_dir = os.getenv(_CACHE_DIR_ENV, ".pyrolyze_cache")
            effective_cache = PersistentArtifactCache(cache_dir=cache_dir)

        _INSTALLED_FINDER = PyRolyzeFinder(
            compiler_fn=compiler_fn,
            cache=effective_cache,
        )

    while _INSTALLED_FINDER in sys.meta_path:
        sys.meta_path.remove(_INSTALLED_FINDER)
    sys.meta_path.insert(0, _INSTALLED_FINDER)
    return _INSTALLED_FINDER



def install_import_hook(
    *,
    compiler_fn: Callable[..., Any] = compile_source_with_env,
    cache: BytecodeCache | PersistentArtifactCache | None = None,
) -> PyRolyzeFinder | None:
    """Install a singleton PyRolyze finder when the feature flag is enabled."""
    global _INSTALLED_FINDER

    if _INSTALLED_FINDER is not None:
        if _INSTALLED_FINDER not in sys.meta_path:
            sys.meta_path.insert(0, _INSTALLED_FINDER)
        return _INSTALLED_FINDER

    enabled_value = os.getenv(_ENABLE_IMPORT_HOOK_ENV, "")
    if not _is_truthy(enabled_value):
        return None

    return _install_finder(
        compiler_fn=compiler_fn,
        cache=cache,
    )



def uninstall_import_hook() -> bool:
    """Remove installed PyRolyze finder(s) from sys.meta_path."""
    global _INSTALLED_FINDER

    removed = False
    for finder in list(sys.meta_path):
        if isinstance(finder, PyRolyzeFinder):
            sys.meta_path.remove(finder)
            removed = True

    _INSTALLED_FINDER = None
    return removed



def _is_truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}



def _safe_mtime(path: str) -> float:
    try:
        return os.path.getmtime(path)
    except OSError:
        return 0.0



def _get_source_from_loader(loader: importlib.abc.Loader, fullname: str) -> str | None:
    if hasattr(loader, "get_source"):
        return loader.get_source(fullname)  # type: ignore[call-arg]
    return None



def _get_code_from_loader(loader: importlib.abc.Loader, fullname: str) -> Any:
    if hasattr(loader, "get_code"):
        code = loader.get_code(fullname)  # type: ignore[call-arg]
        if code is not None:
            return code
    raise ImportError(f"Unable to load module code for '{fullname}' via delegated loader.")


def _invoke_compiler(
    compiler_fn: Callable[..., Any],
    source: str,
    *,
    module_name: str,
    filename: str,
) -> Any:
    signature = inspect.signature(compiler_fn)
    if "filename" in signature.parameters:
        return compiler_fn(source, module_name=module_name, filename=filename)
    return compiler_fn(source, module_name=module_name)


def install_startup_import_hook() -> None:
    """Install the source-transform import hook used by ``#@pyrolyze`` modules.

    This is the canonical startup/bootstrap path for venv ``.pth`` loading and
    should remain idempotent.
    """

    _install_finder()


def uninstall_startup_import_hook() -> None:
    """Remove the source-transform startup hook used by ``#@pyrolyze`` modules."""

    uninstall_import_hook()


PyrolyzeLoader = _PyRolyzeLoader
PyrolyzeMetaPathFinder = PyRolyzeFinder


__all__ = [
    "PyrolyzeLoader",
    "PyrolyzeMetaPathFinder",
    "PyRolyzeFinder",
    "_raw_source_has_pyrolyze_marker",
    "install_import_hook",
    "install_startup_import_hook",
    "uninstall_import_hook",
    "uninstall_startup_import_hook",
]
