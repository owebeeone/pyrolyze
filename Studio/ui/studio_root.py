#@pyrolyze
from typing import Any, Callable

from pyrolyze.api import UIElement, call_native, keyed, pyrolyse, use_state

from Studio.app.reducers import (
    bump_refresh_tick,
    create_initial_state,
    select_entry,
    set_active_panel,
    set_root_path,
    set_show_hidden,
    set_status_message,
)
from Studio.app.selectors import panel_options, snapshot_text
from Studio.services.filesystem_service import list_entries, safe_preview
def _as_string(value: Any) -> str:
    return str(value)


@pyrolyse
def section(title: str, *, accent: str = "blue", visible: bool = True) -> None:
    call_native(UIElement)(
        kind="section",
        props={
            "title": title,
            "accent": accent,
            "visible": bool(visible),
        },
    )


@pyrolyse
def row(row_id: str, *, headline: str, visible: bool = True) -> None:
    call_native(UIElement)(
        kind="row",
        props={
            "row_id": row_id,
            "headline": headline,
            "visible": bool(visible),
        },
    )


@pyrolyse
def badge(text: str, *, tone: str = "info", visible: bool = True) -> None:
    call_native(UIElement)(
        kind="badge",
        props={
            "text": text,
            "tone": tone,
            "visible": bool(visible),
        },
    )


@pyrolyse
def button(
    label: str,
    *,
    on_press: Callable[[], None],
    enabled: bool = True,
    tone: str = "default",
    visible: bool = True,
) -> None:
    call_native(UIElement)(
        kind="button",
        props={
            "label": label,
            "enabled": bool(enabled),
            "tone": tone,
            "visible": bool(visible),
            "on_press": on_press,
        },
    )


@pyrolyse
def text_field(
    field_id: str,
    label: str,
    value: str,
    *,
    on_change: Callable[[str], None],
    enabled: bool = True,
    placeholder: str | None = None,
    visible: bool = True,
) -> None:
    call_native(UIElement)(
        kind="text_field",
        props={
            "field_id": field_id,
            "label": label,
            "value": value,
            "enabled": bool(enabled),
            "placeholder": placeholder,
            "visible": bool(visible),
            "on_change": on_change,
        },
    )


@pyrolyse
def toggle(
    field_id: str,
    label: str,
    checked: bool,
    *,
    on_toggle: Callable[[bool], None],
    enabled: bool = True,
    visible: bool = True,
) -> None:
    call_native(UIElement)(
        kind="toggle",
        props={
            "field_id": field_id,
            "label": label,
            "checked": bool(checked),
            "enabled": bool(enabled),
            "visible": bool(visible),
            "on_toggle": on_toggle,
        },
    )


@pyrolyse
def select_field(
    field_id: str,
    label: str,
    value: str,
    *,
    options: tuple[str, ...],
    on_change: Callable[[str], None],
    enabled: bool = True,
    visible: bool = True,
) -> None:
    call_native(UIElement)(
        kind="select_field",
        props={
            "field_id": field_id,
            "label": label,
            "value": value,
            "options": options,
            "enabled": bool(enabled),
            "visible": bool(visible),
            "on_change": on_change,
        },
    )


def _set_status(
    set_state: Callable[[Any], None],
    message: str,
) -> None:
    set_state(lambda current: set_status_message(current, message))


@pyrolyse
def studio_app(start_root: str = "") -> None:
    state, set_state = use_state(create_initial_state(start_root))
    entries = list_entries(state.root_path, show_hidden=state.show_hidden, limit=64)
    has_error = bool(entries) and entries[0]["kind"] == "error"
    entry_count = 0 if has_error else len(entries)
    preview = safe_preview(state.selected_path, max_chars=800) if state.selected_path else "Select a file to preview."
    snapshot = snapshot_text(state, entry_count=entry_count)

    with section("Studio Prototype (architecture-aligned)", accent="blue"):
        with row("studio:controls", headline="Controls"):
            text_field(
                "studio:root-path",
                "Root Path",
                state.root_path,
                on_change=lambda value: set_state(
                    lambda current: set_root_path(current, _as_string(value))
                ),
            )
            button(
                "Refresh",
                tone="success",
                on_press=lambda: set_state(bump_refresh_tick),
            )
            toggle(
                "studio:show-hidden",
                "Show Hidden",
                state.show_hidden,
                on_toggle=lambda checked: set_state(
                    lambda current: set_show_hidden(current, bool(checked))
                ),
            )
            select_field(
                "studio:panel",
                "Panel",
                state.active_panel,
                options=panel_options(),
                on_change=lambda value: set_state(
                    lambda current: set_active_panel(current, _as_string(value))
                ),
            )

        with section("Explorer", accent="cyan"):
            badge(text=f"Root: {state.root_path}", tone="info")
            badge(text=f"Entries: {entry_count}", tone="info")
            if has_error:
                badge(text=f"Explorer error: {entries[0]['name']}", tone="danger")
            elif not entries:
                badge(text="No entries in this directory.", tone="warning")
            else:
                for entry in keyed(entries, key=lambda value: value["key"]):
                    is_dir = bool(entry["is_dir"])
                    entry_key = _as_string(entry["key"])
                    entry_name = _as_string(entry["name"])
                    entry_path = _as_string(entry["path"])
                    with row(f"studio:entry:{entry_key}", headline=entry_name):
                        badge(text="DIR" if is_dir else "FILE", tone="success" if is_dir else "default")
                        button(
                            "Set Root" if is_dir else "Preview",
                            on_press=lambda path=entry_path, child_is_dir=is_dir: set_state(
                                lambda current: select_entry(current, path, is_dir=child_is_dir)
                            ),
                        )

        with section("Editor Preview", accent="green"):
            badge(text=f"Selected: {state.selected_path or '<none>'}", tone="info")
            badge(text=preview, tone="default")

        with section("Bottom Panel", accent="slate"):
            badge(text=f"Active Panel: {state.active_panel}", tone="info")
            if state.active_panel == "Output":
                badge(text="Output stream placeholder.", tone="default")
            elif state.active_panel == "Terminal":
                badge(text="Terminal placeholder.", tone="default")
            else:
                badge(text="Problems placeholder.", tone="default")

        with section("Command Surface (baseline placeholders)", accent="orange"):
            with row("studio:cmd:file", headline="File"):
                button("New", on_press=lambda: _set_status(set_state, "Creating new file..."))
                button("Open File", on_press=lambda: _set_status(set_state, "Opening file..."))
                button("Save", on_press=lambda: _set_status(set_state, "Saving file..."))
            with row("studio:cmd:edit", headline="Edit"):
                button("Undo", on_press=lambda: _set_status(set_state, "Undo not implemented"))
                button("Redo", on_press=lambda: _set_status(set_state, "Redo not implemented"))
                button("Copy", on_press=lambda: _set_status(set_state, "Copy not implemented"))
            with row("studio:cmd:help", headline="Help"):
                button("About", on_press=lambda: _set_status(set_state, "ViewMesh Studio prototype (PyRolyze)"))

        with section("Inspector Snapshot (simulated)", accent="magenta"):
            button(
                "Refresh Snapshot",
                on_press=lambda: set_state(bump_refresh_tick),
            )
            badge(text=snapshot, tone="info")
            badge(text=f"Status: {state.status_message}", tone="info")
