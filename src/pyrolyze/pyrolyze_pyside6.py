"""PySide6 window and widget helpers for mounting PyRolyze targets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


WidgetEventFn = Callable[[Any], None]


@dataclass
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


def render_semantic_node(node: Mapping[str, Any]) -> QWidget:
    kind = str(node.get("kind", ""))
    values = _mapping(node.get("values"))

    if kind == "section":
        children = tuple(render_semantic_node(child) for child in node.get("children", ()))
        return compose_section(
            str(values.get("title", "")),
            children,
            accent=_optional_str(values.get("accent")),
        )

    if kind == "row":
        children = tuple(render_semantic_node(child) for child in node.get("children", ()))
        widget = compose_section(
            str(values.get("headline", "")),
            children,
        )
        if "row_id" in node:
            widget.setProperty("row_id", node["row_id"])
        if "key" in node:
            widget.setProperty("key", node["key"])
        return widget

    if kind == "badge":
        label = QLabel(str(values.get("text", "")))
        label.setWordWrap(True)
        tone = values.get("tone")
        if tone is not None:
            label.setProperty("tone", tone)
        return label

    if kind == "text_field":
        return _build_text_field(
            field_id=str(node.get("field_id", "")),
            label_text=str(values.get("label", "")),
            value=str(values.get("value", "")),
            event_binding=None,
            on_after_event=None,
            read_only=True,
        )

    if kind == "toggle":
        checkbox = _build_toggle(
            label_text=str(values.get("label", "")),
            checked=bool(values.get("checked", False)),
            event_binding=None,
            on_after_event=None,
        )
        checkbox.setEnabled(False)
        return checkbox

    raise ValueError(f"Unsupported semantic node kind: {kind!r}")


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


def _dispatch_widget_event(
    callback: WidgetEventFn,
    payload: Any,
    *,
    on_after_event: Callable[[], None] | None,
) -> None:
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


__all__ = [
    "PyrolyzeWindow",
    "clear_layout",
    "compose_section",
    "create_window",
    "render_rows_map",
    "render_semantic_node",
    "render_widget_binding",
    "run_window",
    "set_window_content",
]
