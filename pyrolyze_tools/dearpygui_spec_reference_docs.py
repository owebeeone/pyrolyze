"""Generate entities.md + properties.md from ``DearPyGuiUiLibrary.WIDGET_SPECS``."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from pyrolyze.backends.model import (
    AccessorKind,
    MountPointSpec,
    PropMode,
    UiEventSpec,
    UiParamSpec,
    UiPropSpec,
    UiWidgetSpec,
)


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


def _dpg_author_helper(kind: str) -> str:
    try:
        from pyrolyze.backends.dearpygui.author_ui import DearPyGuiC
    except Exception:
        return "—"
    if not kind.startswith("Dpg"):
        return "—"
    tail = kind[3:]
    if tail and callable(getattr(DearPyGuiC, tail, None)):
        return f"`DearPyGuiUiLibrary.C.{tail}`"
    return "—"


def _native_dpg_prop(prop_name: str, p: UiPropSpec) -> str:
    sk = p.setter_kind
    if sk is AccessorKind.DPG_CONFIG:
        key = p.setter_name or prop_name
        return f"`dpg.configure(item, {key}=...)`"
    if sk is AccessorKind.DPG_VALUE:
        key = p.setter_name or prop_name
        return f"`dpg.set_value(...)` / value slot `{key}`"
    if sk is AccessorKind.METHOD and p.setter_name:
        return f"`{p.setter_name}(…)`"
    if p.setter_name:
        return f"`{sk}` / `{p.setter_name}`" if sk else f"`{p.setter_name}`"
    return f"`{sk}`" if sk else "—"


def _native_dpg_ctor_param(name: str, _p: UiParamSpec) -> str:
    return f"`DearPyGui` factory / item ctor `{name}=...`"


def _native_dpg_event(_kind: str, ev: UiEventSpec) -> str:
    return f"`dpg.configure(item, callback=...)` / `{ev.signal_name}`"


def _native_dpg_mount(mp: MountPointSpec) -> str:
    parts = [x for x in (mp.apply_method_name, mp.append_method_name, mp.place_method_name) if x]
    if parts:
        return ", ".join(f"`{p}(…)`" for p in parts)
    if mp.sync_method_name:
        return f"`{mp.sync_method_name}(…)`"
    return "—"


def _collect_glossary_from_specs(
    specs: Mapping[str, UiWidgetSpec],
) -> dict[str, list[tuple[str, str, str, str, str, str]]]:
    """kwarg -> rows (emitter_kind, kw, mode, sk, native, notes)."""
    by_prop: dict[str, list[tuple[str, str, str, str, str, str]]] = defaultdict(list)

    for kind in sorted(specs):
        spec = specs[kind]
        for pname, param in spec.constructor_params.items():
            mode = "constructor"
            sk = "ctor"
            native = _native_dpg_ctor_param(pname, param)
            notes = f"annotation `{param.annotation.expr if param.annotation else '—'}`"
            by_prop[pname].append((kind, pname, mode, sk, native, notes))

        for pname, p in spec.props.items():
            mode = f"PropMode.{p.mode.name}"
            sk = f"AccessorKind.{p.setter_kind.name}" if p.setter_kind else "—"
            native = _native_dpg_prop(pname, p)
            notes = f"setter API `{p.setter_name}`; ctor field `{p.constructor_name}`"
            by_prop[pname].append((kind, pname, mode, sk, native, notes))

        for ename, ev in spec.events.items():
            by_prop[ename].append(
                (
                    kind,
                    ename,
                    "event (handler kwarg)",
                    "callback",
                    _native_dpg_event(kind, ev),
                    f"signal `{ev.signal_name}`; `EventPayloadPolicy.{ev.payload_policy.name}`",
                )
            )

        for mp in spec.mount_points.values():
            for mparam in mp.params:
                key = mparam.name
                by_prop[key].append(
                    (
                        kind,
                        key,
                        "mount selector kwarg",
                        f"mount `{mp.name}`",
                        _native_dpg_mount(mp),
                        f"child `{mp.accepted_produced_type.expr}`",
                    )
                )

    return dict(by_prop)


def write_dearpygui_reference_docs(
    out_dir: Path,
    *,
    specs: Mapping[str, UiWidgetSpec] | None = None,
) -> tuple[Path, Path]:
    if specs is None:
        from pyrolyze.backends.dearpygui.generated_library import DearPyGuiUiLibrary

        resolved = DearPyGuiUiLibrary.WIDGET_SPECS
    else:
        resolved = specs
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    glossary = _collect_glossary_from_specs(resolved)

    usage: dict[str, list[str]] = defaultdict(list)
    for kw, rows in glossary.items():
        seen: set[str] = set()
        for kind, *_ in rows:
            if kind in seen:
                continue
            seen.add(kind)
            usage[kw].append(_md_link(f"`{kind}`", "entities.md", f"entity-{_slug(kind)}"))

    prop_lines = [
        "# Dear PyGui generated library — properties reference",
        "",
        "Machine-generated from `pyrolyze_tools/generate_dearpygui_library.py --gen-docs`.",
        "PyRolyze applies **one-way** updates; mapping is via `dpg.configure` / item factories.",
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
        prop_lines.append(
            "**Author kwarg:** `{0}` (passed on `DearPyGuiUiLibrary.C.*` emitters or `mount(...)`).".format(
                key
            )
        )
        prop_lines.append("")
        prop_lines.append("**Used by:** " + ", ".join(sorted(usage.get(key, []))))
        prop_lines.append("")
        prop_lines.append(
            "| Emitter (kind) | Author kwarg | Native setter / binding | Mode | Setter kind | Notes |"
        )
        prop_lines.append(
            "|------------------|--------------|-------------------------|------|-------------|-------|"
        )
        for kind, kw, mode, sk, native, notes in sorted(glossary[key], key=lambda r: r[0]):
            prop_lines.append(f"| `{kind}` | `{kw}` | {native} | `{mode}` | `{sk}` | {notes} |")
        prop_lines.append("")

    prop_lines.extend(
        [
            "## Unmapped native Dear PyGui surface",
            "",
            "*Not auto-generated.* Compare manually against `dearpygui` API if needed.",
            "",
            "## Unmapped native types",
            "",
            "*Not auto-generated.*",
            "",
        ]
    )

    prop_path = out_dir / "properties.md"
    prop_path.write_text("\n".join(prop_lines), encoding="utf-8")

    ent_lines = [
        "# Dear PyGui generated library — entities (kinds)",
        "",
        "Machine-generated from `DearPyGuiUiLibrary.WIDGET_SPECS`. See [properties.md](properties.md).",
        "",
        f"*Generated {stamp}*",
        "",
        "## Index",
        "",
        "| Kind | Author helper | Mounted type | Child policy |",
        "|------|---------------|--------------|--------------|",
    ]
    for kind in sorted(resolved):
        spec = resolved[kind]
        helper = _dpg_author_helper(kind)
        ent_lines.append(
            f"| {_md_link(f'`{kind}`', 'entities.md', f'entity-{_slug(kind)}')} | {helper} | "
            f"`{spec.mounted_type_name}` | `ChildPolicy.{spec.child_policy.name}` |"
        )

    for kind in sorted(resolved):
        spec = resolved[kind]
        slug = _slug(kind)
        ent_lines.append("")
        ent_lines.append(f'<a id="entity-{slug}"></a>')
        ent_lines.append(f"## `{kind}`")
        ent_lines.append("")
        ent_lines.append(f"- **Author helper:** {_dpg_author_helper(kind)}")
        ent_lines.append(f"- **Mounted type:** `{spec.mounted_type_name}`")
        ent_lines.append(f"- **Child policy:** `ChildPolicy.{spec.child_policy.name}`")
        ent_lines.append("")

        ent_lines.append("### Constructor / factory parameters")
        ent_lines.append("")
        ent_lines.append("| Author kwarg | Native binding | Notes |")
        ent_lines.append("|--------------|----------------|-------|")
        for pname in sorted(spec.constructor_params):
            param = spec.constructor_params[pname]
            native = _native_dpg_ctor_param(pname, param)
            ann = param.annotation.expr if param.annotation else "—"
            pl = _md_link(f"`{pname}`", "properties.md", f"prop-{_prop_anchor_id(pname)}")
            ent_lines.append(f"| {pl} | {native} | `{ann}` |")
        if not spec.constructor_params:
            ent_lines.append("| — | — | *none in spec* |")
        ent_lines.append("")

        ent_lines.append("### Item properties (`dpg.configure`)")
        ent_lines.append("")
        ent_lines.append("| Author kwarg | Native binding | Mode | Setter kind | Notes |")
        ent_lines.append("|--------------|----------------|------|-------------|-------|")
        for pname in sorted(spec.props):
            p = spec.props[pname]
            native = _native_dpg_prop(pname, p)
            pl = _md_link(f"`{pname}`", "properties.md", f"prop-{_prop_anchor_id(pname)}")
            notes = f"setter `{p.setter_name}`"
            sk_cell = f"`AccessorKind.{p.setter_kind.name}`" if p.setter_kind else "—"
            ent_lines.append(
                f"| {pl} | {native} | `PropMode.{p.mode.name}` | "
                f"{sk_cell} | {notes} |"
            )
        if not spec.props:
            ent_lines.append("| — | — | — | — | *none* |")
        ent_lines.append("")

        if spec.events:
            ent_lines.append("### Events (handler kwargs)")
            ent_lines.append("")
            ent_lines.append("| Author kwarg | Native (Dear PyGui callback) | Payload |")
            ent_lines.append("|--------------|------------------------------|---------|")
            for ename in sorted(spec.events):
                ev = spec.events[ename]
                pl = _md_link(f"`{ename}`", "properties.md", f"prop-{_prop_anchor_id(ename)}")
                ent_lines.append(
                    f"| {pl} | {_native_dpg_event(kind, ev)} | `EventPayloadPolicy.{ev.payload_policy.name}` |"
                )
            ent_lines.append("")

        if spec.mount_points:
            ent_lines.append("### Mount points")
            ent_lines.append("")
            ent_lines.append(
                "| Name | Accepts | Params | apply | append | place | detach | sync | replay | prefer_sync |"
            )
            ent_lines.append(
                "|------|---------|--------|-------|--------|-------|--------|------|--------|-------------|"
            )
            for mp in sorted(spec.mount_points.values(), key=lambda m: m.name):
                params = ", ".join(
                    f"`{p.name}`{' (keyed)' if p.keyed else ''}" for p in mp.params
                )
                ent_lines.append(
                    f"| `{mp.name}` | `{mp.accepted_produced_type.expr}` | {params or '—'} | "
                    f"{mp.apply_method_name or '—'} | {mp.append_method_name or '—'} | "
                    f"{mp.place_method_name or '—'} | {mp.detach_method_name or '—'} | "
                    f"{mp.sync_method_name or '—'} | `{mp.replay_kind.name}` | `{mp.prefer_sync}` |"
                )
            ent_lines.append("")

        ent_lines.append("### Default child attachment")
        ent_lines.append("")
        ent_lines.append(f"- `default_child_mount_point_name`: `{spec.default_child_mount_point_name!r}`")
        ent_lines.append(
            f"- `default_attach_mount_point_names`: `{spec.default_attach_mount_point_names!r}`"
        )
        ent_lines.append("")

    ent_path = out_dir / "entities.md"
    ent_path.write_text("\n".join(ent_lines), encoding="utf-8")

    return ent_path, prop_path


__all__ = ["write_dearpygui_reference_docs"]
