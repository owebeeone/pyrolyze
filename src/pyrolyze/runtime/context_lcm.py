"""Lifecycle-metaprogrammed context runtime scaffold."""

from __future__ import annotations

from . import context_original as _base

for _name, _value in vars(_base).items():
    if _name.startswith("_") and _name != "__all__":
        continue
    globals()[_name] = _value

__PYROLYZE_CONTEXT_IMPLEMENTATION__ = "lcm"
