from __future__ import annotations

import pytest

from pyrolyze.api import UIElement
from pyrolyze.backends.model import TypeRef
from pyrolyze.testing.generic_backend import (
    MountInterfaceKind,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
    PyroNodeEngine,
    PyrolyzeMountCompatibilityError,
)


def _phase1_specs() -> tuple[NodeGenSpec, ...]:
    return (
        NodeGenSpec(
            name="Widget",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
        ),
        NodeGenSpec(
            name="Text",
            base_name="Widget",
            constructor=(
                ParamSpec(name="name", annotation=TypeRef("str")),
                ParamSpec(name="text", annotation=TypeRef("str")),
            ),
        ),
        NodeGenSpec(
            name="Menu",
            base_name="Widget",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
        ),
        NodeGenSpec(
            name="Row",
            base_name="Widget",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="child",
                    accepted_base="Widget",
                    interface=MountInterfaceKind.ORDERED,
                    default=True,
                ),
            ),
        ),
        NodeGenSpec(
            name="TextRow",
            base_name="Widget",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="child",
                    accepted_kind="Text",
                    interface=MountInterfaceKind.ORDERED,
                    default=True,
                ),
            ),
        ),
    )


def test_generic_backend_engine_mounts_base_compatible_children() -> None:
    engine = PyroNodeEngine(_phase1_specs(), initial_generation=5)

    mounted = engine.mount(
        UIElement(
            kind="Row",
            props={"name": "root"},
            children=(
                UIElement(kind="Text", props={"name": "text-1", "text": "hello"}),
                UIElement(kind="Menu", props={"name": "menu-1"}),
            ),
        ),
        slot_id=("root", 1),
        call_site_id=11,
    )

    snapshot = engine.snapshot(mounted)

    assert snapshot.node_type == "Row"
    assert snapshot.generation == 5
    assert tuple(entry.node.node_type for entry in snapshot.mounts["child"][0].entries) == ("Text", "Menu")
    assert all(entry.node.generation == 5 for entry in snapshot.mounts["child"][0].entries)


def test_generic_backend_engine_rejects_incompatible_child_types() -> None:
    engine = PyroNodeEngine(_phase1_specs(), initial_generation=3)

    with pytest.raises(PyrolyzeMountCompatibilityError, match="TextRow"):
        engine.mount(
            UIElement(
                kind="TextRow",
                props={"name": "root"},
                children=(UIElement(kind="Menu", props={"name": "menu-1"}),),
            ),
            slot_id=("root", 2),
            call_site_id=22,
        )


def test_generic_backend_generation_only_changes_for_mutated_nodes() -> None:
    engine = PyroNodeEngine(_phase1_specs(), initial_generation=5)
    mounted = engine.mount(
        UIElement(
            kind="Row",
            props={"name": "root"},
            children=(UIElement(kind="Text", props={"name": "text-1", "text": "hello"}),),
        ),
        slot_id=("root", 3),
        call_site_id=33,
    )

    unchanged = engine.update(
        mounted,
        UIElement(
            kind="Row",
            props={"name": "root"},
            children=(UIElement(kind="Text", props={"name": "text-1", "text": "hello"}),),
        ),
        generation=6,
    )
    unchanged_snapshot = engine.snapshot(unchanged)

    assert unchanged_snapshot.generation == 5
    assert unchanged_snapshot.mounts["child"][0].entries[0].node.generation == 5

    changed = engine.update(
        mounted,
        UIElement(
            kind="Row",
            props={"name": "root"},
            children=(UIElement(kind="Text", props={"name": "text-1", "text": "updated"}),),
        ),
        generation=7,
    )
    changed_snapshot = engine.snapshot(changed)

    assert changed_snapshot.generation == 7
    assert changed_snapshot.mounts["child"][0].entries[0].node.generation == 7
