from __future__ import annotations

import pytest

from pyrolyze.api import mount_key, pyrolyze
from pyrolyze.backends.model import TypeRef
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
    PyrolyzeMountCompatibilityError,
    run_pyro,
)


def _compat_specs() -> tuple[NodeGenSpec, ...]:
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
            name="menu",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
        ),
        NodeGenSpec(
            name="row",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="child",
                    accepted_base="node",
                    interface=MountInterfaceKind.ORDERED,
                    default=True,
                ),
            ),
        ),
        NodeGenSpec(
            name="text_row",
            base_name="node",
            constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            mounts=(
                MountSpec(
                    name="child",
                    accepted_kind="text",
                    interface=MountInterfaceKind.ORDERED,
                    default=True,
                ),
            ),
        ),
    )


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


def test_compat_exact_kind_accepts_valid_child() -> None:
    backend = BuildPyroNodeBackend(_compat_specs(), module_name="example.generic_backend.compat.valid")

    namespace = _load_program(
        backend,
        "valid_panel",
        f"""
from {backend.module_name} import text, text_row

@pyrolyze
def panel():
    with text_row("root"):
        text("leaf", "hello")
""",
    )

    snapshot = run_pyro(backend.context(namespace["panel"]).get())

    assert snapshot.node_type == "text_row"
    assert tuple(entry.node.node_type for entry in snapshot.mounts["child"][0].entries) == ("text",)


def test_compat_base_kind_accepts_multiple_subclasses() -> None:
    backend = BuildPyroNodeBackend(_compat_specs(), module_name="example.generic_backend.compat.base")

    namespace = _load_program(
        backend,
        "base_panel",
        f"""
from {backend.module_name} import menu, row, text

@pyrolyze
def panel():
    with row("root"):
        text("text-leaf", "hello")
        menu("menu-leaf")
""",
    )

    snapshot = run_pyro(backend.context(namespace["panel"]).get())

    assert tuple(entry.node.node_type for entry in snapshot.mounts["child"][0].entries) == ("text", "menu")


def test_compat_advert_routed_invalid_child_still_fails() -> None:
    backend = BuildPyroNodeBackend(_compat_specs(), module_name="example.generic_backend.compat.advert")
    child_selector = backend.selector_family("child")
    public_key = mount_key("body")

    namespace = _load_program(
        backend,
        "advert_panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import menu, text_row

@pyrolyze
def panel():
    with text_row("root"):
        advertise_mount(PUBLIC, target=CHILD, default=True)
        with mount(PUBLIC):
            menu("bad-menu")
""",
        PUBLIC=public_key,
        CHILD=child_selector,
    )

    with pytest.raises(PyrolyzeMountCompatibilityError, match="text_row"):
        backend.context(namespace["panel"]).get()


def test_compat_first_pass_valid_then_rerender_invalid_fails() -> None:
    backend = BuildPyroNodeBackend(_compat_specs(), module_name="example.generic_backend.compat.rerender")
    child_selector = backend.selector_family("child")
    public_key = mount_key("body")

    namespace = _load_program(
        backend,
        "rerender_panel",
        f"""
from pyrolyze.api import advertise_mount, mount
from {backend.module_name} import menu, text, text_row

@pyrolyze
def panel(show_menu):
    with text_row("root"):
        advertise_mount(PUBLIC, target=CHILD, default=True)
        with mount(PUBLIC):
            if show_menu:
                menu("bad-menu")
            else:
                text("good-text", "hello")
""",
        PUBLIC=public_key,
        CHILD=child_selector,
    )

    ctx = backend.context(namespace["panel"], False, initial_generation=10)
    first = run_pyro(ctx.get())

    assert tuple(entry.node.node_type for entry in first.mounts["child"][0].entries) == ("text",)

    with pytest.raises(PyrolyzeMountCompatibilityError, match="text_row"):
        ctx.run(True).get()


def test_compat_debug_mode_can_disable_runtime_type_checks_temporarily() -> None:
    backend = BuildPyroNodeBackend(_compat_specs(), module_name="example.generic_backend.compat.debug")

    namespace = _load_program(
        backend,
        "debug_panel",
        f"""
from {backend.module_name} import menu, text_row

@pyrolyze
def panel():
    with text_row("root"):
        menu("menu-leaf")
""",
    )

    render_ctx = RenderContext()
    namespace["panel"]._pyrolyze_meta._func(render_ctx, dirtyof())
    ui_root = render_ctx.committed_ui()[0]
    engine = backend.engine(strict_compatibility=False)

    mounted = engine.mount(
        ui_root,
        slot_id=("root", 1),
        call_site_id=1,
    )
    snapshot = engine.snapshot(mounted)

    assert tuple(entry.node.node_type for entry in snapshot.mounts["child"][0].entries) == ("menu",)
