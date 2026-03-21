"""Manual learnings for the tkinter backend extraction pipeline."""

from __future__ import annotations

from frozendict import frozendict

from pyrolyze.backends.model import UiWidgetLearning

LEARNINGS: frozendict[str, UiWidgetLearning] = frozendict()
