"""PySide6 window and widget helpers for mounting PyRolyze targets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence, cast

from pyrolyze.api import UIElement
from pyrolyze.runtime.context import ModuleRegistry, SlotId
from pyrolyze.runtime.ui_nodes import (
    UiBackendAdapter,
    UiNode,
    UiNodeBinding,
    UiNodeSpec,
    UiOwnerCommitState,
    mount_subtree,
    normalize_ui_inputs,
    reconcile_owner,
)
from PySide6.QtCore import QSignalBlocker, QThread, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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
    owner_state: UiOwnerCommitState | None = None

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
    host.owner_state = None
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


@dataclass(eq=False, slots=True, kw_only=True)
class _QtRootBinding(UiNodeBinding):
    container: QWidget
    layout: QVBoxLayout

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        return None

    def place_child(self, child: UiNode, index: int) -> None:
        widget = _binding_widget(child.binding)
        _layout_place_widget(self.layout, widget, index)

    def detach_child(self, child: UiNode) -> None:
        _layout_detach_widget(self.layout, _binding_widget(child.binding))

    def dispose(self) -> None:
        return None


@dataclass(eq=False, slots=True, kw_only=True)
class _QtBindingBase(UiNodeBinding):
    widget: QWidget
    layout: QVBoxLayout | QHBoxLayout | None = None
    child_offset: int = 0

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        return None

    def place_child(self, child: UiNode, index: int) -> None:
        if self.layout is None:
            raise ValueError(f"{type(self).__name__} does not accept children")
        _layout_place_widget(self.layout, _binding_widget(child.binding), index + self.child_offset)

    def detach_child(self, child: UiNode) -> None:
        if self.layout is None:
            return
        _layout_detach_widget(self.layout, _binding_widget(child.binding))

    def dispose(self) -> None:
        self.widget.setParent(None)
        self.widget.deleteLater()


@dataclass(eq=False, slots=True, kw_only=True)
class _QtSectionBinding(_QtBindingBase):
    widget: QGroupBox
    layout: QVBoxLayout

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        if "title" in changed_props:
            self.widget.setTitle(str(next_spec.props["title"]))
        if "accent" in changed_props:
            self.widget.setProperty("accent", _optional_str(next_spec.props.get("accent")))
        if "visible" in changed_props:
            self.widget.setVisible(bool(next_spec.props["visible"]))


@dataclass(eq=False, slots=True, kw_only=True)
class _QtRowBinding(_QtBindingBase):
    widget: QWidget
    layout: QHBoxLayout
    headline: QLabel
    child_offset: int = 1

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        if "headline" in changed_props:
            self.headline.setText(str(next_spec.props["headline"]))
            self.widget.setProperty("headline", next_spec.props["headline"])
        if "row_id" in changed_props:
            self.widget.setProperty("row_id", next_spec.props["row_id"])
        if "visible" in changed_props:
            self.widget.setVisible(bool(next_spec.props["visible"]))


@dataclass(eq=False, slots=True, kw_only=True)
class _QtBadgeBinding(_QtBindingBase):
    widget: QLabel

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        if "text" in changed_props:
            self.widget.setText(str(next_spec.props["text"]))
        if "tone" in changed_props:
            self.widget.setProperty("tone", next_spec.props.get("tone"))
        if "visible" in changed_props:
            self.widget.setVisible(bool(next_spec.props["visible"]))


@dataclass(eq=False, slots=True, kw_only=True)
class _QtButtonBinding(_QtBindingBase):
    widget: QPushButton
    on_after_event: Callable[[], None] | None
    on_press: Callable[..., None] | None = None

    def __post_init__(self) -> None:
        self.widget.clicked.connect(self._handle_click)

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        if "label" in changed_props:
            self.widget.setText(str(next_spec.props["label"]))
        if "enabled" in changed_props:
            self.widget.setEnabled(bool(next_spec.props["enabled"]))
        if "tone" in changed_props:
            self.widget.setProperty("tone", next_spec.props.get("tone"))
        if "visible" in changed_props:
            self.widget.setVisible(bool(next_spec.props["visible"]))
        if "on_press" in changed_events:
            self.on_press = next_spec.event_props.get("on_press")

    def _handle_click(self, checked: bool = False) -> None:
        del checked
        if callable(self.on_press):
            _dispatch_widget_event(
                cast(WidgetEventFn, self.on_press),
                _NO_EVENT_PAYLOAD,
                on_after_event=self.on_after_event,
            )


@dataclass(eq=False, slots=True, kw_only=True)
class _QtTextFieldBinding(_QtBindingBase):
    widget: QWidget
    layout: QVBoxLayout
    label: QLabel
    line_edit: QLineEdit
    on_after_event: Callable[[], None] | None
    on_change: Callable[..., None] | None = None
    on_submit: Callable[..., None] | None = None

    def __post_init__(self) -> None:
        self.line_edit.textChanged.connect(self._handle_text_changed)
        self.line_edit.returnPressed.connect(self._handle_submit)

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        if "label" in changed_props:
            self.label.setText(str(next_spec.props["label"]))
        if "value" in changed_props:
            next_value = str(next_spec.props["value"])
            if self.line_edit.text() != next_value:
                blocker = QSignalBlocker(self.line_edit)
                self.line_edit.setText(next_value)
                del blocker
        if "enabled" in changed_props:
            self.line_edit.setEnabled(bool(next_spec.props["enabled"]))
        if "placeholder" in changed_props:
            placeholder = next_spec.props.get("placeholder")
            self.line_edit.setPlaceholderText("" if placeholder is None else str(placeholder))
        if "visible" in changed_props:
            self.widget.setVisible(bool(next_spec.props["visible"]))
        if "on_change" in changed_events:
            self.on_change = next_spec.event_props.get("on_change")
        if "on_submit" in changed_events:
            self.on_submit = next_spec.event_props.get("on_submit")

    def _handle_text_changed(self, next_value: str) -> None:
        if callable(self.on_change):
            _dispatch_widget_event(
                cast(WidgetEventFn, self.on_change),
                next_value,
                on_after_event=self.on_after_event,
            )

    def _handle_submit(self) -> None:
        if callable(self.on_submit):
            _dispatch_widget_event(
                cast(WidgetEventFn, self.on_submit),
                _NO_EVENT_PAYLOAD,
                on_after_event=self.on_after_event,
            )


@dataclass(eq=False, slots=True, kw_only=True)
class _QtToggleBinding(_QtBindingBase):
    widget: QCheckBox
    on_after_event: Callable[[], None] | None
    on_toggle: Callable[..., None] | None = None

    def __post_init__(self) -> None:
        self.widget.toggled.connect(self._handle_toggle)

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        if "label" in changed_props:
            self.widget.setText(str(next_spec.props["label"]))
        if "checked" in changed_props:
            blocker = QSignalBlocker(self.widget)
            self.widget.setChecked(bool(next_spec.props["checked"]))
            del blocker
        if "enabled" in changed_props:
            self.widget.setEnabled(bool(next_spec.props["enabled"]))
        if "visible" in changed_props:
            self.widget.setVisible(bool(next_spec.props["visible"]))
        if "on_toggle" in changed_events:
            self.on_toggle = next_spec.event_props.get("on_toggle")

    def _handle_toggle(self, next_value: bool) -> None:
        if callable(self.on_toggle):
            _dispatch_widget_event(
                cast(WidgetEventFn, self.on_toggle),
                next_value,
                on_after_event=self.on_after_event,
            )


@dataclass(eq=False, slots=True, kw_only=True)
class _QtSelectFieldBinding(_QtBindingBase):
    widget: QWidget
    layout: QVBoxLayout
    label: QLabel
    combo_box: QComboBox
    on_after_event: Callable[[], None] | None
    on_change: Callable[..., None] | None = None

    def __post_init__(self) -> None:
        self.combo_box.currentTextChanged.connect(self._handle_change)

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        if "label" in changed_props:
            self.label.setText(str(next_spec.props["label"]))
        if "options" in changed_props:
            _replace_combo_items(self.combo_box, next_spec.props["options"])
        if "value" in changed_props or "options" in changed_props:
            _set_combo_value(self.combo_box, str(next_spec.props["value"]))
        if "enabled" in changed_props:
            self.combo_box.setEnabled(bool(next_spec.props["enabled"]))
        if "visible" in changed_props:
            self.widget.setVisible(bool(next_spec.props["visible"]))
        if "on_change" in changed_events:
            self.on_change = next_spec.event_props.get("on_change")

    def _handle_change(self, next_value: str) -> None:
        if callable(self.on_change):
            _dispatch_widget_event(
                cast(WidgetEventFn, self.on_change),
                next_value,
                on_after_event=self.on_after_event,
            )


@dataclass(slots=True)
class _PySideBackend(UiBackendAdapter):
    app: QApplication
    on_after_event: Callable[[], None] | None = None
    backend_id: str = "pyside6"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        del parent_binding
        if spec.kind == "section":
            section = QGroupBox(str(spec.props["title"]))
            section.setProperty("accent", _optional_str(spec.props.get("accent")))
            section.setVisible(bool(spec.props["visible"]))
            layout = QVBoxLayout(section)
            layout.setContentsMargins(14, 14, 14, 14)
            layout.setSpacing(10)
            return _QtSectionBinding(widget=section, layout=layout)

        if spec.kind == "row":
            container = QWidget()
            container.setVisible(bool(spec.props["visible"]))
            container.setProperty("row_id", spec.props["row_id"])
            container.setProperty("headline", spec.props["headline"])
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(8)
            headline = QLabel(str(spec.props["headline"]))
            layout.addWidget(headline)
            return _QtRowBinding(widget=container, layout=layout, headline=headline)

        if spec.kind == "badge":
            label = QLabel(str(spec.props["text"]))
            label.setWordWrap(True)
            label.setVisible(bool(spec.props["visible"]))
            label.setProperty("tone", spec.props.get("tone"))
            return _QtBadgeBinding(widget=label)

        if spec.kind == "button":
            button = QPushButton(str(spec.props["label"]))
            button.setEnabled(bool(spec.props["enabled"]))
            button.setVisible(bool(spec.props["visible"]))
            button.setProperty("tone", spec.props.get("tone"))
            return _QtButtonBinding(
                widget=button,
                on_after_event=self.on_after_event,
                on_press=spec.event_props.get("on_press"),
            )

        if spec.kind == "text_field":
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
            line_edit.setPlaceholderText("" if placeholder is None else str(placeholder))
            layout.addWidget(label)
            layout.addWidget(line_edit)
            return _QtTextFieldBinding(
                widget=container,
                layout=layout,
                label=label,
                line_edit=line_edit,
                on_after_event=self.on_after_event,
                on_change=spec.event_props.get("on_change"),
                on_submit=spec.event_props.get("on_submit"),
            )

        if spec.kind == "toggle":
            checkbox = QCheckBox(str(spec.props["label"]))
            checkbox.setChecked(bool(spec.props["checked"]))
            checkbox.setEnabled(bool(spec.props["enabled"]))
            checkbox.setVisible(bool(spec.props["visible"]))
            return _QtToggleBinding(
                widget=checkbox,
                on_after_event=self.on_after_event,
                on_toggle=spec.event_props.get("on_toggle"),
            )

        if spec.kind == "select_field":
            container = QWidget()
            container.setVisible(bool(spec.props["visible"]))
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)
            label = QLabel(str(spec.props["label"]))
            combo_box = QComboBox()
            combo_box.setObjectName(str(spec.props["field_id"]))
            _replace_combo_items(combo_box, spec.props["options"])
            _set_combo_value(combo_box, str(spec.props["value"]))
            combo_box.setEnabled(bool(spec.props["enabled"]))
            layout.addWidget(label)
            layout.addWidget(combo_box)
            return _QtSelectFieldBinding(
                widget=container,
                layout=layout,
                label=label,
                combo_box=combo_box,
                on_after_event=self.on_after_event,
                on_change=spec.event_props.get("on_change"),
            )

        raise ValueError(f"Unsupported semantic node kind: {spec.kind!r}")

    def can_reuse(self, current: UiNode, next_spec: UiNodeSpec) -> bool:
        return current.spec.kind == next_spec.kind

    def assert_ui_thread(self) -> None:
        if QThread.currentThread() is not self.app.thread():
            raise RuntimeError("PySide6 reconciliation must run on the UI thread")

    def post_to_ui(self, callback: Callable[[], None]) -> None:
        QTimer.singleShot(0, callback)


def reconcile_window_content(
    host: PyrolyzeWindow,
    elements: Sequence[UIElement | Mapping[str, Any]],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> None:
    specs = normalize_ui_inputs(_UI_OWNER_SLOT, tuple(elements))
    if host.owner_state is None:
        clear_layout(host.content_layout)
        host.owner_state = UiOwnerCommitState(owner_id=_UI_OWNER_SLOT)
    reconcile_owner(
        host.owner_state,
        specs,
        backend=_PySideBackend(app=host.app, on_after_event=on_after_event),
        parent_binding=_QtRootBinding(
            container=host.content_widget,
            layout=host.content_layout,
        ),
    )


def render_ui_element(
    element: UIElement | Mapping[str, Any],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> QWidget:
    return render_ui_elements((element,), on_after_event=on_after_event)[0]


def render_ui_elements(
    elements: Sequence[UIElement | Mapping[str, Any]],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> list[QWidget]:
    backend = _PySideBackend(
        app=QApplication.instance() or QApplication([]),
        on_after_event=on_after_event,
    )
    specs = normalize_ui_inputs(_UI_OWNER_SLOT, tuple(elements))
    widgets: list[QWidget] = []
    for spec in specs:
        node = mount_subtree(spec, backend=backend)
        widget = _binding_widget(node.binding)
        setattr(widget, "_pyrolyze_node", node)
        widgets.append(widget)
    return widgets


def render_semantic_node(
    node: Mapping[str, Any],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> QWidget:
    return render_ui_element(node, on_after_event=on_after_event)


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


def _binding_widget(binding: UiNodeBinding) -> QWidget:
    widget = getattr(binding, "widget", None)
    if not isinstance(widget, QWidget):
        raise TypeError(f"binding {type(binding).__name__} does not expose a QWidget")
    return widget


def _layout_place_widget(
    layout: QVBoxLayout | QHBoxLayout,
    widget: QWidget,
    index: int,
) -> None:
    current_index = _layout_index(layout, widget)
    if current_index == index:
        return
    if current_index >= 0:
        layout.removeWidget(widget)
    layout.insertWidget(index, widget)


def _layout_detach_widget(layout: QVBoxLayout | QHBoxLayout, widget: QWidget) -> None:
    if _layout_index(layout, widget) < 0:
        return
    layout.removeWidget(widget)
    widget.setParent(None)


def _layout_index(layout: QVBoxLayout | QHBoxLayout, widget: QWidget) -> int:
    for index in range(layout.count()):
        item = layout.itemAt(index)
        if item is not None and item.widget() is widget:
            return index
    return -1


def _replace_combo_items(combo_box: QComboBox, options: Any) -> None:
    blocker = QSignalBlocker(combo_box)
    combo_box.clear()
    combo_box.addItems([str(option) for option in tuple(options)])
    del blocker


def _set_combo_value(combo_box: QComboBox, value: str) -> None:
    if combo_box.currentText() == value:
        return
    blocker = QSignalBlocker(combo_box)
    match_index = combo_box.findText(value)
    if match_index >= 0:
        combo_box.setCurrentIndex(match_index)
    elif combo_box.count() == 0:
        combo_box.addItem(value)
        combo_box.setCurrentIndex(0)
    else:
        combo_box.setCurrentText(value)
    del blocker


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
    "reconcile_window_content",
    "render_ui_element",
    "render_ui_elements",
    "render_rows_map",
    "render_semantic_node",
    "render_widget_binding",
    "run_window",
    "set_window_content",
]
