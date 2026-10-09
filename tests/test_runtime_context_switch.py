from __future__ import annotations

import importlib
import sys

import pytest


def _reload_runtime_context():
    sys.modules.pop("pyrolyze.runtime.context", None)
    return importlib.import_module("pyrolyze.runtime.context")


def test_runtime_context_defaults_to_lifecycle_completion(monkeypatch) -> None:
    monkeypatch.delenv("PYROLYZE_CONTEXT_IMPL", raising=False)
    monkeypatch.delenv("PYROLYZE_USE_CONTEXT_LCM", raising=False)

    module = _reload_runtime_context()

    assert module.__PYROLYZE_CONTEXT_IMPLEMENTATION__ == "lcm"
    from pyrolyze.runtime.context_lifecycle import RenderContext

    assert module.RenderContext is RenderContext
    root = module.RenderContext()
    completion = root._state_mgr._field_only_completion
    assert completion is not None
    assert completion.pass_state_selection_enabled
    assert completion.root is root._state_mgr


def test_enabled_legacy_boolean_selects_lifecycle_completion(monkeypatch) -> None:
    monkeypatch.delenv("PYROLYZE_CONTEXT_IMPL", raising=False)
    monkeypatch.setenv("PYROLYZE_USE_CONTEXT_LCM", "1")
    module = _reload_runtime_context()
    from pyrolyze.runtime.context_lifecycle import RenderContext

    assert module.RenderContext is RenderContext


def test_explicit_lifecycle_selector_installs_completion_automatically(monkeypatch) -> None:
    monkeypatch.setenv("PYROLYZE_CONTEXT_IMPL", "lifecycle")
    module = _reload_runtime_context()
    assert module.__PYROLYZE_CONTEXT_IMPLEMENTATION__ == "lcm"
    root = module.RenderContext()
    completion = getattr(root._state_mgr, "_field_only_completion", None)
    assert completion is not None
    assert completion.pass_state_selection_enabled
    assert completion.root is root._state_mgr


def test_default_construction_does_not_activate_private_checkpoints(monkeypatch) -> None:
    from pyrolyze.runtime import context_lifecycle

    def reject_private_activation(root: object) -> None:
        raise AssertionError("default roots must directly install final completion")

    monkeypatch.setattr(
        context_lifecycle, "_enable_pass_state_render", reject_private_activation, raising=False
    )
    root = context_lifecycle.RenderContext()
    assert root._state_mgr._field_only_completion is not None


def test_default_root_preserves_exact_type_activation_guard() -> None:
    from pyrolyze.runtime.context_lifecycle import RenderContext

    class UnrecognizedRoot(RenderContext):
        pass

    with pytest.raises(RuntimeError, match="exact scheduler root"):
        UnrecognizedRoot()


def test_runtime_context_can_switch_back_to_original(monkeypatch) -> None:
    monkeypatch.delenv("PYROLYZE_CONTEXT_IMPL", raising=False)
    monkeypatch.setenv("PYROLYZE_USE_CONTEXT_LCM", "0")

    module = _reload_runtime_context()

    assert module.__PYROLYZE_CONTEXT_IMPLEMENTATION__ == "original"
    assert hasattr(module, "RenderContext")
