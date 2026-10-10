from __future__ import annotations

import pytest

from pyrolyze_tools.native_library_grouping import group_widget_kinds


def test_grouping_is_stable_bounded_and_family_isolated() -> None:
    families = {"Button": "controls", "Label": "controls", "Entry": "controls", "Row": "layouts"}
    groups = group_widget_kinds(families, maximum_kinds=2)
    assert groups == group_widget_kinds(dict(reversed(tuple(families.items()))), maximum_kinds=2)
    assert tuple((group.family, group.kinds) for group in groups) == (
        ("controls", ("Button", "Entry")),
        ("controls", ("Label",)),
        ("layouts", ("Row",)),
    )
    assert len({group.module_name for group in groups}) == len(groups)


def test_size_one_and_exact_cap_do_not_emit_empty_groups() -> None:
    families = {"A": "controls", "B": "controls"}
    assert tuple(group.kinds for group in group_widget_kinds(families, maximum_kinds=1)) == (("A",), ("B",))
    assert tuple(group.kinds for group in group_widget_kinds(families, maximum_kinds=2)) == (("A", "B"),)
    assert group_widget_kinds({}, maximum_kinds=2) == ()


@pytest.mark.parametrize("maximum", (0, -1, True, 1.5))
def test_invalid_cap_is_rejected(maximum: object) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        group_widget_kinds({"A": "controls"}, maximum_kinds=maximum)


@pytest.mark.parametrize("families", ({"": "controls"}, {"A": ""}))
def test_empty_kind_or_family_is_rejected(families: dict[str, str]) -> None:
    with pytest.raises(ValueError, match="nonempty"):
        group_widget_kinds(families, maximum_kinds=2)


def test_family_names_cannot_collide_in_module_names() -> None:
    groups = group_widget_kinds({"A": "a-b", "B": "a_b"}, maximum_kinds=2)
    assert len({group.module_name for group in groups}) == 2
    assert all(group.module_name.isidentifier() for group in groups)
