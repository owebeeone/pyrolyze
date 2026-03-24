"""Meta path hook: compile ``#@pyrolyze``-marked modules before import executes.

Eligibility matches :func:`pyrolyze.compiler.kernels.v3_14.eligibility.should_transform_module`
(first two source lines may contain a ``#@pyrolyze`` marker).

Register via :func:`install` (pytest plugin does this automatically) or
``pyrolyze-import-hook-pth install`` (see ``pyrolyze.pyrolyze_tools.import_hook_pth``).
"""

from __future__ import annotations

import importlib.abc
import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from typing import Any, Sequence

from .facade import analyze_source, lower_plan_to_ast
from .kernel_loader import load_ast_kernel

_finder: PyrolyzeMetaPathFinder | None = None


def _raw_source_has_pyrolyze_marker(source: str) -> bool:
    """Match :func:`pyrolyze.compiler.kernels.v3_14.eligibility.is_pyrolyze_module` (first two lines)."""

    marker_window = source.splitlines()[:2]
    return any(line.strip() == "#@pyrolyze" for line in marker_window)


class PyrolyzeLoader(importlib.abc.Loader):
    def __init__(self, *, fullname: str, path: str, source: str) -> None:
        self._fullname = fullname
        self._path = path
        self._source = source

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> Any:
        return None

    def exec_module(self, module: Any) -> None:
        plan = analyze_source(
            self._source,
            module_name=module.__name__,
            filename=self._path,
        )
        module_ast = lower_plan_to_ast(plan, filename=self._path)
        namespace = module.__dict__
        namespace.setdefault("__name__", module.__name__)
        namespace.setdefault("__file__", self._path)
        pkg = module.__name__.rpartition(".")[0]
        namespace.setdefault("__package__", pkg or None)
        load_ast_kernel().exec_module_ast(
            module_ast,
            filename=self._path,
            namespace=namespace,
        )


class PyrolyzeMetaPathFinder(importlib.abc.MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None,
        target: Any | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
        if spec is None or spec.origin in (None, "built-in") or not spec.has_location:
            return spec
        origin = spec.origin
        if not origin.endswith(".py"):
            return spec
        try:
            raw = Path(origin).read_text(encoding="utf-8")
        except OSError:
            return spec
        if not _raw_source_has_pyrolyze_marker(raw):
            return spec
        loader = PyrolyzeLoader(fullname=fullname, path=origin, source=raw)
        return importlib.util.spec_from_loader(
            fullname,
            loader,
            origin=origin,
            is_package=spec.submodule_search_locations is not None,
        )


def install() -> None:
    """Place the PyRolyze finder at ``sys.meta_path[0]`` (idempotent).

    Must run **before** other file hooks (notably pytest's assertion rewriter)
    so ``#@pyrolyze`` modules are compiled before import executes. If another
    hook inserts itself at the front later (e.g. ``AssertionRewritingHook``),
    call :func:`install` again from ``pytest_configure`` to re-order.
    """

    global _finder
    if _finder is None:
        _finder = PyrolyzeMetaPathFinder()
    while _finder in sys.meta_path:
        sys.meta_path.remove(_finder)
    sys.meta_path.insert(0, _finder)


def uninstall() -> None:
    """Remove the finder installed by :func:`install` (mainly for tests)."""
    global _finder
    if _finder is not None and _finder in sys.meta_path:
        sys.meta_path.remove(_finder)
    _finder = None


__all__ = ["PyrolyzeLoader", "PyrolyzeMetaPathFinder", "install", "uninstall"]
