from __future__ import annotations

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
    generate_argument_fuzz_replay,
    run_pyro,
)


BODY = mount_key("body")
INNER = mount_key("inner")


def _fuzz_specs() -> tuple[NodeGenSpec, ...]:
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
            name="row",
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


def _load_program(backend: BuildPyroNodeBackend) -> object:
    backend.source_namespace()
    index_selector = backend.selector_family("child_ordered_index")
    sync_selector = backend.selector_family("child_tk_pack_surface")
    namespace = load_transformed_namespace(
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
                    advertise_mount(INNER, target=SYNC, default=True)
                else:
                    advertise_mount(INNER, target=INDEX, default=True)
                with mount(INNER):
                    text("minus", "-")
                    text("count", "Count")
                    text("plus", "+")
            text("bottom", "Bottom")
""",
        module_name=f"{backend.module_name}.fuzz_panel",
        filename=f"/virtual/{backend.module_name.replace('.', '/')}/fuzz_panel.py",
        globals_dict={
            "pyrolyze": pyrolyze,
            "BODY": BODY,
            "INNER": INNER,
            "INDEX": index_selector,
            "SYNC": sync_selector,
        },
    )
    return namespace["panel"]


def _structure_summary(snapshot: object, mount_name: str) -> tuple[tuple[str, str], ...]:
    node = run_pyro(snapshot)
    result: list[tuple[str, str]] = []
    for entry in node.mounts[mount_name][0].entries:
        child = entry.node
        if child.node_type == "text":
            result.append(("text", child.kwargs["text"]))
        else:
            result.append((child.node_type, child.kwargs["name"]))
    return tuple(result)


def test_seeded_mount_profile_fuzz_replays_to_fresh_equivalent_state() -> None:
    backend = BuildPyroNodeBackend(
        _fuzz_specs(),
        module_name="example.generic_backend.mount_fuzz",
    )
    panel = _load_program(backend)
    replay = generate_argument_fuzz_replay(
        seed=7,
        step_count=24,
        argument_space={
            "show_top": (False, True),
            "use_sync_surface": (False, True),
        },
    )

    first = replay.steps[0]
    rerender_ctx = backend.context(
        panel,
        first.arguments["show_top"],
        first.arguments["use_sync_surface"],
        initial_generation=0,
    )
    _ = rerender_ctx.get()

    for index, step in enumerate(replay.steps[1:], start=1):
        show_top = step.arguments["show_top"]
        use_sync_surface = step.arguments["use_sync_surface"]
        selected_mount = "child_tk_pack_surface" if use_sync_surface else "child_ordered_index"

        rerendered = run_pyro(rerender_ctx.run(show_top, use_sync_surface).get())
        fresh = run_pyro(backend.context(panel, show_top, use_sync_surface, initial_generation=index + 1).get())

        assert tuple(rerendered.mounts) == (selected_mount,), (
            f"seed={replay.seed} step={index} args={dict(step.arguments)}"
        )
        assert _structure_summary(rerendered, selected_mount) == _structure_summary(fresh, selected_mount), (
            f"seed={replay.seed} step={index} args={dict(step.arguments)}"
        )
