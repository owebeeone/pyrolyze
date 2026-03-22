from __future__ import annotations

from pyrolyze.testing.hydo import (
    HydoAppWidget,
    HydoGridLayout,
    HydoHorizontalLayout,
    HydoLayout,
    HydoMenu,
    HydoOperation,
    HydoWidget,
    HydoWindow,
    build_demo_hierarchy,
    describe_hydo_api_surface,
    max_hydo_depth,
    walk_hydo_widgets,
)


def test_build_demo_hierarchy_produces_depth_five_widget_tree() -> None:
    window = build_demo_hierarchy()

    assert isinstance(window, HydoWindow)
    assert window.title == "Hydo Studio"
    assert isinstance(window.main_widget, HydoAppWidget)
    assert isinstance(window.title_bar_widget, HydoWidget)
    assert isinstance(window.title_bar_widget.layout, HydoHorizontalLayout)
    assert isinstance(window.main_widget.layout, HydoGridLayout)
    assert max_hydo_depth(window) >= 5

    widgets = tuple(walk_hydo_widgets(window))

    assert widgets
    assert all(isinstance(widget, HydoWidget) for widget in widgets)
    assert all(widget.layout is not None for widget in widgets)
    assert all(isinstance(widget.layout, HydoLayout) for widget in widgets)
    assert all(widget.layout.active is True for widget in widgets)
    assert any(isinstance(widget, HydoMenu) for widget in widgets)


def test_describe_hydo_api_surface_covers_supported_shape_categories() -> None:
    surface = describe_hydo_api_surface()

    assert surface["HydoWindow"]["single_mount_methods"] == (
        "set_layout",
        "set_main_widget",
        "set_title_bar_widget",
    )
    assert surface["HydoWidget"]["single_value_methods"] == (
        "set_enabled",
        "set_title",
        "set_visible",
    )
    assert surface["HydoWidget"]["grouped_value_methods"] == (
        "set_geometry",
        "set_range",
    )
    assert surface["HydoWidget"]["ordered_mount_methods"] == (
        "add_child",
        "insert_child",
    )
    assert surface["HydoWidget"]["keyed_mount_methods"] == ("set_corner_widget",)
    assert surface["HydoLayout"]["python_properties"] == ("active",)
    assert surface["HydoHorizontalLayout"]["ordered_mount_methods"] == (
        "add_widget",
        "insert_widget",
    )
    assert surface["HydoGridLayout"]["keyed_mount_methods"] == ("set_cell_widget",)
    assert "add_menu" in surface["HydoMenu"]["ordered_mount_methods"]
    assert "insert_menu" in surface["HydoMenu"]["ordered_mount_methods"]


def test_hydo_objects_record_stable_operation_logs() -> None:
    layout = HydoGridLayout(name="main-grid")
    widget = HydoWidget(name="body")
    widget.set_layout(layout)
    widget.set_title("Body")
    widget.set_geometry(10, 20, 300, 200)
    widget.set_range(1, 9)

    menu = HydoMenu(name="file-menu")
    menu_layout = HydoHorizontalLayout(name="menu-layout")
    menu.set_layout(menu_layout)

    widget.add_child(menu)
    widget.set_corner_widget("top_left", menu)
    layout.set_cell_widget(0, 1, menu, row_span=1, column_span=2)

    assert widget.operations == [
        HydoOperation(owner_type="HydoWidget", owner_name="body", method="set_layout", args=("HydoGridLayout:main-grid",)),
        HydoOperation(owner_type="HydoWidget", owner_name="body", method="set_title", args=("Body",)),
        HydoOperation(owner_type="HydoWidget", owner_name="body", method="set_geometry", args=(10, 20, 300, 200)),
        HydoOperation(owner_type="HydoWidget", owner_name="body", method="set_range", args=(1, 9)),
        HydoOperation(owner_type="HydoWidget", owner_name="body", method="add_child", args=("HydoMenu:file-menu",)),
        HydoOperation(owner_type="HydoWidget", owner_name="body", method="set_corner_widget", args=("top_left", "HydoMenu:file-menu")),
    ]
    assert layout.operations == [
        HydoOperation(
            owner_type="HydoGridLayout",
            owner_name="main-grid",
            method="set_cell_widget",
            args=(0, 1, "HydoMenu:file-menu"),
            kwargs=(("column_span", 2), ("row_span", 1)),
        )
    ]
