"""Manual learnings for the PySide6 backend extraction pipeline."""

from __future__ import annotations

from frozendict import frozendict

from pyrolyze.backends.model import FillPolicy, MethodMode, UiMethodLearning, UiWidgetLearning

LEARNINGS: frozendict[str, UiWidgetLearning] = frozendict(
    {
        "QSpinBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setRange": UiMethodLearning(
                        source_props=("minimum", "maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                }
            )
        ),
        "QDoubleSpinBox": UiWidgetLearning(
            method_learnings=frozendict(
                {
                    "setRange": UiMethodLearning(
                        source_props=("minimum", "maximum"),
                        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                        mode=MethodMode.CREATE_UPDATE,
                        constructor_equivalent=True,
                    ),
                }
            )
        ),
    }
)
