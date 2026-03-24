from __future__ import annotations

import pytest

from pyrolyze.api import mount_key, pyrolyze
from pyrolyze.backends.model import MountReplayKind, TypeRef
from pyrolyze.backends.mounts import resolve_mount_ops
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountParam,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
    run_pyro,
)


BODY = mount_key("body")
LEFT = mount_key("left")
RIGHT = mount_key("right")


def _load_program(
    backend: BuildPyroNodeBackend,
    module_suffix: str,
    source: str,
    **globals_dict: object,
) -> dict[str, object]:
    backend.source_namespace()
    return load_transformed_namespace(
        source,
        module_name=f"{backend.module_name}.{module_suffix}",
        filename=f"/virtual/{backend.module_name.replace('.', '/')}/{module_suffix}.py",
        globals_dict={
            "pyrolyze": pyrolyze,
            **globals_dict,
        },
    )


def _ordered_like_specs(*, replay_kind: MountReplayKind, prefer_sync: bool) -> tuple[NodeGenSpec, ...]:
    return (
        NodeGenSpec(
            name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
        ),
        NodeGenSpec(
            name="text",
            base_name="node",
            constructor=(
                ParamSpec(name="name", annotation=TypeRef("str")),
                ParamSpec(name="text", annotation=TypeRef("str")),
            ),
        ),
        NodeGenSpec(
            name="host",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="child",
                    accepted_base="node",
                    interface=MountInterfaceKind.ORDERED,
                    default=True,
                    replay_kind=replay_kind,
                    prefer_sync=prefer_sync,
                ),
            ),
        ),
    )


def _single_specs() -> tuple[NodeGenSpec, ...]:
    return (
        NodeGenSpec(
            name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
        ),
        NodeGenSpec(
            name="text",
            base_name="node",
            constructor=(
                ParamSpec(name="name", annotation=TypeRef("str")),
                ParamSpec(name="text", annotation=TypeRef("str")),
            ),
        ),
        NodeGenSpec(
            name="host",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="body",
                    accepted_base="node",
                    interface=MountInterfaceKind.SINGLE,
                    default=True,
                ),
            ),
        ),
    )


def _keyed_specs() -> tuple[NodeGenSpec, ...]:
    return (
        NodeGenSpec(
            name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
        ),
        NodeGenSpec(
            name="text",
            base_name="node",
            constructor=(
                ParamSpec(name="name", annotation=TypeRef("str")),
                ParamSpec(name="text", annotation=TypeRef("str")),
            ),
        ),
        NodeGenSpec(
            name="host",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="slot",
                    accepted_base="node",
                    interface=MountInterfaceKind.KEYED,
                    params=(MountParam(name="index", annotation=TypeRef("int"), keyed=True),),
                ),
            ),
        ),
    )


def _child_texts(snapshot: object, mount_name: str) -> tuple[str, ...]:
    node = run_pyro(snapshot)
    return tuple(entry.node.kwargs["text"] for entry in node.mounts[mount_name][0].entries)


def _keyed_bucket_texts(snapshot: object) -> dict[tuple[object, ...], str]:
    node = run_pyro(snapshot)
    return {
        bucket.key.args: bucket.entries[0].node.kwargs["text"]
        for bucket in node.mounts["slot"]
    }


def _single_body_text(snapshot: object) -> str:
    node = run_pyro(snapshot)
    return node.mounts["body"][0].entries[0].node.kwargs["text"]


@pytest.mark.parametrize(
    ("label", "replay_kind", "prefer_sync", "expect_anchor_before"),
    (
        ("index", MountReplayKind.INDEX, False, False),
        ("anchor", MountReplayKind.ANCHOR_BEFORE, True, True),
    ),
)
def test_ordered_adapter_replays_on_index_and_anchor_before_backends(
    label: str,
    replay_kind: MountReplayKind,
    prefer_sync: bool,
    expect_anchor_before: bool,
) -> None:
    backend = BuildPyroNodeBackend(
        _ordered_like_specs(replay_kind=replay_kind, prefer_sync=prefer_sync),
        module_name=f"example.generic_backend.adapter_replay.{label}",
    )
    child_selector = backend.selector_family("child")
    namespace = _load_program(
        backend,
        f"{label}_panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import host, text

@pyrolyze
def panel(reverse):
    with host("root"):
        advertise_mount(BODY, target=CHILD, default=True)
        with mount(BODY):
            if reverse:
                text("second", "Second")
                text("first", "First")
            else:
                text("first", "First")
                text("second", "Second")
""",
        BODY=BODY,
        CHILD=child_selector,
    )

    engine = backend.engine()
    mount_point = engine._mountable_specs["host"].mount_points["child"]
    resolved = resolve_mount_ops(backend.pyro_class("host"), mount_point)

    assert mount_point.replay_kind is replay_kind
    assert mount_point.prefer_sync is prefer_sync
    assert (resolved.place_before is not None) is expect_anchor_before
    assert (resolved.place is None) is expect_anchor_before

    rerender_ctx = backend.context(namespace["panel"], False, initial_generation=0)
    first = run_pyro(rerender_ctx.get())
    rerendered = run_pyro(rerender_ctx.run(True).get())
    fresh = run_pyro(backend.context(namespace["panel"], True, initial_generation=1).get())

    assert _child_texts(first, "child") == ("First", "Second")
    assert _child_texts(rerendered, "child") == ("Second", "First")
    assert rerendered == fresh


@pytest.mark.parametrize(("label", "specs", "module_suffix"), (
    ("single", _single_specs, "single"),
    ("keyed", _keyed_specs, "keyed"),
))
def test_same_adapter_pattern_can_target_single_and_keyed_shapes(
    label: str,
    specs: object,
    module_suffix: str,
) -> None:
    backend = BuildPyroNodeBackend(
        specs(),
        module_name=f"example.generic_backend.adapter_replay.{module_suffix}",
    )
    namespace = _load_program(
        backend,
        f"{module_suffix}_panel",
        f"""
from pyrolyze.api import advertise_mount, keyed, mount
from {backend.module_name} import host, text

@pyrolyze
def panel(reverse_consumers):
    with host("root"):
        for public_key, target, is_default in keyed(ADVERTISEMENTS, key=lambda item: item[0]):
            advertise_mount(public_key, target=target, default=is_default)
        if reverse_consumers:
            for public_key, payloads in keyed(tuple(reversed(CONSUMERS)), key=lambda item: item[0]):
                with mount(public_key):
                    for name, value in keyed(payloads, key=lambda item: item[0]):
                        text(name, value)
        else:
            for public_key, payloads in keyed(CONSUMERS, key=lambda item: item[0]):
                with mount(public_key):
                    for name, value in keyed(payloads, key=lambda item: item[0]):
                        text(name, value)
""",
        ADVERTISEMENTS=_advertisements_for_case(backend, label),
        CONSUMERS=_consumers_for_case(label),
    )

    first = run_pyro(backend.context(namespace["panel"], False, initial_generation=10).get())
    second = run_pyro(backend.context(namespace["panel"], True, initial_generation=10).get())

    if label == "single":
        assert _single_body_text(first) == "Body"
        assert first == second
        return

    assert _keyed_bucket_texts(first) == {
        (0,): "Left",
        (1,): "Right",
    }
    assert first == second


def _advertisements_for_case(
    backend: BuildPyroNodeBackend,
    label: str,
) -> tuple[tuple[object, object, bool], ...]:
    if label == "single":
        body_selector = backend.selector_family("body")
        return ((BODY, body_selector, True),)
    if label == "keyed":
        slot_selector = backend.selector_family("slot")
        return (
            (LEFT, slot_selector(index=0), False),
            (RIGHT, slot_selector(index=1), False),
        )
    raise ValueError(f"unsupported adapter replay case {label!r}")


def _consumers_for_case(label: str) -> tuple[tuple[object, tuple[tuple[str, str], ...]], ...]:
    if label == "single":
        return ((BODY, (("body", "Body"),)),)
    if label == "keyed":
        return (
            (LEFT, (("left", "Left"),)),
            (RIGHT, (("right", "Right"),)),
        )
    raise ValueError(f"unsupported adapter replay case {label!r}")
