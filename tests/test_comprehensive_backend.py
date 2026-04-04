from __future__ import annotations

from pyrolyze.testing.comprehensive_backend import (
    ComprehensiveBackendShape,
    allowed_child_type_names_for_mount,
    build_comprehensive_backend,
    comprehensive_node_specs,
    selector_family_names,
)


def test_comprehensive_backend_generates_base_leaf_and_bin_name_matrix() -> None:
    specs = comprehensive_node_specs(
        shape=ComprehensiveBackendShape(base_type_count=2, leaves_per_base=2, bins_per_base=2)
    )
    names = tuple(spec.name for spec in specs)

    assert names == (
        "Node",
        "BaseAA",
        "LeafAA00",
        "LeafAA01",
        "BinAA00",
        "BinAA01",
        "BaseAB",
        "LeafAB00",
        "LeafAB01",
        "BinAB00",
        "BinAB01",
    )


def test_comprehensive_backend_adds_generated_scalar_fields_to_constructors() -> None:
    specs = comprehensive_node_specs(
        shape=ComprehensiveBackendShape(
            base_type_count=1,
            leaves_per_base=1,
            bins_per_base=1,
            n_int=2,
            n_str=2,
        )
    )
    by_name = {spec.name: spec for spec in specs}

    assert tuple(param.name for param in by_name["BaseAA"].constructor) == (
        "name",
        "fint_a",
        "fint_b",
        "fstr_a",
        "fstr_b",
    )
    assert tuple(param.name for param in by_name["LeafAA00"].constructor) == (
        "name",
        "label",
        "fint_a",
        "fint_b",
        "fstr_a",
        "fstr_b",
    )
    assert tuple(param.name for param in by_name["BinAA00"].constructor) == (
        "name",
        "fint_a",
        "fint_b",
        "fstr_a",
        "fstr_b",
    )


def test_comprehensive_backend_rotates_mount_names_across_mount_types() -> None:
    assert selector_family_names(
        shape=ComprehensiveBackendShape(base_type_count=2, leaves_per_base=1, bins_per_base=2)
    ) == (
        "MountKeyedAB",
        "MountNestedAB",
        "MountOrderedAA",
        "MountSingleAA",
    )


def test_comprehensive_backend_exposes_generated_functions_and_selectors() -> None:
    backend = build_comprehensive_backend(
        module_name="example.generic_backend.comprehensive_test",
        shape=ComprehensiveBackendShape(base_type_count=2, leaves_per_base=2, bins_per_base=2),
    )

    assert backend.pyro_func("LeafAA00").__name__ == "LeafAA00"
    assert backend.pyro_func("BinAB01").__name__ == "BinAB01"

    assert backend.selector_family("MountSingleAA").name == "MountSingleAA"
    assert backend.selector_family("MountOrderedAA").name == "MountOrderedAA"
    assert backend.selector_family("MountNestedAB").name == "MountNestedAB"
    assert backend.selector_family("MountKeyedAB").name == "MountKeyedAB"


def test_allowed_child_type_names_for_mount_filters_by_mount_kind() -> None:
    shape = ComprehensiveBackendShape(base_type_count=2, leaves_per_base=2, bins_per_base=2)

    ordered = allowed_child_type_names_for_mount("MountOrderedAA", shape=shape)
    nested = allowed_child_type_names_for_mount("MountNestedAB", shape=shape)
    keyed = allowed_child_type_names_for_mount("MountKeyedAB", shape=shape)

    assert "LeafAA00" in ordered
    assert "BinAA00" in ordered

    assert "LeafAB00" in nested
    assert "BinAB00" in nested

    assert "LeafAA00" in keyed
    assert "BinAA00" not in keyed
