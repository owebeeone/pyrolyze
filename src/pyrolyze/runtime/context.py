"""Switchable runtime context surface."""

from __future__ import annotations

import importlib
import os


def _selected_context_impl() -> str:
    explicit = os.environ.get("PYROLYZE_CONTEXT_IMPL")
    if explicit is not None:
        value = explicit.strip().lower()
        if value in {"lcm", "original", "bare", "bare_refactor", "bare_refactor_lcm"}:
            return value
        raise RuntimeError(f"unsupported PYROLYZE_CONTEXT_IMPL={explicit!r}")

    raw = os.environ.get("PYROLYZE_USE_CONTEXT_LCM")
    if raw is None:
        return "lcm"
    return "lcm" if raw.strip().lower() not in {"", "0", "false", "no", "off"} else "original"


_IMPL_MODULES = {
    "lcm": ".context_lcm",
    "original": ".context_original",
    "bare": ".context_bare",
    "bare_refactor": ".context_bare_refactor",
    "bare_refactor_lcm": ".context_bare_refactor_lcm",
}

_impl = importlib.import_module(_IMPL_MODULES[_selected_context_impl()], __package__)

for _name, _value in vars(_impl).items():
    if _name.startswith("_") and _name != "__all__":
        continue
    globals()[_name] = _value

try:
    from .context_state._support import REFRACTOR_RUNTIME as _REFRACTOR_RUNTIME
    from ..visitor import walk_context_graph as _walk_context_graph
except ImportError:
    pass
else:
    _REFRACTOR_RUNTIME.walk_context_graph = _walk_context_graph


__PYROLYZE_CONTEXT_IMPLEMENTATION__ = _impl.__PYROLYZE_CONTEXT_IMPLEMENTATION__
