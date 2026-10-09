from __future__ import annotations

from typing import Callable

import pytest

from pyrolyze.api import PyrolyzeHandler, UIElement
from pyrolyze.compiler import emit_transformed_source, load_transformed_namespace
from pyrolyze.runtime import RenderContext, SlotId, SlotIdPath, dirtyof


def native_event_probe(
    on_press: PyrolyzeHandler[[], None], *, formatter: Callable[[str], str],
) -> UIElement:
    return UIElement(kind="button", props={"on_press": on_press, "formatter": formatter})


@pytest.mark.parametrize("imported", [False, True])
@pytest.mark.parametrize("arguments", [
    "lambda: LOG.append(label), formatter=lambda text: text",
    "on_press=lambda: LOG.append(label), formatter=lambda text: text",
])
def test_phase7_native_factory_wraps_only_declared_event_arguments(
    arguments: str, imported: bool,
) -> None:
    source = '''
from typing import Callable
from pyrolyze.api import PyrolyzeHandler as Handler, UIElement, call_native, pyrolyze

def button(on_press: Handler[[], None], *, formatter: Callable[[str], str]):
    return UIElement(kind="button", props={"on_press": on_press, "formatter": formatter})

@pyrolyze
def panel(label):
    call_native(button)(ARGUMENTS)
'''.replace("ARGUMENTS", arguments)
    if imported:
        source = source.replace(
            'def button(on_press: Handler[[], None], *, formatter: Callable[[str], str]):\n'
            '    return UIElement(kind="button", props={"on_press": on_press, "formatter": formatter})',
            'from tests.test_ast_phase7_native_call_rewrite import native_event_probe as button',
        )
    transformed = emit_transformed_source(source, module_name="example.phase7.native_event")
    assert transformed.count(".event_handler(") == 1
    assert ".event_handler_binding(" not in transformed
    assert "formatter=lambda text: text" in transformed


def test_phase7_lowers_call_native_factory_calls() -> None:
    source = """
from pyrolyze.api import Label, call_native, pyrolyze

@pyrolyze
def label_panel(text):
    call_native(Label)(text=text)
"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase7.label_panel",
        filename="/virtual/example/phase7/label_panel.py",
    )

    assert "__pyr_ctx.call_native(Label, text=text, __pyr_call_site_id=1)" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase7.label_panel",
        filename="/virtual/example/phase7/label_panel.py",
    )
    panel = namespace["label_panel"]
    ctx = RenderContext()

    panel._pyrolyze_meta._func(ctx, dirtyof(text=True), "Hello")
    assert ctx.debug_ui() == (
        UIElement(kind="Label", props={"text": "Hello"}),
    )
    assert ctx.debug_ui()[0].call_site_id == 1

    panel._pyrolyze_meta._func(ctx, dirtyof(text=False), "Hello")
    assert ctx.debug_ui() == (
        UIElement(kind="Label", props={"text": "Hello"}),
    )
    assert ctx.debug_ui()[0].call_site_id == 1


def test_phase7_packs_native_wrapper_kwargs_for_kwds_element_helpers() -> None:
    source = """
from typing import Any

from pyrolyze.api import UIElement, call_native, pyrolyze, ui_interface

@ui_interface
class PySide6UiLibrary:
    @classmethod
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    @classmethod
    @pyrolyze
    def CQPushButton(cls, text: str, *, flat: bool | None = None, enabled: bool | None = None) -> None:
        call_native(cls.__element)(kind="QPushButton", text=text, flat=flat, enabled=enabled)

"""

    transformed = emit_transformed_source(
        source,
        module_name="example.phase7.kwds_native_wrapper",
        filename="/virtual/example/phase7/kwds_native_wrapper.py",
    )

    assert "def __pyr_PySide6UiLibrary__CQPushButton(cls, __pyr_ctx, __pyr_dirty_state, **kwds):" in transformed
    assert "__pyr_ctx.call_native(cls.__element, kind='QPushButton', kwds=kwds, __pyr_call_site_id=1)" in transformed

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase7.kwds_native_wrapper",
        filename="/virtual/example/phase7/kwds_native_wrapper.py",
    )
    button_ref = namespace["PySide6UiLibrary"].CQPushButton
    ctx = RenderContext()

    with ctx.pass_scope():
        ctx.component_call(
            SlotId(901, 1, line_no=1),
            button_ref,
            "Save",
            enabled=True,
            dirty_state=dirtyof(text=True, enabled=True),
        )
    assert len(ctx.debug_ui()) == 1
    assert ctx.debug_ui()[0].kind == "QPushButton"
    assert ctx.debug_ui()[0].props == {"text": "Save", "enabled": True}
    assert ctx.debug_ui()[0].call_site_id == 1
    assert ctx.debug_ui()[0].slot_id == SlotIdPath((SlotId(901, 1, line_no=1),))


def test_phase7_packed_native_wrapper_only_emits_explicit_call_arguments() -> None:
    source = """
from typing import Any

from pyrolyze.api import UIElement, call_native, pyrolyze, ui_interface

@ui_interface
class PySide6UiLibrary:
    @classmethod
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    @classmethod
    @pyrolyze
    def CQPushButton(cls, text: str, *, flat: bool | None = None, enabled: bool | None = None) -> None:
        call_native(cls.__element)(kind="QPushButton", text=text, flat=flat, enabled=enabled)

"""

    namespace = load_transformed_namespace(
        source,
        module_name="example.phase7.kwds_native_wrapper_explicitness",
        filename="/virtual/example/phase7/kwds_native_wrapper_explicitness.py",
    )
    button_ref = namespace["PySide6UiLibrary"].CQPushButton

    omitted_ctx = RenderContext()
    with omitted_ctx.pass_scope():
        omitted_ctx.component_call(
            SlotId(902, 1, line_no=1),
            button_ref,
            "Save",
            dirty_state=dirtyof(text=True),
        )
    assert omitted_ctx.debug_ui()[0].props == {"text": "Save"}

    explicit_none_ctx = RenderContext()
    with explicit_none_ctx.pass_scope():
        explicit_none_ctx.component_call(
            SlotId(903, 1, line_no=1),
            button_ref,
            "Save",
            flat=None,
            dirty_state=dirtyof(text=True, flat=True),
        )
    assert explicit_none_ctx.debug_ui()[0].props == {"text": "Save", "flat": None}
