"""Smoke test: PyRolyze compilation + execution under pytest.

The public ``pyrolyze`` decorator in ``pyrolyze.api`` is a **stub** that always
raises (real transformation happens in the compiler). A test module that
defines ``@pyrolyze`` at **import time** would therefore fail collection unless an
import hook compiles before exec — that hook is **not** installed by default.

This file instead uses ``load_transformed_namespace`` (same pipeline as other
tests) to prove that **compiler-transformed** ``@pyrolyze`` code loads and runs
when pytest executes.
"""

from __future__ import annotations

import pytest

from pyrolyze.api import pyrolyze
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof

_MINIMAL_PYROLYZE_SOURCE = """
from pyrolyze.api import pyrolyze

@pyrolyze
def noop_component():
    return None
"""


def test_stub_pyrolyze_decorator_raises_when_applied_directly() -> None:
    """Document why raw ``@pyrolyze`` cannot live on module-level defs in plain .py tests."""

    def _fn() -> None:
        return None

    with pytest.raises(Exception, match="pyrolyze compiler failed"):
        pyrolyze(_fn)


def test_load_transformed_namespace_runs_minimal_pyrolyze_under_pytest() -> None:
    namespace = load_transformed_namespace(
        _MINIMAL_PYROLYZE_SOURCE,
        module_name="tests.unified._virtual_minimal_pyrolyze",
        filename="tests/unified/_virtual_minimal_pyrolyze.py",
        globals_dict={"pyrolyze": pyrolyze},
    )
    noop = namespace["noop_component"]
    meta = getattr(noop, "_pyrolyze_meta", None)
    assert meta is not None
    ctx = RenderContext()
    meta._func(ctx, dirtyof())
