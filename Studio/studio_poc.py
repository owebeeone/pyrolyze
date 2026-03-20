#@pyrolyze
from typing import Any, Callable

from pyrolyze.api import UIElement, call_native, keyed, pyrolyse, use_state

from Studio.studio_logic import build_snapshot_text, list_entries, normalize_root_path, safe_preview


def _as_string(value: Any) -> str:
    return str(value)


def _select_entry(
    path: str,
    is_dir: bool,
    set_root_path: Callable[[str | Callable[[str], str]], None],
    set_selected_path: Callable[[str | Callable[[str], str]], None],
) -> None:
    if is_dir:
        set_root_path(normalize_root_path(path))
        set_selected_path("")
        return
    set_selected_path(path)


@pyrolyse
def section(title: str, *, accent: str = "blue") -> None:
    call_native(UIElement)(
        kind="section",
        props={
            "title": title,
            "accent": accent,
            "visible": True,
        },
    )


@pyrolyse
def row(row_id: str, *, headline: str) -> None:
    call_native(UIElement)(
        kind="row",
        props={
            "row_id": row_id,
            "headline": headline,
            "visible": True,
        },
    )


@pyrolyse
def badge(text: str, *, tone: str = "info") -> None:
    call_native(UIElement)(
        kind="badge",
        props={
            "text": text,
            "tone": tone,
            "visible": True,
        },
    )


@pyrolyse
def button(
    label: str,
    *,
    on_press: Callable[[], None],
    enabled: bool = True,
    tone: str = "default",
) -> None:
    call_native(UIElement)(
        kind="button",
        props={
            "label": label,
            "enabled": enabled,
            "tone": tone,
            "visible": True,
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
) -> None:
    call_native(UIElement)(
        kind="text_field",
        props={
            "field_id": field_id,
            "label": label,
            "value": value,
            "enabled": enabled,
            "placeholder": None,
            "visible": True,
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
) -> None:
    call_native(UIElement)(
        kind="toggle",
        props={
            "field_id": field_id,
            "label": label,
            "checked": checked,
            "enabled": enabled,
            "visible": True,
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
) -> None:
    call_native(UIElement)(
        kind="select_field",
        props={
            "field_id": field_id,
            "label": label,
            "value": value,
            "options": options,
            "enabled": enabled,
            "visible": True,
            "on_change": on_change,
        },
    )


@pyrolyse
def studio_poc_app(start_root: str = "") -> None:
    root_path, set_root_path = use_state(normalize_root_path(start_root))
    selected_path, set_selected_path = use_state("")
    show_hidden, set_show_hidden = use_state(False)
    active_panel, set_active_panel = use_state("Output")
    refresh_tick, set_refresh_tick = use_state(0)

    entries = list_entries(root_path, show_hidden=show_hidden, limit=32)
    has_error = bool(entries) and entries[0]["kind"] == "error"
    entry_count = 0 if has_error else len(entries)
    preview = safe_preview(selected_path, max_chars=800) if selected_path else "Select a file to preview."
    snapshot_text = build_snapshot_text(
        root_path=root_path,
        entry_count=entry_count,
        selected_path=selected_path,
        active_panel=active_panel,
        refresh_tick=int(refresh_tick),
    )

    with section("Studio Prototype (PyRolyze as-is)", accent="blue"):
        with row("studio:controls", headline="Controls"):
            text_field(
                "studio:root-path",
                "Root Path",
                root_path,
                on_change=lambda value: set_root_path(normalize_root_path(value)),
            )
            button(
                "Refresh",
                on_press=lambda: set_refresh_tick(lambda current: int(current) + 1),
                tone="success",
            )
            toggle(
                "studio:show-hidden",
                "Show Hidden",
                show_hidden,
                on_toggle=lambda checked: set_show_hidden(checked),
            )
            select_field(
                "studio:panel",
                "Panel",
                active_panel,
                options=("Output", "Terminal", "Problems"),
                on_change=lambda next_value: set_active_panel(_as_string(next_value)),
            )

        with section("Explorer (simulated via rows)", accent="cyan"):
            badge(text=f"Root: {root_path}", tone="info")
            badge(text=f"Entries: {entry_count}", tone="info")
            if has_error:
                badge(text=f"Explorer error: {entries[0]['name']}", tone="danger")
            elif not entries:
                badge(text="No entries in this directory.", tone="warning")
            else:
                for entry in keyed(entries, key=lambda value: value["key"]):
                    is_dir = bool(entry["is_dir"])
                    with row(f"studio:entry:{entry['key']}", headline=_as_string(entry["name"])):
                        badge(text="DIR" if is_dir else "FILE", tone="success" if is_dir else "default")
                        button(
                            "Set Root" if is_dir else "Preview",
                            on_press=lambda path=_as_string(entry["path"]), child_is_dir=is_dir: _select_entry(
                                path,
                                child_is_dir,
                                set_root_path,
                                set_selected_path,
                            ),
                        )

        with section("Editor Preview (simulated)", accent="green"):
            badge(text=f"Selected: {selected_path or '<none>'}", tone="info")
            badge(text=preview, tone="default")

        with section("Bottom Panel (simulated)", accent="slate"):
            badge(text=f"Active Panel: {active_panel}", tone="info")
            if active_panel == "Output":
                badge(text="Output stream placeholder.", tone="default")
            elif active_panel == "Terminal":
                badge(text="Terminal placeholder.", tone="default")
            else:
                badge(text="Problems placeholder.", tone="default")

        with section("Inspector Snapshot (simulated)", accent="orange"):
            button(
                "Refresh Snapshot",
                on_press=lambda: set_refresh_tick(lambda current: int(current) + 1),
            )
            badge(text=snapshot_text, tone="info")
