from __future__ import annotations

import types
from typing import Any, Union, get_args, get_origin


def _union_members(annotation: Any) -> tuple[Any, ...]:
    origin = get_origin(annotation)
    if origin is Union or origin is types.UnionType:
        return get_args(annotation)
    return (annotation,)


def _is_none_type(annotation: Any) -> bool:
    return annotation is type(None)


def _is_class_narrower_or_equal(sub_annotation: Any, super_annotation: Any) -> bool:
    if sub_annotation == super_annotation:
        return True
    if super_annotation is Any:
        return True
    if not isinstance(sub_annotation, type) or not isinstance(super_annotation, type):
        return False
    return issubclass(sub_annotation, super_annotation)


def _is_generic_narrower_or_equal(sub_annotation: Any, super_annotation: Any) -> bool:
    sub_origin = get_origin(sub_annotation)
    super_origin = get_origin(super_annotation)
    if sub_origin != super_origin:
        return False

    sub_args = get_args(sub_annotation)
    super_args = get_args(super_annotation)
    if len(sub_args) != len(super_args):
        return False

    return all(
        is_annotation_narrower_or_equal(sub_arg, super_arg)
        for sub_arg, super_arg in zip(sub_args, super_args, strict=True)
    )


def is_annotation_narrower_or_equal(sub_annotation: Any, super_annotation: Any) -> bool:
    """Return whether ``sub_annotation`` is a compatible narrowing of ``super_annotation``.

    This is intentionally pragmatic rather than a full type-theory engine. It is
    designed for managed-field merge compatibility checks where a derived class
    may narrow a base annotation.
    """

    if sub_annotation == super_annotation:
        return True
    if super_annotation is Any:
        return True

    sub_members = _union_members(sub_annotation)
    super_members = _union_members(super_annotation)
    if len(sub_members) > 1 or len(super_members) > 1:
        return all(
            any(
                is_annotation_narrower_or_equal(sub_member, super_member)
                for super_member in super_members
            )
            for sub_member in sub_members
        )

    sub_single = sub_members[0]
    super_single = super_members[0]

    if _is_none_type(sub_single) or _is_none_type(super_single):
        return sub_single == super_single

    sub_origin = get_origin(sub_single)
    super_origin = get_origin(super_single)
    if sub_origin is not None or super_origin is not None:
        return _is_generic_narrower_or_equal(sub_single, super_single)

    return _is_class_narrower_or_equal(sub_single, super_single)


__all__ = ["is_annotation_narrower_or_equal"]
