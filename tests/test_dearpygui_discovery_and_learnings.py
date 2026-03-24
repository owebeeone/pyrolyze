"""Phase 1–2: DearPyGui dump loading, canonical kinds, and learnings-shaped author surface."""

from __future__ import annotations

import pytest

from pyrolyze.backends.dearpygui.author_shape import (
    shape_canonical_mountable,
    widget_learning_for_kind,
)
from pyrolyze.backends.dearpygui.discovery import (
    classification_for,
    dearpygui_default_dump_path,
    factory_to_kind_name,
    iter_canonical_mountables,
    load_dearpygui_dump,
)
from pyrolyze.backends.dearpygui.learnings import LEARNINGS, dearpygui_learning_key
from pyrolyze.backends.model import UiWidgetLearning

pytestmark = pytest.mark.skipif(
    not dearpygui_default_dump_path().is_file(),
    reason="requires checked-in DearPyGui dump under scratch/dpg",
)


def test_load_dearpygui_dump_default_path() -> None:
    loaded = load_dearpygui_dump()
    assert loaded.dearpygui_version == "2.2"
    assert loaded.function_count == 497
    assert loaded.classification_counts["mountable_factory"] == 189
    assert loaded.classification_counts["mountable_context_alias"] == 42


def test_classification_preserved_for_known_functions() -> None:
    loaded = load_dearpygui_dump()
    assert classification_for(loaded, "add_button") == "mountable_factory"
    assert classification_for(loaded, "group") == "mountable_context_alias"
    assert classification_for(loaded, "apply_transform") == "backend_method_candidate"
    assert classification_for(loaded, "configure_item") == "backend_runtime_only"


def test_context_alias_maps_group_to_add_group() -> None:
    loaded = load_dearpygui_dump()
    assert loaded.context_alias_to_factory["group"] == "add_group"
    assert loaded.context_alias_to_factory["popup"] is None


def test_alias_metadata_on_canonical_group() -> None:
    loaded = load_dearpygui_dump()
    group = next(c for c in iter_canonical_mountables(loaded) if c.factory_name == "add_group")
    assert "group" in group.context_alias_names


def test_canonical_mountables_only_add_factories() -> None:
    loaded = load_dearpygui_dump()
    canonical = iter_canonical_mountables(loaded)
    assert len(canonical) == loaded.classification_counts["mountable_factory"]
    names = {c.factory_name for c in canonical}
    assert "group" not in names
    assert "add_group" in names


def test_kind_naming_plot_axis_and_theme_component() -> None:
    assert factory_to_kind_name("add_plot_axis") == "PlotAxis"
    assert factory_to_kind_name("add_theme_component") == "ThemeComponent"


def test_factory_to_kind_name_rejects_non_factory() -> None:
    with pytest.raises(ValueError, match="draw_"):
        factory_to_kind_name("group")


def test_kind_naming_draw_line() -> None:
    assert factory_to_kind_name("draw_line") == "DrawLine"


def test_phase2_button_events_and_suppressed_runtime_params() -> None:
    loaded = load_dearpygui_dump()
    button = next(c for c in iter_canonical_mountables(loaded) if c.factory_name == "add_button")
    shaped = shape_canonical_mountable(button)
    prop_names = {p.public_name for p in shaped.props}
    assert "tag" not in prop_names
    assert "parent" not in prop_names
    assert "before" not in prop_names
    assert "callback" not in prop_names
    event_names = {e.public_name for e in shaped.events}
    assert event_names == {"on_drop", "on_drag", "on_press"}


def test_phase2_input_text_default_value_becomes_value() -> None:
    loaded = load_dearpygui_dump()
    item = next(c for c in iter_canonical_mountables(loaded) if c.factory_name == "add_input_text")
    shaped = shape_canonical_mountable(item)
    prop_names = {p.public_name: p.constructor_name for p in shaped.props}
    assert prop_names.get("value") == "default_value"
    assert "default_value" not in prop_names


def test_phase2_window_mount_point_ranking() -> None:
    loaded = load_dearpygui_dump()
    window = next(c for c in iter_canonical_mountables(loaded) if c.factory_name == "add_window")
    shaped = shape_canonical_mountable(window)
    assert shaped.mount_point_names == ("menu_bar", "standard")
    assert {e.public_name for e in shaped.events} == {"on_close"}


def test_phase2_node_editor_includes_link_mount() -> None:
    loaded = load_dearpygui_dump()
    editor = next(c for c in iter_canonical_mountables(loaded) if c.factory_name == "add_node_editor")
    shaped = shape_canonical_mountable(editor)
    assert "link" in shaped.mount_point_names
    assert "node" in shaped.mount_point_names


def test_learnings_merge_uses_empty_default() -> None:
    w = widget_learning_for_kind("NonexistentKindXYZ")
    assert w == UiWidgetLearning()


def test_dearpygui_learning_keys_exist_for_curated_widgets() -> None:
    assert dearpygui_learning_key("Button") in LEARNINGS
    assert dearpygui_learning_key("Window") in LEARNINGS
