from __future__ import annotations

import inspect

from pyrolyze.api import MountSelector
from pyrolyze.backends.model import TypeRef
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
)


def _api_specs() -> tuple[NodeGenSpec, ...]:
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
                MountSpec(
                    name="child",
                    accepted_base="node",
                    interface=MountInterfaceKind.ORDERED,
                    default=True,
                ),
            ),
        ),
    )


def test_build_backend_exposes_direct_helpers_classes_and_selectors() -> None:
    backend = BuildPyroNodeBackend(_api_specs(), module_name="example.generic_backend.api")

    text = backend.pyro_func("text")
    row_type = backend.pyro_class("row")

    assert hasattr(text, "_pyrolyze_meta")
    assert text._pyrolyze_meta.name == "text"
    assert row_type.__name__ == "row"
    assert backend.selector_family("child") == MountSelector.named("child")


def test_direct_helper_signature_is_readable() -> None:
    backend = BuildPyroNodeBackend(_api_specs(), module_name="example.generic_backend.sig")

    text = backend.pyro_func("text")
    signature = inspect.signature(text)

    assert tuple(signature.parameters) == ("name", "text")
    assert text.__annotations__ == {"name": "str", "text": "str", "return": "None"}
