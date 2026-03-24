#@pyrolyze
"""Smoke test: PyRolyze compilation + execution under pytest.

The public ``pyrolyze`` decorator in ``pyrolyze.api`` is a **stub** that raises
unless the module is loaded through the compiler. The ``pyrolyze`` pytest
plugin (``project.entry-points.pytest11``) installs a meta path hook so
modules marked with ``#@pyrolyze`` are transformed before import executes.

Tests that build **dynamic** source strings (generic backend harnesses, f-string
module names) should keep using ``load_transformed_namespace``.
"""

from __future__ import annotations

import pytest

from pyrolyze.api import pyrolyze
from pyrolyze.runtime import RenderContext, dirtyof


@pyrolyze
def noop_component() -> None:
    return None


def test_stub_pyrolyze_decorator_raises_when_applied_directly() -> None:
    def _fn() -> None:
        return None

    with pytest.raises(Exception, match="pyrolyze compiler failed"):
        pyrolyze(_fn)


def test_module_level_pyrolyze_component_runs_under_pytest() -> None:
    meta = getattr(noop_component, "_pyrolyze_meta", None)
    assert meta is not None
    ctx = RenderContext()
    meta._func(ctx, dirtyof())
