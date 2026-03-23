"""Apply DearPyGui learnings to canonical dump records (author-facing props/events)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from pyrolyze.backends.dearpygui.discovery import DpgCanonicalMountable
from pyrolyze.backends.dearpygui.learnings import (
    KINDS_DEFAULT_VALUE_AS_VALUE,
    LEARNINGS,
    RUNTIME_OWNED_PARAM_NAMES,
    dearpygui_learning_key,
)
from pyrolyze.backends.model import EventPayloadPolicy, UiWidgetLearning


@dataclass(frozen=True, slots=True)
class DpgAuthorPropSpec:
    public_name: str
    constructor_name: str
    annotation: str | None
    default_repr: str | None


@dataclass(frozen=True, slots=True)
class DpgAuthorEventSpec:
    public_name: str
    signal_name: str
    payload_policy: EventPayloadPolicy
    annotation: str | None
    default_repr: str | None


@dataclass(frozen=True, slots=True)
class DpgShapedMountable:
    factory_name: str
    kind_name: str
    public_kind_name: str
    props: tuple[DpgAuthorPropSpec, ...]
    events: tuple[DpgAuthorEventSpec, ...]
    mount_point_names: tuple[str, ...]


def widget_learning_for_kind(
    kind_name: str,
    learnings: Mapping[str, UiWidgetLearning] | None = None,
) -> UiWidgetLearning:
    table = LEARNINGS if learnings is None else learnings
    return table.get(dearpygui_learning_key(kind_name), UiWidgetLearning())


def _event_public_name(learning: UiWidgetLearning, toolkit_param: str) -> str:
    for public_name, ev in learning.event_learnings.items():
        if ev.signal_name == toolkit_param:
            return public_name
    return toolkit_param


def shape_canonical_mountable(
    item: DpgCanonicalMountable,
    learnings: Mapping[str, UiWidgetLearning] | None = None,
) -> DpgShapedMountable:
    learning = widget_learning_for_kind(item.kind_name, learnings)
    public_kind = learning.public_name or item.kind_name

    props: list[DpgAuthorPropSpec] = []
    events: list[DpgAuthorEventSpec] = []
    event_params = frozenset(item.record.event_params)

    for param in item.record.parameters:
        name = param.name
        if param.kind == "VAR_KEYWORD":
            continue
        if name in RUNTIME_OWNED_PARAM_NAMES:
            continue
        prop_learning = learning.prop_learnings.get(name)
        if prop_learning is not None and prop_learning.public is False:
            continue

        if name in event_params:
            public_ev = _event_public_name(learning, name)
            ev_learning = learning.event_learnings.get(public_ev)
            payload = (
                ev_learning.payload_policy
                if ev_learning is not None
                else EventPayloadPolicy.NONE
            )
            signal = ev_learning.signal_name if ev_learning is not None else name
            events.append(
                DpgAuthorEventSpec(
                    public_name=public_ev,
                    signal_name=signal,
                    payload_policy=payload,
                    annotation=param.annotation,
                    default_repr=param.default_repr,
                )
            )
            continue

        if name == "default_value" and item.kind_name in KINDS_DEFAULT_VALUE_AS_VALUE:
            props.append(
                DpgAuthorPropSpec(
                    public_name="value",
                    constructor_name="default_value",
                    annotation=param.annotation,
                    default_repr=param.default_repr,
                )
            )
            continue

        props.append(
            DpgAuthorPropSpec(
                public_name=name,
                constructor_name=name,
                annotation=param.annotation,
                default_repr=param.default_repr,
            )
        )

    mount_names = tuple(
        sorted(
            learning.mount_point_learnings.keys(),
            key=lambda n: (
                learning.mount_point_learnings[n].default_attach_rank is None,
                learning.mount_point_learnings[n].default_attach_rank or 0,
                n,
            ),
        )
    )

    return DpgShapedMountable(
        factory_name=item.factory_name,
        kind_name=item.kind_name,
        public_kind_name=public_kind,
        props=tuple(props),
        events=tuple(events),
        mount_point_names=mount_names,
    )


__all__ = [
    "DpgAuthorEventSpec",
    "DpgAuthorPropSpec",
    "DpgShapedMountable",
    "shape_canonical_mountable",
    "widget_learning_for_kind",
]
