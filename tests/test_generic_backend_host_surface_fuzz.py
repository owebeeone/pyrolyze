from __future__ import annotations

from pyrolyze.api import pyrolyze
from pyrolyze.backends.model import MountMutationPolicy, MountReplayKind, TypeRef
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    HostPlacementChildKind,
    HostPlacementProfile,
    HostSurfaceStyle,
    MountInterfaceKind,
    MountPointProfile,
    MountStyleVariant,
    MountVariantSpec,
    NodeGenSpec,
    ParamSpec,
    capture_host_surface_replay_state,
    generate_argument_fuzz_replay,
    run_pyro,
)


def _host_surface_fuzz_backend() -> BuildPyroNodeBackend:
    return BuildPyroNodeBackend(
        (
            NodeGenSpec(
                name="node",
                constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            ),
            NodeGenSpec(
                name="text",
                base_name="node",
                host_child_kind=HostPlacementChildKind.WIDGET,
                constructor=(
                    ParamSpec(name="name", annotation=TypeRef("str")),
                    ParamSpec(name="text", annotation=TypeRef("str")),
                ),
            ),
            NodeGenSpec(
                name="row",
                base_name="node",
                host_child_kind=HostPlacementChildKind.NESTED_CONTAINER,
                constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
                mounts=(
                    MountVariantSpec(
                        name="child",
                        accepted_base="node",
                        default=True,
                        profiles=(
                            MountPointProfile(
                                label="nested_layout_surface",
                                style=MountStyleVariant(
                                    label="ordered_index",
                                    interface=MountInterfaceKind.ORDERED,
                                    replay_kind=MountReplayKind.INDEX,
                                ),
                                mutation_policy=MountMutationPolicy.PLACE_ONLY,
                                host_surface_style=HostSurfaceStyle(label="ordered_slots"),
                                host_placement_profile=HostPlacementProfile(
                                    label="nested_container_child",
                                    allowed_child_kinds=(
                                        HostPlacementChildKind.WIDGET,
                                        HostPlacementChildKind.NESTED_CONTAINER,
                                    ),
                                ),
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
                                label="nested_layout_surface",
                                style=MountStyleVariant(
                                    label="ordered_index",
                                    interface=MountInterfaceKind.ORDERED,
                                    replay_kind=MountReplayKind.INDEX,
                                ),
                                mutation_policy=MountMutationPolicy.PLACE_ONLY,
                                host_surface_style=HostSurfaceStyle(label="ordered_slots"),
                                host_placement_profile=HostPlacementProfile(
                                    label="nested_container_child",
                                    allowed_child_kinds=(
                                        HostPlacementChildKind.WIDGET,
                                        HostPlacementChildKind.NESTED_CONTAINER,
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
        module_name="example.generic_backend.host_surface_fuzz",
    )


def _load_program(backend: BuildPyroNodeBackend) -> object:
    backend.source_namespace()
    namespace = load_transformed_namespace(
        f"""
from {backend.module_name} import host, row, text

@pyrolyze
def panel(show_top, show_bottom, show_page):
    with host("root"):
        if show_top:
            text("top", "Top")
        else:
            text("top", "Top changed")
        if show_page:
            text("page", "Page size: 50")
        else:
            text("page", "Page size: 100")
        with row("controls"):
            text("minus", "-")
            text("count", "Count")
            text("plus", "+")
        if show_bottom:
            text("bottom", "Bottom")
        else:
            text("bottom", "Bottom changed")
""",
        module_name=f"{backend.module_name}.host_surface_fuzz_panel",
        filename=f"/virtual/{backend.module_name.replace('.', '/')}/host_surface_fuzz_panel.py",
        globals_dict={"pyrolyze": pyrolyze},
    )
    return namespace["panel"]


def test_seeded_host_surface_fuzz_replays_to_fresh_equivalent_state() -> None:
    backend = _host_surface_fuzz_backend()
    panel = _load_program(backend)
    replay = generate_argument_fuzz_replay(
        seed=19,
        step_count=32,
        argument_space={
            "show_top": (False, True),
            "show_bottom": (False, True),
            "show_page": (False, True),
        },
    )

    first = replay.steps[0]
    rerender_ctx = backend.context(
        panel,
        first.arguments["show_top"],
        first.arguments["show_bottom"],
        first.arguments["show_page"],
        initial_generation=0,
    )
    _ = rerender_ctx.get()

    for index, step in enumerate(replay.steps[1:], start=1):
        show_top = step.arguments["show_top"]
        show_bottom = step.arguments["show_bottom"]
        show_page = step.arguments["show_page"]

        rerendered = run_pyro(rerender_ctx.run(show_top, show_bottom, show_page).get())
        fresh = run_pyro(
            backend.context(
                panel,
                show_top,
                show_bottom,
                show_page,
                initial_generation=index + 1,
            ).get()
        )

        rerendered_state = capture_host_surface_replay_state(rerendered)
        fresh_state = capture_host_surface_replay_state(fresh)
        host_order = rerendered_state.host_surface_orders["child_nested_layout_surface"]
        host_kinds = rerendered_state.host_surface_kinds["child_nested_layout_surface"]

        assert rerendered_state == fresh_state, (
            f"seed={replay.seed} step={index} args={dict(step.arguments)} "
            f"rerendered={rerendered_state} fresh={fresh_state}"
        )
        assert host_order == ("top", "page", "controls", "bottom"), (
            f"seed={replay.seed} step={index} args={dict(step.arguments)} host_order={host_order}"
        )
        assert host_kinds == ("widget", "widget", "nested_container", "widget"), (
            f"seed={replay.seed} step={index} args={dict(step.arguments)} host_kinds={host_kinds}"
        )
        assert host_order.index("controls") < host_order.index("bottom"), (
            f"seed={replay.seed} step={index} args={dict(step.arguments)} host_order={host_order}"
        )
