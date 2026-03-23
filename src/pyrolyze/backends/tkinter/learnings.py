"""Manual learnings for the tkinter backend extraction pipeline."""

from __future__ import annotations

from frozendict import frozendict

from pyrolyze.backends.model import (
    EventPayloadPolicy,
    MountReplayKind,
    UiEventLearning,
    UiMountPointLearning,
    UiPropLearning,
    UiWidgetLearning,
)


def _hidden_props(*names: str) -> frozendict[str, UiPropLearning]:
    return frozendict({name: UiPropLearning(public=False) for name in names})


LEARNINGS: frozendict[str, UiWidgetLearning] = frozendict(
    {
        "tkinter:Button": UiWidgetLearning(
            prop_learnings=_hidden_props("master", "cnf", "command"),
            event_learnings=frozendict(
                {
                    "on_command": UiEventLearning(
                        signal_name="command",
                        payload_policy=EventPayloadPolicy.NONE,
                    )
                }
            ),
        ),
        "tkinter.ttk:Button": UiWidgetLearning(
            prop_learnings=_hidden_props("master", "command"),
            event_learnings=frozendict(
                {
                    "on_command": UiEventLearning(
                        signal_name="command",
                        payload_policy=EventPayloadPolicy.NONE,
                    )
                }
            ),
        ),
        "tkinter:Entry": UiWidgetLearning(
            prop_learnings=_hidden_props("master", "cnf"),
            event_learnings=frozendict(
                {
                    "on_key_release": UiEventLearning(
                        signal_name="bind:<KeyRelease>",
                        payload_policy=EventPayloadPolicy.FIRST_ARG,
                    )
                }
            ),
        ),
        "tkinter.ttk:Entry": UiWidgetLearning(
            prop_learnings=_hidden_props("master", "widget"),
            event_learnings=frozendict(
                {
                    "on_key_release": UiEventLearning(
                        signal_name="bind:<KeyRelease>",
                        payload_policy=EventPayloadPolicy.FIRST_ARG,
                    )
                }
            ),
        ),
        "tkinter:Frame": UiWidgetLearning(
            prop_learnings=_hidden_props("master", "cnf"),
            mount_point_learnings=frozendict(
                {
                    "pack": UiMountPointLearning(
                        default_child=True,
                        default_attach_rank=0,
                        append_method_name="pack",
                        replay_kind=MountReplayKind.NONE,
                        prefer_sync=True,
                    )
                }
            ),
        ),
        "tkinter.ttk:Frame": UiWidgetLearning(
            prop_learnings=_hidden_props("master"),
            mount_point_learnings=frozendict(
                {
                    "pack": UiMountPointLearning(
                        default_child=True,
                        default_attach_rank=0,
                        append_method_name="pack",
                        replay_kind=MountReplayKind.NONE,
                        prefer_sync=True,
                    )
                }
            ),
        ),
        "tkinter:Menu": UiWidgetLearning(
            prop_learnings=_hidden_props("master", "cnf"),
        ),
        "tkinter:PanedWindow": UiWidgetLearning(
            prop_learnings=_hidden_props("master", "cnf"),
            mount_point_learnings=frozendict(
                {
                    "pane": UiMountPointLearning(
                        default_child=True,
                        default_attach_rank=0,
                        append_method_name="add",
                        replay_kind=MountReplayKind.INDEX,
                    )
                }
            ),
        ),
        "tkinter.ttk:Notebook": UiWidgetLearning(
            prop_learnings=_hidden_props("master"),
        ),
        "tkinter.ttk:Panedwindow": UiWidgetLearning(
            prop_learnings=_hidden_props("master"),
        ),
    }
)
