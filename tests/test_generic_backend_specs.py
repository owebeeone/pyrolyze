from __future__ import annotations

import pytest

from pyrolyze.backends.model import TypeRef
from pyrolyze.testing.generic_backend import (
    MountInterfaceKind,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
    validate_node_specs,
)


def test_validate_node_specs_rejects_duplicate_node_names() -> None:
    specs = (
        NodeGenSpec(name="Widget"),
        NodeGenSpec(name="Widget"),
    )

    with pytest.raises(ValueError, match="duplicate node spec name"):
        validate_node_specs(specs)


def test_validate_node_specs_rejects_unknown_base_or_accepted_type() -> None:
    specs = (
        NodeGenSpec(name="Widget"),
        NodeGenSpec(
            name="Row",
            base_name="MissingBase",
            mounts=(
                MountSpec(
                    name="child",
                    accepted_kind="MissingChild",
                    interface=MountInterfaceKind.ORDERED,
                    default=True,
                ),
            ),
        ),
    )

    with pytest.raises(ValueError, match="unknown base"):
        validate_node_specs(specs)


def test_validate_node_specs_accepts_base_compatible_mounts() -> None:
    specs = (
        NodeGenSpec(name="Widget"),
        NodeGenSpec(
            name="Text",
            base_name="Widget",
            constructor=(ParamSpec(name="text", annotation=TypeRef("str")),),
        ),
        NodeGenSpec(
            name="Row",
            base_name="Widget",
            mounts=(
                MountSpec(
                    name="child",
                    accepted_base="Widget",
                    interface=MountInterfaceKind.ORDERED,
                    default=True,
                ),
            ),
        ),
    )

    validated = validate_node_specs(specs)

    assert tuple(spec.name for spec in validated) == ("Widget", "Text", "Row")
