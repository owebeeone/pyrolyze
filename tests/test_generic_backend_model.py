from __future__ import annotations

from frozendict import frozendict

from pyrolyze.testing.generic_backend import (
    PyroArgs,
    PyroMountBucket,
    PyroMountEntry,
    PyroNode,
)


def test_pyro_node_builder_round_trips_immutable_snapshot() -> None:
    leaf = PyroNode(
        node_type="Text",
        generation=4,
        kwargs=frozendict({"name": "leaf", "text": "hello"}),
    )
    node = PyroNode(
        node_type="Row",
        generation=4,
        kwargs=frozendict({"name": "root"}),
        mounts=frozendict(
            {
                "child": (
                    PyroMountBucket(
                        key=PyroArgs(),
                        values=PyroArgs(),
                        entries=(PyroMountEntry(placement_id=0, node=leaf),),
                    ),
                ),
            }
        ),
    )

    rebuilt = node.to_builder().build()

    assert rebuilt == node


def test_pyro_node_builder_mutation_does_not_change_original_snapshot() -> None:
    original = PyroNode(
        node_type="Widget",
        generation=2,
        kwargs=frozendict({"name": "root"}),
    )

    builder = original.to_builder()
    builder.generation = 7
    builder.kwargs["name"] = "updated"
    updated = builder.build()

    assert original.generation == 2
    assert original.kwargs["name"] == "root"
    assert updated.generation == 7
    assert updated.kwargs["name"] == "updated"
