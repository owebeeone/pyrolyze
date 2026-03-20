from __future__ import annotations

from typing import Any

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    PyrolyzeHandler,
    UIElement,
    pyrolyze_component_ref,
)


def __pyr_studio_splitter(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    splitter_id: str,
    *,
    orientation: str,
    sizes: tuple[int, ...] = (),
    handle_width: int = 7,
    visible: bool = True,
    on_splitter_moved: PyrolyzeHandler[[Any], None] | None = None,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="studio_splitter",
            props={
                "splitter_id": splitter_id,
                "orientation": orientation,
                "sizes": tuple(sizes),
                "handle_width": int(handle_width),
                "visible": bool(visible),
                "on_splitter_moved": on_splitter_moved,
            },
        )


@pyrolyze_component_ref(ComponentMetadata("studio_splitter", __pyr_studio_splitter))
def studio_splitter(
    splitter_id: str,
    *,
    orientation: str,
    sizes: tuple[int, ...] = (),
    handle_width: int = 7,
    visible: bool = True,
    on_splitter_moved: PyrolyzeHandler[[Any], None] | None = None,
) -> None:
    raise CallFromNonPyrolyzeContext("studio_splitter")


def __pyr_studio_tabs(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    tabs_id: str,
    *,
    movable: bool = False,
    closable: bool = False,
    current_index: int = 0,
    visible: bool = True,
    on_current_changed: PyrolyzeHandler[[Any], None] | None = None,
    on_tab_close: PyrolyzeHandler[[Any], None] | None = None,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="studio_tabs",
            props={
                "tabs_id": tabs_id,
                "movable": bool(movable),
                "closable": bool(closable),
                "current_index": int(current_index),
                "visible": bool(visible),
                "on_current_changed": on_current_changed,
                "on_tab_close": on_tab_close,
            },
        )


@pyrolyze_component_ref(ComponentMetadata("studio_tabs", __pyr_studio_tabs))
def studio_tabs(
    tabs_id: str,
    *,
    movable: bool = False,
    closable: bool = False,
    current_index: int = 0,
    visible: bool = True,
    on_current_changed: PyrolyzeHandler[[Any], None] | None = None,
    on_tab_close: PyrolyzeHandler[[Any], None] | None = None,
) -> None:
    raise CallFromNonPyrolyzeContext("studio_tabs")


def __pyr_studio_tab_page(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    page_id: str,
    *,
    title: str,
    closable: bool = False,
    visible: bool = True,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="studio_tab_page",
            props={
                "page_id": page_id,
                "title": title,
                "closable": bool(closable),
                "visible": bool(visible),
            },
        )


@pyrolyze_component_ref(ComponentMetadata("studio_tab_page", __pyr_studio_tab_page))
def studio_tab_page(
    page_id: str,
    *,
    title: str,
    closable: bool = False,
    visible: bool = True,
) -> None:
    raise CallFromNonPyrolyzeContext("studio_tab_page")


def __pyr_studio_toolbar(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    toolbar_id: str,
    *,
    title: str = "",
    visible: bool = True,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="studio_toolbar",
            props={
                "toolbar_id": toolbar_id,
                "title": title,
                "visible": bool(visible),
            },
        )


@pyrolyze_component_ref(ComponentMetadata("studio_toolbar", __pyr_studio_toolbar))
def studio_toolbar(
    toolbar_id: str,
    *,
    title: str = "",
    visible: bool = True,
) -> None:
    raise CallFromNonPyrolyzeContext("studio_toolbar")


def __pyr_studio_tree_view(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    tree_id: str,
    *,
    root_path: str,
    show_hidden: bool = False,
    visible: bool = True,
    on_selected: PyrolyzeHandler[[str], None] | None = None,
    on_activated: PyrolyzeHandler[[str], None] | None = None,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="studio_tree_view",
            props={
                "tree_id": tree_id,
                "root_path": root_path,
                "show_hidden": bool(show_hidden),
                "visible": bool(visible),
                "on_selected": on_selected,
                "on_activated": on_activated,
            },
        )


@pyrolyze_component_ref(ComponentMetadata("studio_tree_view", __pyr_studio_tree_view))
def studio_tree_view(
    tree_id: str,
    *,
    root_path: str,
    show_hidden: bool = False,
    visible: bool = True,
    on_selected: PyrolyzeHandler[[str], None] | None = None,
    on_activated: PyrolyzeHandler[[str], None] | None = None,
) -> None:
    raise CallFromNonPyrolyzeContext("studio_tree_view")


def __pyr_studio_status_strip(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    strip_id: str,
    *,
    status_message: str = "Ready",
    encoding: str = "UTF-8",
    line_col: str = "Ln 1, Col 1",
    indent_mode: str = "Spaces: 4",
    visible: bool = True,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="studio_status_strip",
            props={
                "strip_id": strip_id,
                "status_message": status_message,
                "encoding": encoding,
                "line_col": line_col,
                "indent_mode": indent_mode,
                "visible": bool(visible),
            },
        )


@pyrolyze_component_ref(ComponentMetadata("studio_status_strip", __pyr_studio_status_strip))
def studio_status_strip(
    strip_id: str,
    *,
    status_message: str = "Ready",
    encoding: str = "UTF-8",
    line_col: str = "Ln 1, Col 1",
    indent_mode: str = "Spaces: 4",
    visible: bool = True,
) -> None:
    raise CallFromNonPyrolyzeContext("studio_status_strip")


def __pyr_studio_overlay_canvas(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    overlay_id: str,
    *,
    target_rect: tuple[int, int, int, int] | None = None,
    highlight_color: str = "#ff0000",
    visible: bool = True,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="studio_overlay_canvas",
            props={
                "overlay_id": overlay_id,
                "target_rect": target_rect,
                "highlight_color": highlight_color,
                "visible": bool(visible),
            },
        )


@pyrolyze_component_ref(ComponentMetadata("studio_overlay_canvas", __pyr_studio_overlay_canvas))
def studio_overlay_canvas(
    overlay_id: str,
    *,
    target_rect: tuple[int, int, int, int] | None = None,
    highlight_color: str = "#ff0000",
    visible: bool = True,
) -> None:
    raise CallFromNonPyrolyzeContext("studio_overlay_canvas")


def __pyr_studio_screenshot_canvas(
    __pyr_ctx: object,
    __pyr_dirty_state: object,
    canvas_id: str,
    *,
    has_image: bool = False,
    stroke_color: str = "#ff0000",
    stroke_width: int = 2,
    visible: bool = True,
    on_draw_changed: PyrolyzeHandler[[Any], None] | None = None,
) -> None:
    del __pyr_dirty_state
    with __pyr_ctx.pass_scope():
        __pyr_ctx.call_native(
            UIElement,
            kind="studio_screenshot_canvas",
            props={
                "canvas_id": canvas_id,
                "has_image": bool(has_image),
                "stroke_color": stroke_color,
                "stroke_width": int(stroke_width),
                "visible": bool(visible),
                "on_draw_changed": on_draw_changed,
            },
        )


@pyrolyze_component_ref(ComponentMetadata("studio_screenshot_canvas", __pyr_studio_screenshot_canvas))
def studio_screenshot_canvas(
    canvas_id: str,
    *,
    has_image: bool = False,
    stroke_color: str = "#ff0000",
    stroke_width: int = 2,
    visible: bool = True,
    on_draw_changed: PyrolyzeHandler[[Any], None] | None = None,
) -> None:
    raise CallFromNonPyrolyzeContext("studio_screenshot_canvas")


__all__ = [
    "studio_overlay_canvas",
    "studio_screenshot_canvas",
    "studio_splitter",
    "studio_status_strip",
    "studio_tab_page",
    "studio_tabs",
    "studio_toolbar",
    "studio_tree_view",
]
