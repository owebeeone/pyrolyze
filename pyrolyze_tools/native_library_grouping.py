"""Deterministic offline partitioning for generated native definition modules."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WidgetKindGroup:
    family: str
    kinds: tuple[str, ...]
    module_name: str


def group_widget_kinds(
    families: Mapping[str, str], *, maximum_kinds: int
) -> tuple[WidgetKindGroup, ...]:
    if type(maximum_kinds) is not int or maximum_kinds < 1:
        raise ValueError("maximum_kinds must be a positive integer")
    by_family: dict[str, list[str]] = {}
    for kind, family in families.items():
        if not isinstance(kind, str) or not kind or not isinstance(family, str) or not family:
            raise ValueError("kind and family must be nonempty strings")
        by_family.setdefault(family, []).append(kind)

    groups: list[WidgetKindGroup] = []
    for family in sorted(by_family):
        kinds = sorted(by_family[family])
        # Encoding, rather than punctuation replacement, keeps filenames unique.
        prefix = "family_" + family.encode("utf-8").hex()
        for index, start in enumerate(range(0, len(kinds), maximum_kinds)):
            groups.append(
                WidgetKindGroup(
                    family=family,
                    kinds=tuple(kinds[start:start + maximum_kinds]),
                    module_name=f"{prefix}_{index:04d}",
                )
            )
    return tuple(groups)
