from __future__ import annotations

import pytest

from pyrolyze.api import mount_key, pyrolyze
from pyrolyze.backends.model import MountMutationPolicy, MountReplayKind, TypeRef
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountPointProfile,
    MountStyleVariant,
    MountVariantSpec,
    NodeGenSpec,
    ParamSpec,
    run_pyro,
)


def _expanded_specs() -> tuple[NodeGenSpec, ...]:
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
                MountVariantSpec(
                    name="child",
                    accepted_base="node",
                    profiles=(
                        MountPointProfile(
                            label="ordered_index",
                            style=MountStyleVariant(
                                label="ordered_index",
                                interface=MountInterfaceKind.ORDERED,
                                replay_kind=MountReplayKind.INDEX,
                            ),
                            mutation_policy=MountMutationPolicy.PLACE_ONLY,
                        ),
                        MountPointProfile(
                            label="tk_pack_surface",
                            style=MountStyleVariant(
                                label="ordered_sync_preferred",
                                interface=MountInterfaceKind.ORDERED,
                                replay_kind=MountReplayKind.NONE,
                                prefer_sync=True,
                            ),
                            mutation_policy=MountMutationPolicy.REPLAY_THEN_SYNC,
                            small_delta_threshold=8,
                        ),
                    ),
                ),
            ),
        ),
    )


BODY = mount_key("body")
INNER = mount_key("inner")


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


def _structure_summary(snapshot: object, mount_name: str) -> tuple[tuple[str, str], ...]:
    node = run_pyro(snapshot)
    summary: list[tuple[str, str]] = []
    for entry in node.mounts[mount_name][0].entries:
        child = entry.node
        if child.node_type == "text":
            summary.append(("text", child.kwargs["text"]))
        else:
            summary.append((child.node_type, child.kwargs["name"]))
    return tuple(summary)


def test_mount_variant_specs_expand_into_concrete_mount_surfaces() -> None:
    backend = BuildPyroNodeBackend(
        _expanded_specs(),
        module_name="example.generic_backend.mount_style_expansion",
    )

    host_spec = next(spec for spec in backend.node_specs if spec.name == "host")

    assert tuple(mount.name for mount in host_spec.mounts) == (
        "child_ordered_index",
        "child_tk_pack_surface",
    )
    assert host_spec.mounts[0].style_label == "ordered_index"
    assert host_spec.mounts[0].profile_label == "ordered_index"
    assert host_spec.mounts[0].mutation_policy is MountMutationPolicy.PLACE_ONLY
    assert host_spec.mounts[1].style_label == "ordered_sync_preferred"
    assert host_spec.mounts[1].profile_label == "tk_pack_surface"
    assert host_spec.mounts[1].mutation_policy is MountMutationPolicy.REPLAY_THEN_SYNC
    assert host_spec.mounts[1].small_delta_threshold == 8

    engine = backend.engine()
    mount_point = engine._mountable_specs["host"].mount_points["child_tk_pack_surface"]
    assert mount_point.mutation_policy is MountMutationPolicy.REPLAY_THEN_SYNC
    assert mount_point.small_delta_threshold == 8


def test_snapshot_exposes_style_and_profile_identity_for_expanded_mount_surface() -> None:
    backend = BuildPyroNodeBackend(
        _expanded_specs(),
        module_name="example.generic_backend.mount_style_expansion.snapshot",
    )

    host_type = backend.pyro_class("host")
    text_type = backend.pyro_class("text")
    root = host_type("root")
    child = text_type("first", "First")
    root.add_child_tk_pack_surface(child)

    snapshot = root.to_pyro_node()
    metadata = snapshot.mount_metadata["child_tk_pack_surface"]

    assert tuple(snapshot.mounts) == ("child_tk_pack_surface",)
    assert metadata["profile_label"] == "tk_pack_surface"
    assert metadata["style_label"] == "ordered_sync_preferred"
    assert metadata["interface"] == "ordered_mount"
    assert metadata["replay_kind"] == "none"
    assert metadata["prefer_sync"] is True
    assert metadata["mutation_policy"] == "replay_then_sync"
    assert metadata["small_delta_threshold"] == 8


@pytest.mark.parametrize(
    ("selected_mount", "expected_style", "use_sync_surface"),
    (
        ("child_ordered_index", "ordered_index", False),
        ("child_tk_pack_surface", "ordered_sync_preferred", True),
    ),
)
def test_generated_interface_can_exercise_only_the_selected_concrete_mount_surface(
    selected_mount: str,
    expected_style: str,
    use_sync_surface: bool,
) -> None:
    backend = BuildPyroNodeBackend(
        _expanded_specs(),
        module_name=f"example.generic_backend.mount_style_expansion.interface.{selected_mount}",
    )
    index_selector = backend.selector_family("child_ordered_index")
    sync_selector = backend.selector_family("child_tk_pack_surface")
    row_index_selector = backend.selector_family("child_ordered_index")
    row_sync_selector = backend.selector_family("child_tk_pack_surface")
    namespace = _load_program(
        backend,
        "panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import host, text

@pyrolyze
def panel(use_sync_surface):
    with host("root"):
        if use_sync_surface:
            advertise_mount(BODY, target=SYNC, default=True)
        else:
            advertise_mount(BODY, target=INDEX, default=True)
        with mount(BODY):
            text("only", "Only")
""",
        BODY=BODY,
        INDEX=index_selector,
        SYNC=sync_selector,
    )

    snapshot = run_pyro(backend.context(namespace["panel"], use_sync_surface).get())

    assert tuple(snapshot.mounts) == (selected_mount,)
    assert snapshot.mount_metadata[selected_mount]["style_label"] == expected_style
    assert {operation.mount_name for operation in snapshot.mount_operations} == {selected_mount}


@pytest.mark.parametrize(
    ("selected_mount", "use_sync_surface"),
    (
        ("child_ordered_index", False),
        ("child_tk_pack_surface", True),
    ),
)
def test_nested_retained_row_stays_before_trailing_sibling_under_branch_churn(
    selected_mount: str,
    use_sync_surface: bool,
) -> None:
    backend = BuildPyroNodeBackend(
        (
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
                name="row",
                base_name="node",
                constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
                mounts=(
                    MountVariantSpec(
                        name="child",
                        accepted_base="node",
                        default=True,
                        profiles=(
                            MountPointProfile(
                                label="ordered_index",
                                style=MountStyleVariant(
                                    label="ordered_index",
                                    interface=MountInterfaceKind.ORDERED,
                                    replay_kind=MountReplayKind.INDEX,
                                ),
                                    mutation_policy=MountMutationPolicy.PLACE_ONLY,
                            ),
                            MountPointProfile(
                                label="tk_pack_surface",
                                style=MountStyleVariant(
                                    label="ordered_sync_preferred",
                                    interface=MountInterfaceKind.ORDERED,
                                    replay_kind=MountReplayKind.NONE,
                                    prefer_sync=True,
                                ),
                                    mutation_policy=MountMutationPolicy.REPLAY_THEN_SYNC,
                            ),
                        ),
                    ),
                ),
            ),
            NodeGenSpec(
                name="host",
                base_name="node",
                constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
                mounts=(
                    MountVariantSpec(
                        name="child",
                        accepted_base="node",
                        default=True,
                        profiles=(
                            MountPointProfile(
                                label="ordered_index",
                                style=MountStyleVariant(
                                    label="ordered_index",
                                    interface=MountInterfaceKind.ORDERED,
                                    replay_kind=MountReplayKind.INDEX,
                                ),
                                    mutation_policy=MountMutationPolicy.PLACE_ONLY,
                            ),
                            MountPointProfile(
                                label="tk_pack_surface",
                                style=MountStyleVariant(
                                    label="ordered_sync_preferred",
                                    interface=MountInterfaceKind.ORDERED,
                                    replay_kind=MountReplayKind.NONE,
                                    prefer_sync=True,
                                ),
                                    mutation_policy=MountMutationPolicy.REPLAY_THEN_SYNC,
                            ),
                        ),
                    ),
                ),
            ),
        ),
        module_name=f"example.generic_backend.mount_style_expansion.branching.{selected_mount}",
    )
    index_selector = backend.selector_family("child_ordered_index")
    sync_selector = backend.selector_family("child_tk_pack_surface")
    row_index_selector = backend.selector_family("child_ordered_index")
    row_sync_selector = backend.selector_family("child_tk_pack_surface")
    namespace = _load_program(
        backend,
        "panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import host, row, text

@pyrolyze
def panel(show_top, use_sync_surface):
    with host("root"):
        if use_sync_surface:
            advertise_mount(BODY, target=SYNC, default=True)
        else:
            advertise_mount(BODY, target=INDEX, default=True)
        with mount(BODY):
            if show_top:
                text("top", "Top")
            with row("controls"):
                if use_sync_surface:
                    advertise_mount(INNER, target=ROW_SYNC, default=True)
                else:
                    advertise_mount(INNER, target=ROW_INDEX, default=True)
                with mount(INNER):
                    text("minus", "-")
                    text("count", "Count")
                    text("plus", "+")
            text("bottom", "Bottom")
""",
        BODY=BODY,
        INNER=INNER,
        INDEX=index_selector,
        ROW_INDEX=row_index_selector,
        SYNC=sync_selector,
        ROW_SYNC=row_sync_selector,
    )

    rerender_ctx = backend.context(namespace["panel"], True, use_sync_surface, initial_generation=0)
    _ = rerender_ctx.get()
    rerendered = run_pyro(rerender_ctx.run(False, use_sync_surface).get())
    fresh = run_pyro(backend.context(namespace["panel"], False, use_sync_surface, initial_generation=1).get())

    assert _structure_summary(rerendered, selected_mount) == _structure_summary(fresh, selected_mount)
    assert tuple(rerendered.mounts) == (selected_mount,)
    mounted_children = rerendered.mounts[selected_mount][0].entries
    assert tuple(entry.node.node_type for entry in mounted_children) == ("row", "text")
    assert mounted_children[0].node.kwargs["name"] == "controls"
    assert mounted_children[1].node.kwargs["text"] == "Bottom"
    assert _structure_summary(rerendered, selected_mount) == (("row", "controls"), ("text", "Bottom"))
    assert {operation.mount_name for operation in rerendered.mount_operations} == {selected_mount}
