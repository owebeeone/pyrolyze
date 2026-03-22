from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest
from frozendict import frozendict

from pyrolyze.api import MountSelector, SlotSelector, default, no_emit, validate_mount_selectors


def test_named_mount_selector_is_immutable_runtime_value() -> None:
    selector = MountSelector.named("menu")

    assert isinstance(selector, SlotSelector)
    assert selector.kind == "named"
    assert selector.name == "menu"
    assert selector.values == frozendict()

    with pytest.raises(FrozenInstanceError):
        selector.name = "widget"  # type: ignore[misc]


def test_named_mount_selector_call_returns_new_parameterized_value() -> None:
    selector = MountSelector.named("corner_widget")

    parameterized = selector(corner="top_left")

    assert parameterized is not selector
    assert selector.values == frozendict()
    assert parameterized.kind == "named"
    assert parameterized.name == "corner_widget"
    assert parameterized.values == frozendict({"corner": "top_left"})


def test_default_and_no_emit_are_special_selector_values() -> None:
    assert default.kind == "default"
    assert default.name == "default"
    assert default.values == frozendict()

    assert no_emit.kind == "no_emit"
    assert no_emit.name is None
    assert no_emit.values == frozendict()

    with pytest.raises(TypeError):
        default(corner="top_left")

    with pytest.raises(TypeError):
        no_emit(corner="top_left")


def test_validate_mount_selectors_accepts_named_and_default_terms() -> None:
    menu = MountSelector.named("menu")
    validated = validate_mount_selectors(menu, default)

    assert validated == (menu, default)


def test_validate_mount_selectors_rejects_no_emit_mixed_with_other_terms() -> None:
    menu = MountSelector.named("menu")

    with pytest.raises(ValueError, match="no_emit"):
        validate_mount_selectors(no_emit, menu)

    with pytest.raises(ValueError, match="no_emit"):
        validate_mount_selectors(menu, no_emit)


def test_validate_mount_selectors_rejects_non_selector_values() -> None:
    with pytest.raises(TypeError, match="SlotSelector"):
        validate_mount_selectors("menu")  # type: ignore[arg-type]
