"""Manual learnings for the tkinter backend extraction pipeline."""

from __future__ import annotations

from frozendict import frozendict

from pyrolyze.backends.model import MountReplayKind, UiMountPointLearning, UiWidgetLearning

LEARNINGS: frozendict[str, UiWidgetLearning] = frozendict(
    {
        "tkinter:PanedWindow": UiWidgetLearning(
            mount_point_learnings=frozendict(
                {
                    "pane": UiMountPointLearning(
                        default_child=True,
                        default_attach_rank=0,
                        append_method_name="add",
                        replay_kind=MountReplayKind.INDEX,
                    )
                }
            )
        )
    }
)
