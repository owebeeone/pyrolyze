"""PySide6 window and widget helpers for mounting PyRolyze targets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence, cast

from pyrolyze.api import UIElement
from pyrolyze.runtime.context import ModuleRegistry, SlotId
from pyrolyze.runtime.ui_nodes import UiNodeSpec, normalize_ui_elements
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


WidgetEventFn = Callable[[Any], None]
_NO_EVENT_PAYLOAD = object()


_module_registry = ModuleRegistry()
_UI_MODULE_ID = _module_registry.module_id("pyrolyze.pyrolyze_pyside6")
_UI_OWNER_SLOT = SlotId(_UI_MODULE_ID, 1)


@dataclass(slots=True)
class PyrolyzeWindow:
    app: QApplication
    window: QMainWindow
    scroll_area: QScrollArea
    content_widget: QWidget
    content_layout: QVBoxLayout

    def show(self) -> None:
        self.window.show()

    def exec(self) -> int:
        self.show()
        return self.app.exec()

    def close(self) -> None:
        self.window.close()


def create_window(
    title: str,
    *,
    width: int = 960,
    height: int = 720,
) -> PyrolyzeWindow:
    app = QApplication.instance() or QApplication([])
    window = QMainWindow()
    window.setWindowTitle(title)
    window.resize(width, height)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    content_layout.setContentsMargins(20, 20, 20, 20)
    content_layout.setSpacing(16)

    scroll_area.setWidget(content_widget)
    window.setCentralWidget(scroll_area)
    return PyrolyzeWindow(
        app=app,
        window=window,
        scroll_area=scroll_area,
        content_widget=content_widget,
        content_layout=content_layout,
    )


def run_window(host: PyrolyzeWindow) -> int:
    return host.exec()


def clear_layout(layout: QVBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif isinstance(child_layout, QVBoxLayout):
            clear_layout(child_layout)


def set_window_content(host: PyrolyzeWindow, widgets: Sequence[QWidget]) -> None:
    clear_layout(host.content_layout)
    for widget in widgets:
        host.content_layout.addWidget(widget)


def compose_section(
    title: str,
    children: Sequence[QWidget],
    *,
    accent: str | None = None,
) -> QGroupBox:
    section = QGroupBox(title)
    if accent is not None:
        section.setProperty("accent", accent)
    layout = QVBoxLayout(section)
    layout.setContentsMargins(14, 14, 14, 14)
    layout.setSpacing(10)
    for child in children:
        layout.addWidget(child)
    return section


def render_ui_element(
    element: UIElement | Mapping[str, Any],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> QWidget:
    spec = normalize_ui_elements(
        _UI_OWNER_SLOT,
        (_coerce_ui_element(element),),
    )[0]
    return _render_ui_spec(spec, on_after_event=on_after_event)


def render_ui_elements(
    elements: Sequence[UIElement | Mapping[str, Any]],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> list[QWidget]:
    specs = normalize_ui_elements(
        _UI_OWNER_SLOT,
        tuple(_coerce_ui_element(element) for element in elements),
    )
    return [_render_ui_spec(spec, on_after_event=on_after_event) for spec in specs]


def render_semantic_node(node: Mapping[str, Any]) -> QWidget:
    return render_ui_element(_coerce_ui_element(node))


def render_widget_binding(
    binding: Any,
    *,
    on_after_event: Callable[[], None] | None = None,
    on_row_click: Callable[[str], None] | None = None,
) -> QWidget:
    runtime_kind = str(getattr(binding, "runtime_kind", ""))
    properties = _mapping(getattr(binding, "properties", {}))
    events = _mapping(getattr(binding, "events", {}))

    if runtime_kind == "Label":
        label = QLabel(str(properties.get("text", "")))
        label.setWordWrap(True)
        return label

    if runtime_kind == "TextField":
        return _build_text_field(
            field_id=str(properties.get("field_id", "")),
            label_text=str(properties.get("label", "")),
            value=str(properties.get("value", "")),
            event_binding=events.get("textChanged"),
            on_after_event=on_after_event,
            read_only=False,
        )

    if runtime_kind == "Toggle":
        return _build_toggle(
            label_text=str(properties.get("label", "")),
            checked=bool(properties.get("checked", False)),
            event_binding=events.get("toggled"),
            on_after_event=on_after_event,
        )

    if runtime_kind == "ForBlockRows":
        return render_rows_map(properties.get("rows", {}), on_row_click=on_row_click)

    raise ValueError(f"Unsupported widget binding runtime kind: {runtime_kind!r}")


def render_rows_map(
    rows: Mapping[str, Mapping[str, Any]] | Mapping[str, Any],
    *,
    on_row_click: Callable[[str], None] | None = None,
) -> QWidget:
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)

    for row_key, row in rows.items():
        row_mapping = _mapping(row)
        detail_mode = str(row_mapping.get("detail_mode", "collapsed"))
        label = row_mapping.get("label") or row_mapping.get("headline") or row_key
        button = QPushButton(f"{label} [{detail_mode}]")
        button.setProperty("row_key", row_key)
        if "call_site_id" in row_mapping:
            button.setProperty("call_site_id", row_mapping["call_site_id"])
        if callable(on_row_click):
            button.clicked.connect(
                lambda checked=False, key=str(row_key): on_row_click(key)
            )
        layout.addWidget(button)

    if layout.count() == 0:
        layout.addWidget(QLabel("No rows"))

    return container


def _build_text_field(
    *,
    field_id: str,
    label_text: str,
    value: str,
    event_binding: Any,
    on_after_event: Callable[[], None] | None,
    read_only: bool,
) -> QWidget:
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    label = QLabel(label_text)
    line_edit = QLineEdit()
    line_edit.setObjectName(field_id)
    line_edit.setText(value)
    line_edit.setReadOnly(read_only)

    callback = getattr(event_binding, "callback", None)
    if callable(callback):
        line_edit.textChanged.connect(
            lambda next_value: _dispatch_widget_event(
                callback,
                next_value,
                on_after_event=on_after_event,
            )
        )

    layout.addWidget(label)
    layout.addWidget(line_edit)
    return container


def _build_toggle(
    *,
    label_text: str,
    checked: bool,
    event_binding: Any,
    on_after_event: Callable[[], None] | None,
) -> QCheckBox:
    checkbox = QCheckBox(label_text)
    checkbox.setChecked(checked)
    callback = getattr(event_binding, "callback", None)
    if callable(callback):
        checkbox.toggled.connect(
            lambda next_value: _dispatch_widget_event(
                callback,
                next_value,
                on_after_event=on_after_event,
            )
        )
    return checkbox


def _build_button(
    *,
    label_text: str,
    enabled: bool,
    visible: bool,
    on_press: Callable[..., None] | None,
    on_after_event: Callable[[], None] | None,
) -> QPushButton:
    button = QPushButton(label_text)
    button.setEnabled(enabled)
    button.setVisible(visible)
    if callable(on_press):
        button.clicked.connect(
            lambda checked=False: _dispatch_widget_event(
                cast(WidgetEventFn, on_press),
                _NO_EVENT_PAYLOAD,
                on_after_event=on_after_event,
            )
        )
    return button


def _build_ui_text_field(
    spec: UiNodeSpec,
    *,
    on_after_event: Callable[[], None] | None,
) -> QWidget:
    container = QWidget()
    container.setVisible(bool(spec.props["visible"]))
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    label = QLabel(str(spec.props["label"]))
    line_edit = QLineEdit()
    line_edit.setObjectName(str(spec.props["field_id"]))
    line_edit.setText(str(spec.props["value"]))
    line_edit.setEnabled(bool(spec.props["enabled"]))
    placeholder = spec.props.get("placeholder")
    if placeholder is not None:
        line_edit.setPlaceholderText(str(placeholder))

    on_change = spec.event_props.get("on_change")
    if callable(on_change):
        line_edit.textChanged.connect(
            lambda next_value: _dispatch_widget_event(
                cast(WidgetEventFn, on_change),
                next_value,
                on_after_event=on_after_event,
            )
        )

    on_submit = spec.event_props.get("on_submit")
    if callable(on_submit):
        line_edit.returnPressed.connect(
            lambda: _dispatch_widget_event(
                cast(WidgetEventFn, on_submit),
                _NO_EVENT_PAYLOAD,
                on_after_event=on_after_event,
            )
        )

    layout.addWidget(label)
    layout.addWidget(line_edit)
    return container


def _build_ui_toggle(
    spec: UiNodeSpec,
    *,
    on_after_event: Callable[[], None] | None,
) -> QCheckBox:
    checkbox = QCheckBox(str(spec.props["label"]))
    checkbox.setChecked(bool(spec.props["checked"]))
    checkbox.setEnabled(bool(spec.props["enabled"]))
    checkbox.setVisible(bool(spec.props["visible"]))

    on_toggle = spec.event_props.get("on_toggle")
    if callable(on_toggle):
        checkbox.toggled.connect(
            lambda next_value: _dispatch_widget_event(
                cast(WidgetEventFn, on_toggle),
                next_value,
                on_after_event=on_after_event,
            )
        )
    return checkbox


def _build_row_widget(
    spec: UiNodeSpec,
    *,
    on_after_event: Callable[[], None] | None,
) -> QWidget:
    container = QWidget()
    container.setVisible(bool(spec.props["visible"]))
    container.setProperty("row_id", spec.props["row_id"])
    container.setProperty("headline", spec.props["headline"])
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    headline = QLabel(str(spec.props["headline"]))
    layout.addWidget(headline)
    for child in spec.children:
        layout.addWidget(_render_ui_spec(child, on_after_event=on_after_event))
    return container


def _render_ui_spec(
    spec: UiNodeSpec,
    *,
    on_after_event: Callable[[], None] | None,
) -> QWidget:
    if spec.kind == "section":
        section = compose_section(
            str(spec.props["title"]),
            [
                _render_ui_spec(child, on_after_event=on_after_event)
                for child in spec.children
            ],
            accent=_optional_str(spec.props.get("accent")),
        )
        section.setVisible(bool(spec.props["visible"]))
        return section

    if spec.kind == "row":
        return _build_row_widget(spec, on_after_event=on_after_event)

    if spec.kind == "badge":
        label = QLabel(str(spec.props["text"]))
        label.setWordWrap(True)
        label.setVisible(bool(spec.props["visible"]))
        tone = spec.props.get("tone")
        if tone is not None:
            label.setProperty("tone", tone)
        return label

    if spec.kind == "button":
        return _build_button(
            label_text=str(spec.props["label"]),
            enabled=bool(spec.props["enabled"]),
            visible=bool(spec.props["visible"]),
            on_press=spec.event_props.get("on_press"),
            on_after_event=on_after_event,
        )

    if spec.kind == "text_field":
        return _build_ui_text_field(spec, on_after_event=on_after_event)

    if spec.kind == "toggle":
        return _build_ui_toggle(spec, on_after_event=on_after_event)

    raise ValueError(f"Unsupported semantic node kind: {spec.kind!r}")


def _dispatch_widget_event(
    callback: Callable[..., Any],
    payload: Any,
    *,
    on_after_event: Callable[[], None] | None,
) -> None:
    if payload is _NO_EVENT_PAYLOAD:
        callback()
    else:
        callback(payload)
    if callable(on_after_event):
        on_after_event()


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _coerce_ui_element(value: UIElement | Mapping[str, Any]) -> UIElement:
    if isinstance(value, UIElement):
        return value
    if not isinstance(value, Mapping):
        raise TypeError(f"expected UIElement or mapping, got {type(value).__name__}")

    kind = str(value.get("kind", ""))
    props = _mapping(value.get("props"))
    if not props:
        props = _mapping(value.get("values"))
    if kind == "row" and "row_id" in value and "row_id" not in props:
        props["row_id"] = value["row_id"]
    children = tuple(_coerce_ui_element(child) for child in value.get("children", ()))
    return UIElement(kind=kind, props=props, children=children)


__all__ = [
    "PyrolyzeWindow",
    "clear_layout",
    "compose_section",
    "create_window",
    "render_ui_element",
    "render_ui_elements",
    "render_rows_map",
    "render_semantic_node",
    "render_widget_binding",
    "run_window",
    "set_window_content",
]
