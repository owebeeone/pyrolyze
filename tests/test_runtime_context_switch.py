from __future__ import annotations

import importlib
import sys


def _reload_runtime_context():
    sys.modules.pop("pyrolyze.runtime.context", None)
    return importlib.import_module("pyrolyze.runtime.context")


def test_runtime_context_defaults_to_lcm(monkeypatch) -> None:
    monkeypatch.delenv("PYROLYZE_USE_CONTEXT_LCM", raising=False)

    module = _reload_runtime_context()

    assert module.__PYROLYZE_CONTEXT_IMPLEMENTATION__ == "lcm"
    assert hasattr(module, "RenderContext")


def test_runtime_context_can_switch_back_to_original(monkeypatch) -> None:
    monkeypatch.setenv("PYROLYZE_USE_CONTEXT_LCM", "0")

    module = _reload_runtime_context()

    assert module.__PYROLYZE_CONTEXT_IMPLEMENTATION__ == "original"
    assert hasattr(module, "RenderContext")
