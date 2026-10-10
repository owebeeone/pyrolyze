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
    completion = root._field_only_completion
    assert completion is not None
    assert completion.pass_state_selection_enabled
    assert completion.root is root


@pytest.mark.parametrize("legacy_setting", ("0", "1", "false", "true"))
def test_retired_boolean_cannot_select_a_fallback(monkeypatch, legacy_setting) -> None:
    monkeypatch.delenv("PYROLYZE_CONTEXT_IMPL", raising=False)
    monkeypatch.setenv("PYROLYZE_USE_CONTEXT_LCM", legacy_setting)
    module = _reload_runtime_context()
    from pyrolyze.runtime.context_lifecycle import RenderContext

    assert module.RenderContext is RenderContext


def test_explicit_lifecycle_selector_installs_completion_automatically(monkeypatch) -> None:
    monkeypatch.setenv("PYROLYZE_CONTEXT_IMPL", "lifecycle")
    module = _reload_runtime_context()
    assert module.__PYROLYZE_CONTEXT_IMPLEMENTATION__ == "lcm"
    root = module.RenderContext()
    completion = getattr(root, "_field_only_completion", None)
    assert completion is not None
    assert completion.pass_state_selection_enabled
    assert completion.root is root




def test_default_root_preserves_exact_type_activation_guard() -> None:
    from pyrolyze.runtime.context_lifecycle import RenderContext

    class UnrecognizedRoot(RenderContext):
        pass

    with pytest.raises(RuntimeError, match="exact scheduler root"):
        UnrecognizedRoot()


@pytest.mark.parametrize("legacy_setting", ("original", "bare", "bare_refactor", "bare_refactor_lcm", "lcm"))
def test_retired_selector_cannot_select_a_fallback(monkeypatch, legacy_setting) -> None:
    monkeypatch.setenv("PYROLYZE_CONTEXT_IMPL", legacy_setting)
    module = _reload_runtime_context()
    from pyrolyze.runtime.context_lifecycle import RenderContext

    assert module.RenderContext is RenderContext
