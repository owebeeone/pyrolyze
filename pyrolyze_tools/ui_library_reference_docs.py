"""Generate compressed Markdown reference for discovery-based UI libraries (PySide6, Tkinter).

See ``py-rolyze/docs/reference/Generated_UI_Library_Reference_Doc_Spec.md``.
Dear PyGui uses ``dearpygui_spec_reference_docs`` (spec-driven). Does not emit ``README.md``.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence

from pyrolyze.backends.model import FillPolicy, MethodMode, UiEventLearning

from pyrolyze_tools.generate_semantic_library import (
    DiscoveredMountPoint,
    DiscoveredParameter,
    DiscoveredProperty,
    DiscoveredWidgetClass,
    _assign_kind_names,
    _default_source_props_for_method,
    _infer_default_attach_mount_point_names,
    _infer_default_child_mount_point_name,
    _public_parameters_for_widget,
    _render_getter_kind,
    _render_getter_name,
    _render_prop_mode,
    _render_setter_kind,
    _render_setter_name,
)


@dataclass(frozen=True, slots=True)
class DiscoveryDocProfile:
    """Backend-specific wording and native-binding strings for discovery docs."""

    display_title: str
    doc_slug: str
    author_kwarg_blurb: str
    unmapped_heading: str
    unmapped_intro: str
    event_native_column: str
    machine_toolkit_note: str
    native_prop: Callable[
        [DiscoveredWidgetClass, str, DiscoveredParameter | None, DiscoveredProperty | None],
        str,
    ]
    native_event_glossary: Callable[[DiscoveredWidgetClass, UiEventLearning], str]
    native_event_entity: Callable[[DiscoveredWidgetClass, UiEventLearning], str]
    prop_type_note: Callable[[DiscoveredProperty], str]


def _slug(text: str) -> str:
    s = "".join(c if c.isalnum() else "-" for c in text.lower())
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


def _prop_anchor_id(key: str) -> str:
    return _slug(key)


def _md_link(text: str, path: str, anchor: str | None = None) -> str:
    dest = f"{path}#{anchor}" if anchor else path
    return f"[{text}]({dest})"


def _pyside_prop_type_note(discovered_property: DiscoveredProperty) -> str:
    return f"Qt type `{discovered_property.type_name}`"


def _tk_prop_type_note(discovered_property: DiscoveredProperty) -> str:
    return f"Tk option type `{discovered_property.type_name}`"


def _native_binding_pyside_prop(
    widget: DiscoveredWidgetClass,
    prop_name: str,
    parameter: DiscoveredParameter | None,
    discovered_property: DiscoveredProperty | None,
) -> str:
    cls = widget.class_name
    mod = widget.module_name
    if parameter is not None and discovered_property is None:
        return f"`{mod}.{cls}.__init__(..., {prop_name}=...)`"
    if discovered_property is not None and discovered_property.writable:
        sp = f'`setProperty("{prop_name}", value)`'
        if parameter is not None:
            return f"{sp} (also `{cls}.__init__(..., {prop_name}=...)`)"
        return sp
    if discovered_property is not None:
        return f"read-only Qt meta `{prop_name}` (`{discovered_property.type_name}`)"
    if parameter is not None:
        return f"`{mod}.{cls}.__init__(..., {prop_name}=...)`"
    return "—"


def _native_binding_tk_prop(
    widget: DiscoveredWidgetClass,
    prop_name: str,
    parameter: DiscoveredParameter | None,
    discovered_property: DiscoveredProperty | None,
) -> str:
    cls = widget.class_name
    mod = widget.module_name
    if parameter is not None and discovered_property is None:
        return f"`{mod}.{cls}.__init__(..., {prop_name}=...)`"
    if discovered_property is not None and discovered_property.writable:
        cfg = f"`widget.configure({{{prop_name!r}: value}})`"
        if parameter is not None:
            return f"{cfg} (also `{cls}.__init__(..., {prop_name}=...)`)"
        return cfg
    if discovered_property is not None:
        return f"read-only / internal option `{prop_name}` (`{discovered_property.type_name}`)"
    if parameter is not None:
        return f"`{mod}.{cls}.__init__(..., {prop_name}=...)`"
    return "—"


def _pyside_event_glossary(widget: DiscoveredWidgetClass, elearn: UiEventLearning) -> str:
    return f"`{widget.class_name}.{elearn.signal_name}` (Qt signal)"


def _pyside_event_entity(widget: DiscoveredWidgetClass, elearn: UiEventLearning) -> str:
    return f"`{widget.class_name}.{elearn.signal_name}`"


def _tk_event_glossary(widget: DiscoveredWidgetClass, elearn: UiEventLearning) -> str:
    return f"`{widget.class_name}.bind(...)` / `{elearn.signal_name}` (Tk event sequence or callback name)"


def _tk_event_entity(widget: DiscoveredWidgetClass, elearn: UiEventLearning) -> str:
    return f"`bind` → `{elearn.signal_name}`"


PYSIDE6_DISCOVERY_PROFILE = DiscoveryDocProfile(
    display_title="PySide6",
    doc_slug="pyside6",
    author_kwarg_blurb="passed on the generated `CQ*` call or `mount(...)` selector",
    unmapped_heading="Unmapped native properties",
    unmapped_intro=(
        "Qt `QMetaObject` properties present on discovered classes but **not** exposed as author kwargs "
        "on that emitter (no entry in the generated `CQ*` signature for that widget)."
    ),
    event_native_column="Native (Qt signal)",
    machine_toolkit_note="PySide6",
    native_prop=_native_binding_pyside_prop,
    native_event_glossary=_pyside_event_glossary,
    native_event_entity=_pyside_event_entity,
    prop_type_note=_pyside_prop_type_note,
)

TKINTER_DISCOVERY_PROFILE = DiscoveryDocProfile(
    display_title="Tkinter",
    doc_slug="tkinter",
    author_kwarg_blurb="passed on the generated `C*` call or `mount(...)` selector",
    unmapped_heading="Unmapped native options",
    unmapped_intro=(
        "Tk widget configuration options present on discovered classes but **not** exposed as author kwargs "
        "on that emitter (no entry in the generated `C*` signature for that widget)."
    ),
    event_native_column="Native (Tk bind / callback)",
    machine_toolkit_note="Tkinter",
    native_prop=_native_binding_tk_prop,
    native_event_glossary=_tk_event_glossary,
    native_event_entity=_tk_event_entity,
    prop_type_note=_tk_prop_type_note,
)


def _iter_mapped_prop_rows(
    package_name: str,
    widget: DiscoveredWidgetClass,
    profile: DiscoveryDocProfile,
) -> list[tuple[str, str, str, str, str, str]]:
    rows: list[tuple[str, str, str, str, str, str]] = []
    constructor_params = {parameter.name: parameter for parameter in widget.parameters}
    properties = {prop.name: prop for prop in widget.properties}
    prop_names = tuple(dict.fromkeys([*constructor_params, *properties]))
    for prop_name in prop_names:
        learning = widget.prop_learnings.get(prop_name)
        if learning is not None and learning.public is False:
            continue
        parameter = constructor_params.get(prop_name)
        discovered_property = properties.get(prop_name)
        mode = _render_prop_mode(parameter is not None, discovered_property)
        sk = _render_setter_kind(package_name, discovered_property)
        sn = _render_setter_name(package_name, discovered_property)
        gk = _render_getter_kind(package_name, discovered_property)
        gn = _render_getter_name(package_name, discovered_property)
        notes: list[str] = []
        if parameter is not None:
            notes.append("constructor")
        if discovered_property is not None:
            notes.append(profile.prop_type_note(discovered_property))
        if gk != "None":
            notes.append(f"read: {gk} {gn}")
        native = profile.native_prop(widget, prop_name, parameter, discovered_property)
        rows.append(
            (
                prop_name,
                mode,
                sk,
                sn,
                "; ".join(notes) if notes else "—",
                native,
            )
        )
    return rows


def _method_row_infos(
    package_name: str,
    widget: DiscoveredWidgetClass,
) -> list[tuple[str, str, tuple[str, ...], str, str]]:
    out: list[tuple[str, str, tuple[str, ...], str, str]] = []
    for method in widget.setter_methods:
        learning = widget.method_learnings.get(method.name)
        source_props = (
            learning.source_props
            if learning is not None and learning.source_props is not None
            else _default_source_props_for_method(package_name, widget, method)
        )
        mode = (
            learning.mode
            if learning is not None and learning.mode is not None
            else MethodMode.CREATE_UPDATE
        )
        fill = (
            learning.fill_policy
            if learning is not None and learning.fill_policy is not None
            else FillPolicy.RETAIN_EFFECTIVE
        )
        native = f"{widget.module_name}.{widget.class_name}.{method.name}(…)"
        out.append(
            (method.name, f"MethodMode.{mode.name}", source_props, f"FillPolicy.{fill.name}", native)
        )
    return out


def _method_rows(package_name: str, widget: DiscoveredWidgetClass) -> list[tuple[str, str, str, str, str]]:
    return [
        (m, mode, ", ".join(sps), fill, native)
        for m, mode, sps, fill, native in _method_row_infos(package_name, widget)
    ]


def _mount_rows(widget: DiscoveredWidgetClass) -> list[DiscoveredMountPoint]:
    return list(widget.mount_points)


def _collect_author_visible_names(package_name: str, widget: DiscoveredWidgetClass) -> set[str]:
    return {p.name for p in _public_parameters_for_widget(package_name, widget)}


def _native_for_method(widget: DiscoveredWidgetClass, method_name: str) -> str:
    return f"`{widget.module_name}.{widget.class_name}.{method_name}(…)`"


def _native_for_mount(mp: DiscoveredMountPoint) -> str:
    parts = [x for x in (mp.apply_method_name, mp.append_method_name, mp.place_method_name) if x]
    if parts:
        return ", ".join(f"`{p}(…)`" for p in parts)
    return "—"


def _collect_property_glossary(
    package_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
    profile: DiscoveryDocProfile,
) -> tuple[dict[str, list[tuple[str, str, str, str, str, str]]], dict[str, list[str]]]:
    by_prop: dict[str, list[tuple[str, str, str, str, str, str]]] = defaultdict(list)
    usage: dict[str, list[str]] = defaultdict(list)

    for widget in widgets:
        emitter = widget.public_name
        e_anchor = _slug(emitter)
        emitter_link = _md_link(emitter, "entities.md", f"entity-{e_anchor}")

        prop_table_names = {row[0] for row in _iter_mapped_prop_rows(package_name, widget, profile)}
        for row in _iter_mapped_prop_rows(package_name, widget, profile):
            name, mode, sk, sn, notes, native = row
            by_prop[name].append((emitter, name, mode, sk, native, f"setter API `{sn}`; {notes}"))
            usage[name].append(emitter_link)

        for mname, mode_str, source_props, fill_str, native_call in _method_row_infos(package_name, widget):
            native_m = _native_for_method(widget, mname)
            for sp in source_props:
                if sp in prop_table_names:
                    continue
                by_prop[sp].append(
                    (
                        emitter,
                        sp,
                        mode_str,
                        "native method",
                        native_m,
                        f"author `{sp}` → `{native_call}`; `{fill_str}`",
                    )
                )
                usage[sp].append(emitter_link)

        for event_name in sorted(widget.event_learnings):
            elearn = widget.event_learnings[event_name]
            native_sig = profile.native_event_glossary(widget, elearn)
            by_prop[event_name].append(
                (
                    emitter,
                    event_name,
                    "event (handler kwarg)",
                    "signal",
                    native_sig,
                    f"`EventPayloadPolicy.{elearn.payload_policy.name}`",
                )
            )
            usage[event_name].append(emitter_link)

        for mp in widget.mount_points:
            for param in mp.params:
                pname = param.name
                native_mount = _native_for_mount(mp)
                by_prop[pname].append(
                    (
                        emitter,
                        pname,
                        "mount selector kwarg",
                        f"mount `{mp.name}`",
                        native_mount,
                        f"param `{param.name}`; child `{mp.accepted_type_name}`",
                    )
                )
                usage[pname].append(emitter_link)

    return dict(by_prop), {k: sorted(set(v)) for k, v in usage.items()}


def _unmapped_discovery_properties(
    package_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
) -> dict[str, list[str]]:
    """Native option/property names on classes that are not author-visible for that emitter."""
    out: dict[str, list[str]] = defaultdict(list)
    if package_name not in {"PySide6", "tkinter"}:
        return {}
    for widget in widgets:
        visible = _collect_author_visible_names(package_name, widget)
        for prop in widget.properties:
            if prop.name not in visible:
                out[prop.name].append(f"{widget.public_name} (`{widget.class_name}`)")
    return {k: sorted(set(v)) for k, v in sorted(out.items())}


def write_discovery_reference_docs(
    root_module_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
    out_dir: Path,
    profile: DiscoveryDocProfile,
) -> tuple[Path, Path]:
    package_name = root_module_name.split(".", 1)[0]
    if profile.doc_slug == "pyside6" and package_name != "PySide6":
        raise ValueError(f"expected PySide6 module root, got {root_module_name!r}")
    if profile.doc_slug == "tkinter" and package_name != "tkinter":
        raise ValueError(f"expected tkinter module root, got {root_module_name!r}")

    out_dir.mkdir(parents=True, exist_ok=True)
    kind_names = _assign_kind_names(root_module_name, widgets)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    glossary, usage = _collect_property_glossary(package_name, widgets, profile)
    unmapped = _unmapped_discovery_properties(package_name, widgets)

    prop_lines = [
        f"# {profile.display_title} generated library — properties reference",
        "",
        f"Machine-generated from `pyrolyze_tools/generate_semantic_library.py --gen-docs` ({profile.machine_toolkit_note}).",
        "PyRolyze applies **one-way** updates; this lists outbound mapping only.",
        "",
        f"*Generated {stamp}*",
        "",
        "## Mapped fields (TOC)",
        "",
    ]
    for key in sorted(glossary):
        prop_lines.append(f"- {_md_link(f'`{key}`', 'properties.md', f'prop-{_prop_anchor_id(key)}')}")

    prop_lines.extend(["", "## Mapped fields (detail)", ""])

    for key in sorted(glossary):
        pid = _prop_anchor_id(key)
        prop_lines.append(f'<a id="prop-{pid}"></a>')
        prop_lines.append(f"## `{key}`")
        prop_lines.append("")
        prop_lines.append(f"**Author kwarg:** `{key}` ({profile.author_kwarg_blurb}).")
        prop_lines.append("")
        prop_lines.append("**Used by:** " + ", ".join(usage.get(key, [])))
        prop_lines.append("")
        prop_lines.append(
            "| Emitter | Author kwarg | Native setter / binding | Mode | Setter kind | Notes |"
        )
        prop_lines.append("|----------|--------------|-------------------------|------|-------------|-------|")
        for emitter, kw, mode, sk, native, notes in sorted(glossary[key], key=lambda r: r[0]):
            prop_lines.append(f"| `{emitter}` | `{kw}` | {native} | `{mode}` | `{sk}` | {notes} |")
        prop_lines.append("")

    prop_lines.extend(
        [
            f"## {profile.unmapped_heading}",
            "",
            profile.unmapped_intro,
            "",
        ]
    )
    if unmapped:
        prop_lines.append("| Native name | Where it exists (not exposed) |")
        prop_lines.append("|-------------|--------------------------------|")
        for name, where in unmapped.items():
            prop_lines.append(f"| `{name}` | {', '.join(where)} |")
        prop_lines.append("")
    else:
        prop_lines.append("*None detected for this extraction.*")
        prop_lines.append("")

    prop_lines.extend(
        [
            "## Unmapped native types",
            "",
            "*Not auto-generated.* Types with no generated emitter are maintained manually if needed.",
            "",
        ]
    )

    prop_path = out_dir / "properties.md"
    prop_path.write_text("\n".join(prop_lines), encoding="utf-8")

    ent_lines = [
        f"# {profile.display_title} generated library — entities (emitters)",
        "",
        "Machine-generated. See [properties.md](properties.md) for field glossary and unmapped native surface.",
        "",
        f"*Generated {stamp}*",
        "",
        "## Index",
        "",
        "| Emitter | Kind | Mounted type |",
        "|---------|------|--------------|",
    ]
    for widget in sorted(widgets, key=lambda w: w.public_name):
        kind = kind_names[(widget.module_name, widget.class_name)]
        mounted = f"{widget.module_name}.{widget.class_name}"
        slug = _slug(widget.public_name)
        ent_lines.append(
            f"| {_md_link(f'`{widget.public_name}`', 'entities.md', f'entity-{slug}')} | `{kind}` | `{mounted}` |"
        )

    for widget in sorted(widgets, key=lambda w: w.public_name):
        kind = kind_names[(widget.module_name, widget.class_name)]
        mounted = f"{widget.module_name}.{widget.class_name}"
        slug = _slug(widget.public_name)
        ent_lines.append("")
        ent_lines.append(f'<a id="entity-{slug}"></a>')
        ent_lines.append(f"## `{widget.public_name}`")
        ent_lines.append("")
        ent_lines.append(f"- **Kind:** `{kind}`")
        ent_lines.append(f"- **Mounted type:** `{mounted}`")
        ent_lines.append(f"- **Child policy:** `ChildPolicy.NONE` (generated)")
        ent_lines.append("")

        ent_lines.append("### Author kwargs → native binding (props & constructor)")
        ent_lines.append("")
        prop_table_names = {r[0] for r in _iter_mapped_prop_rows(package_name, widget, profile)}
        ent_lines.append("| Author kwarg | Native setter / binding | Mode | Setter kind | Notes |")
        ent_lines.append("|--------------|-------------------------|------|-------------|-------|")
        for name, mode, sk, sn, notes, native in _iter_mapped_prop_rows(package_name, widget, profile):
            plink = _md_link(f"`{name}`", "properties.md", f"prop-{_prop_anchor_id(name)}")
            ent_lines.append(f"| {plink} | {native} | `{mode}` | `{sk}` | setter API `{sn}`; {notes} |")
        for mname, mode_str, source_props, fill_str, native_call in _method_row_infos(package_name, widget):
            native_m = _native_for_method(widget, mname)
            for sp in source_props:
                if sp in prop_table_names:
                    continue
                plink = _md_link(f"`{sp}`", "properties.md", f"prop-{_prop_anchor_id(sp)}")
                ent_lines.append(
                    f"| {plink} | {native_m} | `{mode_str}` | native method | "
                    f"author `{sp}` → `{native_call}`; `{fill_str}` |"
                )
        ent_lines.append("")

        ev_rows = list(widget.event_learnings.items())
        if ev_rows:
            ent_lines.append("### Events (handler kwargs)")
            ent_lines.append("")
            ent_lines.append(f"| Author kwarg | {profile.event_native_column} | Payload |")
            ent_lines.append("|--------------|-------------------|---------|")
            for ename, elearn in sorted(ev_rows, key=lambda x: x[0]):
                pl = _md_link(f"`{ename}`", "properties.md", f"prop-{_prop_anchor_id(ename)}")
                native_cell = profile.native_event_entity(widget, elearn)
                ent_lines.append(
                    f"| {pl} | {native_cell} | `EventPayloadPolicy.{elearn.payload_policy.name}` |"
                )
            ent_lines.append("")

        mrows = _method_rows(package_name, widget)
        if mrows:
            ent_lines.append("### Methods (native setters wrapped)")
            ent_lines.append("")
            ent_lines.append("| Method | Mode | Source props | Fill | Native |")
            ent_lines.append("|--------|------|--------------|------|--------|")
            for name, mode, props, fill, native in mrows:
                ent_lines.append(f"| `{name}` | `{mode}` | `{props}` | `{fill}` | `{native}` |")
            ent_lines.append("")

        mounts = _mount_rows(widget)
        if mounts:
            ent_lines.append("### Mount points")
            ent_lines.append("")
            ent_lines.append(
                "| Name | Accepts | Params | apply | append | place | detach | sync | replay | prefer_sync |"
            )
            ent_lines.append(
                "|------|---------|--------|-------|--------|-------|--------|------|--------|-------------|"
            )
            for mp in sorted(mounts, key=lambda m: m.name):
                params = ", ".join(
                    f"`{p.name}`{' (keyed)' if p.name in mp.keyed_param_names else ''}" for p in mp.params
                )
                ent_lines.append(
                    f"| `{mp.name}` | `{mp.accepted_type_name}` | {params or '—'} | "
                    f"{mp.apply_method_name or '—'} | {mp.append_method_name or '—'} | "
                    f"{mp.place_method_name or '—'} | {mp.detach_method_name or '—'} | "
                    f"{mp.sync_method_name or '—'} | `{mp.replay_kind.name}` | `{mp.prefer_sync}` |"
                )
            ent_lines.append("")

        default_child = _infer_default_child_mount_point_name(package_name, mounts)
        default_attach = _infer_default_attach_mount_point_names(package_name, mounts)
        ent_lines.append("### Default child attachment")
        ent_lines.append("")
        ent_lines.append(f"- `default_child_mount_point_name`: `{default_child!r}`")
        ent_lines.append(f"- `default_attach_mount_point_names`: `{default_attach!r}`")
        ent_lines.append("")

    ent_path = out_dir / "entities.md"
    ent_path.write_text("\n".join(ent_lines), encoding="utf-8")

    return ent_path, prop_path


def write_pyside6_reference_docs(
    root_module_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
    out_dir: Path,
) -> tuple[Path, Path]:
    return write_discovery_reference_docs(
        root_module_name, widgets, out_dir, PYSIDE6_DISCOVERY_PROFILE
    )


def write_tkinter_reference_docs(
    root_module_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
    out_dir: Path,
) -> tuple[Path, Path]:
    return write_discovery_reference_docs(
        root_module_name, widgets, out_dir, TKINTER_DISCOVERY_PROFILE
    )


__all__ = [
    "DiscoveryDocProfile",
    "PYSIDE6_DISCOVERY_PROFILE",
    "TKINTER_DISCOVERY_PROFILE",
    "write_discovery_reference_docs",
    "write_pyside6_reference_docs",
    "write_tkinter_reference_docs",
]
