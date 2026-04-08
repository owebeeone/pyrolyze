"""Switchable runtime context surface."""

from __future__ import annotations

import importlib
import os


def _use_lcm_context() -> bool:
    raw = os.environ.get("PYROLYZE_USE_CONTEXT_LCM", "")
    return raw.strip().lower() not in {"", "0", "false", "no", "off"}


if _use_lcm_context():
    _impl = importlib.import_module(".context_lcm", __package__)
else:
    _impl = importlib.import_module(".context_original", __package__)

for _name, _value in vars(_impl).items():
    if _name.startswith("_") and _name != "__all__":
        continue
    globals()[_name] = _value


__PYROLYZE_CONTEXT_IMPLEMENTATION__ = _impl.__PYROLYZE_CONTEXT_IMPLEMENTATION__
