from __future__ import annotations

from typing import Any

from pyrolyze.type_annotations import is_annotation_narrower_or_equal


class GeoPoint:
    pass


class Point(GeoPoint):
    pass


class OtherPoint:
    pass


def test_exact_annotation_match_is_allowed() -> None:
    assert is_annotation_narrower_or_equal(int, int)


def test_subclass_annotation_is_allowed() -> None:
    assert is_annotation_narrower_or_equal(Point, GeoPoint)


def test_unrelated_class_annotation_is_rejected() -> None:
    assert not is_annotation_narrower_or_equal(OtherPoint, GeoPoint)


def test_optional_list_annotation_may_narrow_element_type() -> None:
    assert is_annotation_narrower_or_equal(
        list[Point | None] | None,
        list[GeoPoint | None] | None,
    )


def test_union_target_allows_narrowing_to_one_parent_branch() -> None:
    assert is_annotation_narrower_or_equal(
        list[Point | None] | None,
        list[GeoPoint | OtherPoint | None] | None,
    )


def test_widening_annotation_is_rejected() -> None:
    assert not is_annotation_narrower_or_equal(
        list[GeoPoint | None] | None,
        list[Point | None] | None,
    )


def test_any_target_accepts_narrower_annotation() -> None:
    assert is_annotation_narrower_or_equal(list[Point], Any)


def test_different_container_origin_is_rejected() -> None:
    assert not is_annotation_narrower_or_equal(set[Point], list[GeoPoint])
