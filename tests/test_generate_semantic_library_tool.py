from __future__ import annotations

import inspect
from pathlib import Path
import sys

import pytest
from frozendict import frozendict

from pyrolyze.backends.model import (
    EventPayloadPolicy,
    FillPolicy,
    MethodMode,
    MountReplayKind,
    TypeRef,
    UiMethodLearning,
    UiMountPointLearning,
    UiMountParamLearning,
    UiPropLearning,
    UiWidgetLearning,
)
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary

from pyrolyze_tools.generate_semantic_library import (
    DiscoveredMountPoint,
    DiscoveredParameter,
    DiscoveredProperty,
    DiscoveredSetterMethod,
    DiscoveredWidgetClass,
    apply_learnings,
    _extract_multiarg_setter_methods,
    _extract_pyside6_parameters,
    _extract_qt_properties,
    discover_modules,
    discover_widget_classes,
    generate_pyside6_learnings_source,
    generate_library_source,
    infer_pyside6_learnings,
    main,
    write_generated_library,
)


def _write_fake_widget_package(root: Path) -> None:
    package_dir = root / "fakewidgets"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("from .widgets import AlphaWidget, VariadicWidget\n")
    (package_dir / "__main__.py").write_text("raise RuntimeError('should not import __main__')\n")
    (package_dir / "base.py").write_text(
        "class WidgetBase:\n"
        "    pass\n"
    )
    (package_dir / "widgets.py").write_text(
        "from __future__ import annotations\n"
        "from .base import WidgetBase\n"
        "\n"
        "class AlphaWidget(WidgetBase):\n"
        "    def __init__(self, title: str, *, visible: bool = True, count: int = 0) -> None:\n"
        "        self.title = title\n"
        "        self.visible = visible\n"
        "        self.count = count\n"
        "\n"
        "class VariadicWidget(WidgetBase):\n"
        "    def __init__(self, parent=None, **kw) -> None:\n"
        "        self.parent = parent\n"
        "        self.kw = kw\n"
    )
    (package_dir / "extras.py").write_text(
        "class NotAWidget:\n"
        "    pass\n"
    )


def test_discover_modules_recurses_package(tmp_path: Path, monkeypatch) -> None:
    _write_fake_widget_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    modules = discover_modules("fakewidgets")

    assert "fakewidgets" in modules
    assert "fakewidgets.base" in modules
    assert "fakewidgets.widgets" in modules
    assert "fakewidgets.extras" in modules
    assert "fakewidgets.__main__" not in modules


def test_discover_widget_classes_filters_by_base_class(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_fake_widget_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    widgets = discover_widget_classes(
        "fakewidgets",
        widget_base_specs=("fakewidgets.base:WidgetBase",),
    )

    assert [widget.class_name for widget in widgets] == ["AlphaWidget", "VariadicWidget"]
    assert widgets[0].public_name == "CAlphaWidget"
    assert widgets[1].public_name == "CVariadicWidget"


def test_generate_library_source_renders_explicit_parameters_and_coercions(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_fake_widget_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    widgets = discover_widget_classes(
        "fakewidgets",
        widget_base_specs=("fakewidgets.base:WidgetBase",),
    )
    source = generate_library_source("fakewidgets", widgets)

    assert source.startswith("#@pyrolyze\n")
    assert "@ui_interface" in source
    assert "class FakewidgetsUiLibrary:" in source
    assert "def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:" in source
    assert "from frozendict import frozendict" in source
    assert "from pyrolyze.backends.model import" in source
    assert "UI_INTERFACE: ClassVar[UiInterface]" in source
    assert "WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]]" in source
    assert "def CAlphaWidget(" in source
    assert "title: str" in source
    assert "visible: bool = True" in source
    assert "count: int = 0" in source
    assert "visible=visible" in source
    assert "count=count" in source
    assert "call_native(cls.__element)(" in source
    assert "# NOTE: original signature for VariadicWidget includes omitted variadic arguments" in source


def test_generate_library_source_renders_qt_property_metadata() -> None:
    source = generate_library_source(
        "PySide6",
        [
            DiscoveredWidgetClass(
                module_name="PySide6.QtWidgets",
                class_name="QPushButton",
                public_name="CQPushButton",
                parameters=(),
                properties=(
                    DiscoveredProperty(
                        name="enabled",
                        type_name="bool",
                        readable=True,
                        writable=True,
                    ),
                    DiscoveredProperty(
                        name="text",
                        type_name="QString",
                        readable=True,
                        writable=True,
                    ),
                ),
            )
        ],
    )

    assert source.startswith("#@pyrolyze\n")
    assert "class PySide6UiLibrary:" in source
    assert "import PySide6" in source
    assert (
        "from pyrolyze.api import MISSING, MissingType, MountSelector, PyrolyzeHandler, UIElement, call_native, "
        "pyrolyze, ui_interface" in source
    )
    assert 'QT_PROPERTY_GETTER: ClassVar[str] = "property"' in source
    assert 'QT_PROPERTY_SETTER: ClassVar[str] = "setProperty"' in source
    assert 'WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]]' in source
    assert 'UiWidgetSpec(' in source
    assert 'UiPropSpec(' in source
    assert 'name="text"' in source
    assert 'mode=PropMode.CREATE_UPDATE' in source
    assert 'setter_kind=AccessorKind.QT_PROPERTY' in source
    assert "def CQPushButton(" in source
    assert "enabled: bool | MissingType = MISSING" in source
    assert "text: str | MissingType = MISSING" in source


def test_generated_pyside6_line_edit_exposes_text_changed_event() -> None:
    spec = PySide6UiLibrary.WIDGET_SPECS["QLineEdit"]

    event = spec.events["on_textChanged"]

    assert event.signal_name == "textChanged"
    assert event.payload_policy is EventPayloadPolicy.FIRST_ARG


def test_generated_pyside6_scroll_area_prefers_widget_for_default_attach() -> None:
    spec = PySide6UiLibrary.WIDGET_SPECS["QScrollArea"]

    assert "widget" in spec.default_attach_mount_point_names
    assert "viewport" in spec.default_attach_mount_point_names
    assert spec.default_attach_mount_point_names.index("widget") < spec.default_attach_mount_point_names.index(
        "viewport"
    )


def test_generated_pyside6_library_exposes_mount_selector_artifacts() -> None:
    assert PySide6UiLibrary.mounts.layout.name == "layout"
    assert PySide6UiLibrary.mounts.menu_bar.name == "menu_bar"
    assert PySide6UiLibrary.mounts.central_widget.name == "central_widget"


def test_generate_library_source_renders_mount_selector_artifacts() -> None:
    source = generate_library_source(
        "fakewidgets",
        [
            DiscoveredWidgetClass(
                module_name="fakewidgets.widgets",
                class_name="Panel",
                public_name="CPanel",
                parameters=(),
                mount_points=(
                    DiscoveredMountPoint(
                        name="widget",
                        accepted_type_name="fakewidgets.widgets.Child",
                        sync_method_name="sync_widgets",
                    ),
                    DiscoveredMountPoint(
                        name="menu",
                        accepted_type_name="fakewidgets.widgets.Child",
                        sync_method_name="sync_menus",
                    ),
                ),
            )
        ],
    )

    assert "from pyrolyze.api import MISSING, MissingType, MountSelector, PyrolyzeHandler" in source
    assert "class mounts:" in source
    assert 'widget = MountSelector.named("widget")' in source
    assert 'menu = MountSelector.named("menu")' in source


def test_generate_library_source_renders_discovered_method_specs() -> None:
    source = generate_library_source(
        "fakewidgets",
        [
            DiscoveredWidgetClass(
                module_name="fakewidgets.widgets",
                class_name="GeometryWidget",
                public_name="CGeometryWidget",
                parameters=(),
                setter_methods=(
                    DiscoveredSetterMethod(
                        owner_class_name="GeometryWidget",
                        name="setGeometry",
                        parameters=(
                            DiscoveredParameter(
                                name="x",
                                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                annotation_source="int",
                                default_source=None,
                                coerced_expression="int(x)",
                            ),
                            DiscoveredParameter(
                                name="y",
                                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                annotation_source="int",
                                default_source=None,
                                coerced_expression="int(y)",
                            ),
                            DiscoveredParameter(
                                name="width",
                                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                annotation_source="int",
                                default_source=None,
                                coerced_expression="int(width)",
                            ),
                            DiscoveredParameter(
                                name="height",
                                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                annotation_source="int",
                                default_source=None,
                                coerced_expression="int(height)",
                            ),
                        ),
                    ),
                ),
            )
        ],
    )

    assert "FillPolicy," in source
    assert "MethodMode," in source
    assert "UiMethodSpec," in source
    assert 'methods=frozendict({' in source
    assert '"setGeometry": UiMethodSpec(' in source
    assert 'mode=MethodMode.CREATE_UPDATE' in source
    assert 'source_props=("x", "y", "width", "height")' in source
    assert 'fill_policy=FillPolicy.RETAIN_EFFECTIVE' in source
    assert 'constructor_equivalent=False' in source


def test_generate_library_source_renders_mount_point_specs() -> None:
    source = generate_library_source(
        "fakewidgets",
        [
            DiscoveredWidgetClass(
                module_name="fakewidgets.widgets",
                class_name="LayoutWidget",
                public_name="CLayoutWidget",
                parameters=(),
                mount_points=(
                    DiscoveredMountPoint(
                        name="standard",
                        accepted_type_name="fakewidgets.widgets.LayoutWidget",
                        params=(),
                        min_children=0,
                        max_children=None,
                        apply_method_name=None,
                        sync_method_name="sync_widgets",
                        place_method_name="place_widget",
                        append_method_name="append_widget",
                        detach_method_name="detach_widget",
                        replay_kind=MountReplayKind.INDEX,
                        prefer_sync=True,
                    ),
                ),
            )
        ],
    )

    assert "MountParamSpec," in source
    assert "MountPointSpec," in source
    assert "mount_points=frozendict({" in source
    assert '"standard": MountPointSpec(' in source
    assert 'accepted_produced_type=TypeRef(expr=\'fakewidgets.widgets.LayoutWidget\')' in source
    assert "default_child_mount_point_name='standard'" in source
    assert "default_attach_mount_point_names=('standard',)" in source
    assert "sync_method_name='sync_widgets'" in source
    assert "place_method_name='place_widget'" in source
    assert "append_method_name='append_widget'" in source
    assert "detach_method_name='detach_widget'" in source
    assert "replay_kind=MountReplayKind.INDEX" in source
    assert "prefer_sync=True" in source


def test_write_generated_library_uses_package_name_for_output(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_fake_widget_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    widgets = discover_widget_classes(
        "fakewidgets",
        widget_base_specs=("fakewidgets.base:WidgetBase",),
    )

    out_file = write_generated_library(
        "fakewidgets",
        widgets,
        output_dir=tmp_path / "out",
    )

    assert out_file.name == "fakewidgets.py"
    assert out_file.exists()
    assert "class FakewidgetsUiLibrary:" in out_file.read_text()


def test_write_generated_library_writes_raw_source_not_lowered_module(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_fake_widget_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    widgets = discover_widget_classes(
        "fakewidgets",
        widget_base_specs=("fakewidgets.base:WidgetBase",),
    )

    out_file = write_generated_library(
        "fakewidgets",
        widgets,
        output_dir=tmp_path / "out",
    )

    source = out_file.read_text()
    assert "@pyrolyze" in source
    assert "__pyr_component_ref" not in source


def test_main_generates_file_from_module_name(tmp_path: Path, monkeypatch) -> None:
    _write_fake_widget_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    out_dir = tmp_path / "generated"
    exit_code = main(
        [
            "fakewidgets",
            "--widget-base",
            "fakewidgets.base:WidgetBase",
            "--output-dir",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert (out_dir / "fakewidgets.py").exists()


def test_extract_pyside6_parameters_prefers_stub_signatures() -> None:
    pytest.importorskip("PySide6.QtWidgets")
    from PySide6.QtWidgets import QPushButton

    parameters = _extract_pyside6_parameters(QPushButton)
    names = [parameter.name for parameter in parameters]

    assert "text" in names
    assert "parent" in names
    assert "autoDefault" in names
    assert "default" in names
    assert "flat" in names


def test_extract_qt_properties_uses_metaobject() -> None:
    pytest.importorskip("PySide6.QtWidgets")
    from PySide6.QtWidgets import QPushButton

    properties = {prop.name: prop for prop in _extract_qt_properties(QPushButton)}

    assert properties["text"].type_name == "QString"
    assert properties["text"].readable is True
    assert properties["text"].writable is True
    assert properties["enabled"].type_name == "bool"


def test_extract_pyside6_setters_ignore_property_backed_single_value_setters() -> None:
    pytest.importorskip("PySide6.QtWidgets")
    from PySide6.QtWidgets import QPushButton

    methods = {method.name for method in _extract_multiarg_setter_methods("PySide6", QPushButton)}

    assert "setGeometry" in methods
    assert "setText" not in methods


def test_extract_tkinter_multiarg_setters_filters_generic_setvar() -> None:
    pytest.importorskip("tkinter")
    from tkinter import Scrollbar

    methods = {method.name for method in _extract_multiarg_setter_methods("tkinter", Scrollbar)}

    assert "set" in methods
    assert "setvar" not in methods


def test_discover_widget_classes_captures_multiarg_setters_in_raw_phase() -> None:
    pytest.importorskip("PySide6.QtWidgets")

    widgets = discover_widget_classes("PySide6")
    push_button = next(widget for widget in widgets if widget.class_name == "QPushButton")

    assert "setGeometry" in {method.name for method in push_button.setter_methods}


def test_discover_widget_classes_includes_pyside6_mountable_base_classes_and_mount_points() -> None:
    pytest.importorskip("PySide6.QtWidgets")

    widgets = discover_widget_classes("PySide6")
    by_name = {widget.class_name: widget for widget in widgets}

    assert "QWidget" in by_name
    assert "QLayout" in by_name
    assert "QAction" in by_name

    assert "layout" in {mount.name for mount in by_name["QWidget"].mount_points}
    assert "central_widget" in {mount.name for mount in by_name["QMainWindow"].mount_points}
    assert "widget" in {mount.name for mount in by_name["QBoxLayout"].mount_points}


def test_discover_widget_classes_includes_tkinter_mount_points() -> None:
    pytest.importorskip("tkinter")
    pytest.importorskip("tkinter.ttk")

    widgets = discover_widget_classes("tkinter")
    by_name = {widget.class_name: widget for widget in widgets}
    by_identity = {(widget.module_name, widget.class_name): widget for widget in widgets}

    assert "Notebook" in by_name
    assert "PanedWindow" in by_name
    assert "Panedwindow" in by_name
    assert "tab" in {mount.name for mount in by_name["Notebook"].mount_points}
    assert "pane" in {mount.name for mount in by_identity[("tkinter", "PanedWindow")].mount_points}
    assert "pane" in {mount.name for mount in by_name["Panedwindow"].mount_points}


def test_discover_widget_classes_includes_pyside6_single_arg_setters() -> None:
    pytest.importorskip("PySide6.QtWidgets")

    widgets = discover_widget_classes("PySide6")
    by_name = {widget.class_name: widget for widget in widgets}

    assert "setSeparator" in {method.name for method in by_name["QAction"].setter_methods}


def test_discover_widget_classes_includes_tkinter_single_arg_setters() -> None:
    pytest.importorskip("tkinter")
    pytest.importorskip("tkinter.ttk")

    widgets = discover_widget_classes("tkinter")
    by_identity = {(widget.module_name, widget.class_name): widget for widget in widgets}

    assert "set" in {method.name for method in by_identity[("tkinter.ttk", "Combobox")].setter_methods}


def test_discover_widget_classes_includes_tkinter_config_props_for_common_widgets() -> None:
    pytest.importorskip("tkinter")
    pytest.importorskip("tkinter.ttk")

    widgets = discover_widget_classes("tkinter")
    by_identity = {(widget.module_name, widget.class_name): widget for widget in widgets}

    raw_button_props = {prop.name for prop in by_identity[("tkinter", "Button")].properties}
    ttk_button_props = {prop.name for prop in by_identity[("tkinter.ttk", "Button")].properties}
    raw_entry_props = {prop.name for prop in by_identity[("tkinter", "Entry")].properties}
    ttk_entry_props = {prop.name for prop in by_identity[("tkinter.ttk", "Entry")].properties}
    raw_frame_props = {prop.name for prop in by_identity[("tkinter", "Frame")].properties}
    menu_props = {prop.name for prop in by_identity[("tkinter", "Menu")].properties}

    assert "text" in raw_button_props
    assert "command" in raw_button_props
    assert "text" in ttk_button_props
    assert "command" in ttk_button_props
    assert "show" in raw_entry_props
    assert "show" in ttk_entry_props
    assert "width" in raw_frame_props
    assert "tearoff" in menu_props


def test_discover_widget_classes_includes_tkinter_pack_mount_for_frames() -> None:
    pytest.importorskip("tkinter")
    pytest.importorskip("tkinter.ttk")

    widgets = discover_widget_classes("tkinter")
    by_identity = {(widget.module_name, widget.class_name): widget for widget in widgets}

    raw_frame_mounts = {mount.name for mount in by_identity[("tkinter", "Frame")].mount_points}
    ttk_frame_mounts = {mount.name for mount in by_identity[("tkinter.ttk", "Frame")].mount_points}

    assert "pack" in raw_frame_mounts
    assert "pack" in ttk_frame_mounts
    assert "grid" in raw_frame_mounts
    assert "grid" in ttk_frame_mounts


def test_apply_learnings_overrides_property_signature_defaults() -> None:
    widgets = [
        DiscoveredWidgetClass(
            module_name="PySide6.QtWidgets",
            class_name="QPushButton",
            public_name="CQPushButton",
            parameters=(),
            properties=(
                DiscoveredProperty(
                    name="enabled",
                    type_name="bool",
                    readable=True,
                    writable=True,
                ),
            ),
        )
    ]

    resolved = apply_learnings(
        widgets,
        frozendict(
            {
                "QPushButton": UiWidgetLearning(
                    prop_learnings=frozendict(
                        {
                            "enabled": UiPropLearning(
                                signature_annotation=TypeRef("bool | None"),
                                signature_default_repr="None",
                            ),
                        }
                    )
                )
            }
        ),
    )
    source = generate_library_source("PySide6", resolved)

    assert "enabled: bool | None = None" in source


def test_apply_learnings_prefers_module_qualified_widget_keys_for_duplicates() -> None:
    widgets = [
        DiscoveredWidgetClass(
            module_name="tkinter",
            class_name="PanedWindow",
            public_name="CPanedWindow",
            parameters=(),
        ),
        DiscoveredWidgetClass(
            module_name="tkinter.tix",
            class_name="PanedWindow",
            public_name="CTixPanedWindow",
            parameters=(),
        ),
    ]

    resolved = apply_learnings(
        widgets,
        frozendict(
            {
                "tkinter:PanedWindow": UiWidgetLearning(public_name="CRawPanedWindow"),
                "PanedWindow": UiWidgetLearning(public_name="CFallbackPanedWindow"),
            }
        ),
    )

    assert resolved[0].public_name == "CRawPanedWindow"
    assert resolved[1].public_name == "CFallbackPanedWindow"


def test_apply_learnings_overrides_method_source_props_and_constructor_equivalence() -> None:
    widgets = [
        DiscoveredWidgetClass(
            module_name="fakewidgets.widgets",
            class_name="SpinWidget",
            public_name="CSpinWidget",
            parameters=(
                DiscoveredParameter(
                    name="minimum",
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    annotation_source="int | None",
                    default_source="...",
                    coerced_expression="minimum",
                ),
                DiscoveredParameter(
                    name="maximum",
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    annotation_source="int | None",
                    default_source="...",
                    coerced_expression="maximum",
                ),
            ),
            setter_methods=(
                DiscoveredSetterMethod(
                    owner_class_name="SpinWidget",
                    name="setRange",
                    parameters=(
                        DiscoveredParameter(
                            name="min",
                            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            annotation_source="int",
                            default_source=None,
                            coerced_expression="int(min)",
                        ),
                        DiscoveredParameter(
                            name="max",
                            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            annotation_source="int",
                            default_source=None,
                            coerced_expression="int(max)",
                        ),
                    ),
                ),
            ),
        )
    ]

    resolved = apply_learnings(
        widgets,
        frozendict(
            {
                "SpinWidget": UiWidgetLearning(
                    method_learnings=frozendict(
                        {
                            "setRange": UiMethodLearning(
                                source_props=("minimum", "maximum"),
                                constructor_equivalent=True,
                                fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                                mode=MethodMode.CREATE_UPDATE,
                            ),
                        }
                    )
                )
            }
        ),
    )
    source = generate_library_source("fakewidgets", resolved)

    assert '"setRange": UiMethodSpec(' in source
    assert 'source_props=("minimum", "maximum")' in source
    assert 'constructor_equivalent=True' in source


def test_apply_learnings_overrides_mount_point_shape_and_defaults() -> None:
    widgets = [
        DiscoveredWidgetClass(
            module_name="fakewidgets.widgets",
            class_name="PanelWidget",
            public_name="CPanelWidget",
            parameters=(),
            mount_points=(
                DiscoveredMountPoint(
                    name="widget",
                    accepted_type_name="fakewidgets.widgets.PanelWidget",
                    params=(
                        DiscoveredParameter(
                            name="column",
                            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            annotation_source="int",
                            default_source="0",
                            coerced_expression="int(column)",
                        ),
                    ),
                    min_children=0,
                    max_children=None,
                    place_method_name="insert_widget",
                    detach_method_name="detach_widget",
                    replay_kind=MountReplayKind.INDEX,
                ),
            ),
        )
    ]

    resolved = apply_learnings(
        widgets,
        frozendict(
            {
                "PanelWidget": UiWidgetLearning(
                    mount_point_learnings=frozendict(
                        {
                            "widget": UiMountPointLearning(
                                public_name="panel_widget",
                                param_learnings=frozendict(
                                    {
                                        "column": UiMountParamLearning(
                                            keyed=True,
                                            annotation=TypeRef("int | None"),
                                            default_repr="1",
                                        )
                                    }
                                ),
                                default_child=True,
                                default_attach_rank=0,
                                replay_kind=MountReplayKind.ANCHOR_BEFORE,
                                append_method_name="append_widget",
                                prefer_sync=True,
                            )
                        }
                    )
                )
            }
        ),
    )

    source = generate_library_source("fakewidgets", resolved)

    assert '"panel_widget": MountPointSpec(' in source
    assert 'MountParamSpec(name="column", annotation=TypeRef(expr=\'int | None\'), keyed=True, default_repr=\'1\')' in source
    assert "default_child_mount_point_name='panel_widget'" in source
    assert "default_attach_mount_point_names=('panel_widget',)" in source
    assert "append_method_name='append_widget'" in source
    assert "replay_kind=MountReplayKind.ANCHOR_BEFORE" in source
    assert "prefer_sync=True" in source


def test_learned_method_backed_source_props_become_public_parameters() -> None:
    widgets = [
        DiscoveredWidgetClass(
            module_name="fakewidgets.widgets",
            class_name="RangeOnlyWidget",
            public_name="CRangeOnlyWidget",
            parameters=(),
            setter_methods=(
                DiscoveredSetterMethod(
                    owner_class_name="RangeOnlyWidget",
                    name="setRange",
                    parameters=(
                        DiscoveredParameter(
                            name="min",
                            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            annotation_source="int",
                            default_source=None,
                            coerced_expression="int(min)",
                        ),
                        DiscoveredParameter(
                            name="max",
                            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            annotation_source="int",
                            default_source=None,
                            coerced_expression="int(max)",
                        ),
                    ),
                ),
            ),
        )
    ]

    resolved = apply_learnings(
        widgets,
        frozendict(
            {
                "RangeOnlyWidget": UiWidgetLearning(
                    method_learnings=frozendict(
                        {
                            "setRange": UiMethodLearning(
                                source_props=("minimum", "maximum"),
                                constructor_equivalent=True,
                                fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                                mode=MethodMode.CREATE_UPDATE,
                            ),
                        }
                    )
                )
            }
        ),
    )
    source = generate_library_source("fakewidgets", resolved)

    assert "def CRangeOnlyWidget(" in source
    assert "minimum: int | MissingType = MISSING" in source
    assert "maximum: int | MissingType = MISSING" in source
    assert "minimum=minimum" in source
    assert "maximum=maximum" in source


def test_infer_pyside6_learnings_maps_common_method_families() -> None:
    pytest.importorskip("PySide6.QtWidgets")

    learnings = infer_pyside6_learnings(discover_widget_classes("PySide6"))

    qpush = learnings["QPushButton"].method_learnings
    assert qpush["setGeometry"].source_props == (
        "geometry_x",
        "geometry_y",
        "geometry_width",
        "geometry_height",
    )
    assert qpush["setMaximumSize"].source_props == ("maximumWidth", "maximumHeight")
    assert qpush["setMaximumSize"].constructor_equivalent is True
    assert qpush["setMinimumSize"].source_props == ("minimumWidth", "minimumHeight")
    assert "setParent" not in qpush

    qspin = learnings["QSpinBox"].method_learnings
    assert qspin["setRange"].source_props == ("minimum", "maximum")
    assert qspin["setRange"].constructor_equivalent is True


def test_generate_pyside6_learnings_source_renders_module_constant() -> None:
    source = generate_pyside6_learnings_source(
        frozendict(
            {
                "QPushButton": UiWidgetLearning(
                    method_learnings=frozendict(
                        {
                            "setGeometry": UiMethodLearning(
                                source_props=(
                                    "geometry_x",
                                    "geometry_y",
                                    "geometry_width",
                                    "geometry_height",
                                ),
                                fill_policy=FillPolicy.RETAIN_EFFECTIVE,
                                mode=MethodMode.CREATE_UPDATE,
                                constructor_equivalent=False,
                            )
                        }
                    )
                ),
                "QWidget": UiWidgetLearning(
                    mount_point_learnings=frozendict(
                        {
                            "layout": UiMountPointLearning(
                                public_name="layout",
                                default_child=True,
                                replay_kind=MountReplayKind.INDEX,
                                prefer_sync=True,
                            )
                        }
                    )
                ),
            }
        )
    )

    assert "LEARNINGS: frozendict[str, UiWidgetLearning] = frozendict(" in source
    assert '"QPushButton": UiWidgetLearning(' in source
    assert '"setGeometry": UiMethodLearning(' in source
    assert 'source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height")' in source
    assert "UiMountPointLearning" in source
    assert '"layout": UiMountPointLearning(' in source
    assert "replay_kind=MountReplayKind.INDEX" in source
