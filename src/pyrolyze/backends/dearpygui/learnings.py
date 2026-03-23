"""DearPyGui generator learnings: author-facing names, suppressed params, mounts."""

from __future__ import annotations

from frozendict import frozendict

from pyrolyze.backends.model import (
    EventPayloadPolicy,
    MountReplayKind,
    TypeRef,
    UiEventLearning,
    UiMountPointLearning,
    UiWidgetLearning,
)


def dearpygui_learning_key(kind_name: str) -> str:
    return f"dearpygui:{kind_name}"


RUNTIME_OWNED_PARAM_NAMES: frozenset[str] = frozenset(
    {
        "tag",
        "parent",
        "before",
        "source",
        "user_data",
        "kwargs",
        "use_internal_label",
    }
)

KINDS_DEFAULT_VALUE_AS_VALUE: frozenset[str] = frozenset(
    {
        "InputText",
        "InputFloat",
        "InputInt",
        "InputDouble",
        "Checkbox",
        "SliderFloat",
        "SliderInt",
        "Listbox",
        "Combo",
        "RadioButton",
        "ProgressBar",
    }
)


LEARNINGS: frozendict[str, UiWidgetLearning] = frozendict(
    {
        dearpygui_learning_key("Button"): UiWidgetLearning(
            event_learnings=frozendict(
                {
                    "on_press": UiEventLearning(
                        signal_name="callback",
                        payload_policy=EventPayloadPolicy.NONE,
                    ),
                    "on_drag": UiEventLearning(
                        signal_name="drag_callback",
                        payload_policy=EventPayloadPolicy.ALL_ARGS,
                    ),
                    "on_drop": UiEventLearning(
                        signal_name="drop_callback",
                        payload_policy=EventPayloadPolicy.ALL_ARGS,
                    ),
                }
            ),
        ),
        dearpygui_learning_key("Checkbox"): UiWidgetLearning(
            event_learnings=frozendict(
                {
                    "on_change": UiEventLearning(
                        signal_name="callback",
                        payload_policy=EventPayloadPolicy.NONE,
                    ),
                    "on_drag": UiEventLearning(
                        signal_name="drag_callback",
                        payload_policy=EventPayloadPolicy.ALL_ARGS,
                    ),
                    "on_drop": UiEventLearning(
                        signal_name="drop_callback",
                        payload_policy=EventPayloadPolicy.ALL_ARGS,
                    ),
                }
            ),
        ),
        dearpygui_learning_key("InputText"): UiWidgetLearning(
            event_learnings=frozendict(
                {
                    "on_change": UiEventLearning(
                        signal_name="callback",
                        payload_policy=EventPayloadPolicy.NONE,
                    ),
                    "on_drag": UiEventLearning(
                        signal_name="drag_callback",
                        payload_policy=EventPayloadPolicy.ALL_ARGS,
                    ),
                    "on_drop": UiEventLearning(
                        signal_name="drop_callback",
                        payload_policy=EventPayloadPolicy.ALL_ARGS,
                    ),
                }
            ),
        ),
        dearpygui_learning_key("Window"): UiWidgetLearning(
            event_learnings=frozendict(
                {
                    "on_close": UiEventLearning(
                        signal_name="on_close",
                        payload_policy=EventPayloadPolicy.NONE,
                    ),
                }
            ),
            mount_point_learnings=frozendict(
                {
                    "menu_bar": UiMountPointLearning(
                        public_name="menu_bar",
                        default_child=False,
                        default_attach_rank=0,
                        accepted_produced_type=TypeRef(expr='"DpgMenuBarItem"'),
                        replay_kind=MountReplayKind.NONE,
                        prefer_sync=True,
                    ),
                    "standard": UiMountPointLearning(
                        public_name="standard",
                        default_child=True,
                        default_attach_rank=1,
                        accepted_produced_type=TypeRef(expr='"DpgContainerItem"'),
                        replay_kind=MountReplayKind.ANCHOR_BEFORE,
                        prefer_sync=True,
                    ),
                }
            ),
        ),
        dearpygui_learning_key("Table"): UiWidgetLearning(
            mount_point_learnings=frozendict(
                {
                    "column": UiMountPointLearning(
                        public_name="column",
                        default_child=False,
                        default_attach_rank=0,
                        accepted_produced_type=TypeRef(expr='"DpgTableColumnItem"'),
                        replay_kind=MountReplayKind.ANCHOR_BEFORE,
                    ),
                    "row": UiMountPointLearning(
                        public_name="row",
                        default_child=True,
                        default_attach_rank=1,
                        accepted_produced_type=TypeRef(expr='"DpgTableRowItem"'),
                        replay_kind=MountReplayKind.ANCHOR_BEFORE,
                    ),
                }
            ),
        ),
        dearpygui_learning_key("Plot"): UiWidgetLearning(
            mount_point_learnings=frozendict(
                {
                    "axis": UiMountPointLearning(
                        public_name="axis",
                        default_child=True,
                        default_attach_rank=0,
                        accepted_produced_type=TypeRef(expr='"DpgPlotAxisItem"'),
                        replay_kind=MountReplayKind.ANCHOR_BEFORE,
                    ),
                }
            ),
        ),
        dearpygui_learning_key("NodeEditor"): UiWidgetLearning(
            mount_point_learnings=frozendict(
                {
                    "node": UiMountPointLearning(
                        public_name="node",
                        default_child=True,
                        default_attach_rank=0,
                        accepted_produced_type=TypeRef(expr='"DpgNodeItem"'),
                        replay_kind=MountReplayKind.ANCHOR_BEFORE,
                    ),
                    "link": UiMountPointLearning(
                        public_name="link",
                        default_child=False,
                        default_attach_rank=1,
                        accepted_produced_type=TypeRef(expr='"DpgNodeLinkItem"'),
                        replay_kind=MountReplayKind.ANCHOR_BEFORE,
                    ),
                }
            ),
        ),
    }
)


__all__ = [
    "KINDS_DEFAULT_VALUE_AS_VALUE",
    "LEARNINGS",
    "RUNTIME_OWNED_PARAM_NAMES",
    "dearpygui_learning_key",
]
