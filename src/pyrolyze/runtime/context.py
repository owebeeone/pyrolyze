"""Public lifecycle-backed runtime context surface."""

from __future__ import annotations

from . import context_lifecycle as _impl

for _name, _value in vars(_impl).items():
    if _name.startswith("_") and _name != "__all__":
        continue
    globals()[_name] = _value

__PYROLYZE_CONTEXT_IMPLEMENTATION__ = _impl.__PYROLYZE_CONTEXT_IMPLEMENTATION__

# Compatibility alias until a dedicated plain-call runtime context type lands.
PlainCallRuntimeContext = SlotRuntimeContext
