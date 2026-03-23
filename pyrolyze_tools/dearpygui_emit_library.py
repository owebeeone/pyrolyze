"""Emit ``generated_library.py`` for the DearPyGui backend (``DearPyGuiUiLibrary``)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from frozendict import frozendict

from pyrolyze.backends.dearpygui.author_shape import shape_canonical_mountable, widget_learning_for_kind
from pyrolyze.backends.dearpygui.discovery import (
    DpgCanonicalMountable,
    DpgLoadedDump,
    iter_canonical_mountables,
    load_dearpygui_dump,
)
from pyrolyze.backends.dearpygui.learnings import KINDS_DEFAULT_VALUE_AS_VALUE
from pyrolyze.backends.model import (
    AccessorKind,
    ChildPolicy,
    MountPointSpec,
    MountReplayKind,
    PropMode,
    TypeRef,
    UiEventSpec,
    UiMountPointLearning,
    UiParamSpec,
    UiPropSpec,
    UiWidgetLearning,
    UiWidgetSpec,
)

ITEMS = "pyrolyze.backends.dearpygui.items"
GEN_MOD = "pyrolyze.backends.dearpygui.generated_library"

# Hand-authored mountable classes (factory coverage); everything else uses M_<factory>.
HAND_MOUNTED: dict[str, str] = {
    "DpgButton": f"{ITEMS}.DpgButtonItem",
    "DpgInputText": f"{ITEMS}.DpgInputTextItem",
    "DpgMenu": f"{ITEMS}.DpgMenuItem",
    "DpgMenuBar": f"{ITEMS}.DpgMenuBarItem",
    "DpgTable": f"{ITEMS}.DpgTableItem",
    "DpgPlot": f"{ITEMS}.DpgPlotItem",
    "DpgNode": f"{ITEMS}.DpgNodeItem",
    "DpgNodeLink": f"{ITEMS}.DpgNodeLinkItem",
    "DpgThemeComponent": f"{ITEMS}.DpgThemeComponentItem",
    "DpgTheme": f"{ITEMS}.DpgThemeItem",
    "DpgFontRegistry": f"{ITEMS}.DpgFontRegistryItem",
    "DpgWindow": f"{ITEMS}.DpgWindowItem",
    "DpgTableColumn": f"{ITEMS}.DpgTableColumnItem",
    "DpgTableRow": f"{ITEMS}.DpgTableRowItem",
    "DpgPlotAxis": f"{ITEMS}.DpgPlotAxisItem",
    "DpgNodeEditor": f"{ITEMS}.DpgNodeEditorItem",
}

# (DearPyGui kind_name, mount_point_name) -> (sync_method, apply_method, max_children)
MOUNT_OPS: dict[tuple[str, str], tuple[str | None, str | None, int | None]] = {
    ("Window", "menu_bar"): (None, "attach_menu_bar", 1),
    ("Window", "standard"): ("sync_children", None, None),
    ("Table", "column"): ("sync_column_children", None, None),
    ("Table", "row"): ("sync_row_children", None, None),
    ("Plot", "axis"): ("sync_axis_children", None, None),
    ("NodeEditor", "node"): ("sync_nodes", None, None),
    ("NodeEditor", "link"): ("sync_links", None, None),
    ("MenuBar", "standard"): ("sync_children", None, None),
    ("Menu", "standard"): ("sync_children", None, None),
    ("TableRow", "cell"): ("sync_cells", None, None),
    ("Theme", "component"): ("sync_component_children", None, None),
    ("ThemeComponent", "entry"): ("sync_entry_children", None, None),
    ("FontRegistry", "standard"): ("sync_registry_children", None, None),
    ("Node", "standard"): ("sync_children", None, None),
}


def ui_kind_name(public_kind_name: str) -> str:
    if public_kind_name.startswith("Dpg"):
        return public_kind_name
    return f"Dpg{public_kind_name}"


def _duplicate_kind_names(items: tuple[DpgCanonicalMountable, ...]) -> frozenset[str]:
    counts: dict[str, int] = {}
    for it in items:
        counts[it.kind_name] = counts.get(it.kind_name, 0) + 1
    return frozenset(k for k, n in counts.items() if n > 1)


def ui_kind_for_item(item: DpgCanonicalMountable, dup_kinds: frozenset[str]) -> str:
    """Stable UI kind; ``draw_*`` twins that share an ``add_*`` kind get a ``DrawCmd`` suffix."""

    shaped = shape_canonical_mountable(item)
    base = ui_kind_name(shaped.public_kind_name)
    if item.kind_name not in dup_kinds:
        return base
    if item.factory_name.startswith("add_"):
        return base
    return f"{base}DrawCmd"


def _norm_annotation(raw: str | None) -> str:
    if raw is None or not raw.strip():
        return "Any"
    ann = raw.strip()
    if ann in {"int", "str", "float", "bool", "Any"}:
        return ann
    if ann == "<class 'str'>":
        return "str"
    if ann == "<class 'int'>":
        return "int"
    if ann == "<class 'float'>":
        return "float"
    if ann == "<class 'bool'>":
        return "bool"
    return "Any"


def _resolve_accepted_type(tr: TypeRef | None, *, default_suffix: str = "DpgItem") -> str:
    """Dotted mounted type string used as ``TypeRef`` expression text."""
    if tr is None:
        return f"{ITEMS}.{default_suffix}"
    raw = tr.expr.strip()
    if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
        inner = raw[1:-1]
        if "." in inner:
            return inner
        return f"{ITEMS}.{inner}"
    return raw


def _default_attach_order(learning: UiWidgetLearning, mount_names: tuple[str, ...]) -> tuple[str, ...]:
    def sort_key(name: str) -> tuple[bool, int, str]:
        mpl = learning.mount_point_learnings.get(name, UiMountPointLearning())
        r = mpl.default_attach_rank
        return (r is None, r if r is not None else 10_000, name)

    return tuple(sorted(mount_names, key=sort_key))


def _default_child_mount(
    learning: UiWidgetLearning,
    mount_names: tuple[str, ...],
) -> str | None:
    if not mount_names:
        return None
    for name in mount_names:
        mpl = learning.mount_point_learnings.get(name, UiMountPointLearning())
        if mpl.default_child:
            return name
    return mount_names[0]


def _mount_specs_for(
    shaped_kind: str,
    mount_names: tuple[str, ...],
    learning: UiWidgetLearning,
) -> frozendict[str, MountPointSpec]:
    if not mount_names:
        return frozendict()
    out: dict[str, MountPointSpec] = {}
    for name in mount_names:
        mpl = learning.mount_point_learnings.get(name, UiMountPointLearning())
        accepted = _resolve_accepted_type(mpl.accepted_produced_type)
        sync_d, apply_d, max_c = MOUNT_OPS.get(
            (shaped_kind, name),
            ("sync_children", None, None),
        )
        replay = mpl.replay_kind if mpl.replay_kind is not None else MountReplayKind.NONE
        prefer = mpl.prefer_sync if mpl.prefer_sync is not None else False
        out[name] = MountPointSpec(
            name=name,
            accepted_produced_type=TypeRef(accepted),
            sync_method_name=sync_d,
            apply_method_name=apply_d,
            max_children=max_c,
            replay_kind=replay,
            prefer_sync=prefer,
        )
    return frozendict(out)


def build_widget_spec(item: DpgCanonicalMountable, *, ui_kind: str) -> UiWidgetSpec:
    shaped = shape_canonical_mountable(item)
    learning = widget_learning_for_kind(item.kind_name)
    uk = ui_kind

    ctor: dict[str, UiParamSpec] = {}
    props: dict[str, UiPropSpec] = {}
    for p in shaped.props:
        ctor[p.public_name] = UiParamSpec(
            name=p.public_name,
            annotation=TypeRef(_norm_annotation(p.annotation)),
            default_repr=p.default_repr,
        )
        is_value = item.kind_name in KINDS_DEFAULT_VALUE_AS_VALUE and p.public_name == "value"
        if is_value:
            props[p.public_name] = UiPropSpec(
                name=p.public_name,
                annotation=TypeRef(_norm_annotation(p.annotation)),
                mode=PropMode.CREATE_UPDATE,
                constructor_name=p.constructor_name,
                setter_kind=AccessorKind.DPG_VALUE,
                getter_kind=AccessorKind.DPG_VALUE,
            )
        else:
            props[p.public_name] = UiPropSpec(
                name=p.public_name,
                annotation=TypeRef(_norm_annotation(p.annotation)),
                mode=PropMode.CREATE_UPDATE,
                constructor_name=p.constructor_name,
                setter_kind=AccessorKind.DPG_CONFIG,
                setter_name=p.constructor_name,
            )

    events: dict[str, UiEventSpec] = {}
    for ev in shaped.events:
        events[ev.public_name] = UiEventSpec(
            name=ev.public_name,
            signal_name=ev.signal_name,
            payload_policy=ev.payload_policy,
        )

    mps = _mount_specs_for(shaped.kind_name, shaped.mount_point_names, learning)
    child_policy = ChildPolicy.ORDERED if mps else ChildPolicy.NONE
    default_child = _default_child_mount(learning, shaped.mount_point_names)
    default_attach = _default_attach_order(learning, shaped.mount_point_names)

    mounted = HAND_MOUNTED.get(uk, f"{GEN_MOD}.M_{item.factory_name}")

    return UiWidgetSpec(
        kind=uk,
        mounted_type_name=mounted,
        constructor_params=frozendict(ctor),
        props=frozendict(props),
        methods=frozendict(),
        child_policy=child_policy,
        events=frozendict(events),
        mount_points=mps,
        default_child_mount_point_name=default_child,
        default_attach_mount_point_names=default_attach,
    )


def build_all_widget_specs(loaded: DpgLoadedDump | None = None) -> dict[str, UiWidgetSpec]:
    data = load_dearpygui_dump() if loaded is None else loaded
    items = iter_canonical_mountables(data)
    dup = _duplicate_kind_names(items)
    by_kind: dict[str, UiWidgetSpec] = {}
    for item in items:
        uk = ui_kind_for_item(item, dup)
        spec = build_widget_spec(item, ui_kind=uk)
        if spec.kind in by_kind:
            msg = f"Duplicate UI kind {spec.kind!r}"
            raise ValueError(msg)
        by_kind[spec.kind] = spec
    return dict(sorted(by_kind.items(), key=lambda kv: kv[0]))


def _factories_needing_generated_classes(specs: Mapping[str, UiWidgetSpec]) -> list[tuple[str, bool]]:
    """``(factory_name, is_container)`` for ``M_<factory>`` stubs."""

    need: list[tuple[str, bool]] = []
    seen: set[str] = set()
    for spec in specs.values():
        if not spec.mounted_type_name.startswith(f"{GEN_MOD}."):
            continue
        factory = spec.mounted_type_name.removeprefix(f"{GEN_MOD}.M_")
        if factory in seen:
            continue
        seen.add(factory)
        is_container = spec.child_policy is ChildPolicy.ORDERED
        need.append((factory, is_container))
    return sorted(need, key=lambda t: t[0])


def _render_type_ref(tr: TypeRef) -> str:
    return f"TypeRef({tr.expr!r})"


def _render_ui_param(p: UiParamSpec) -> list[str]:
    ann = "None" if p.annotation is None else _render_type_ref(p.annotation)
    return [
        f"UiParamSpec(name={p.name!r}, annotation={ann}, default_repr={p.default_repr!r}),",
    ]


def _render_ui_prop(p: UiPropSpec) -> list[str]:
    ann = "None" if p.annotation is None else _render_type_ref(p.annotation)
    sk = "None" if p.setter_kind is None else f"AccessorKind.{p.setter_kind.name}"
    gk = "None" if p.getter_kind is None else f"AccessorKind.{p.getter_kind.name}"
    lines = [
        f"UiPropSpec(",
        f"                name={p.name!r},",
        f"                annotation={ann},",
        f"                mode=PropMode.{p.mode.name},",
        f"                constructor_name={p.constructor_name!r},",
        f"                setter_kind={sk},",
    ]
    if p.setter_name is not None:
        lines.append(f"                setter_name={p.setter_name!r},")
    lines.append(f"                getter_kind={gk},")
    if p.getter_name is not None:
        lines.append(f"                getter_name={p.getter_name!r},")
    lines.append("            ),")
    return lines


def _render_mount_point(mp: MountPointSpec) -> list[str]:
    acc = _render_type_ref(mp.accepted_produced_type)
    lines = [
        f'MountPointSpec(',
        f'                    name={mp.name!r},',
        f"                    accepted_produced_type={acc},",
        "                    params=(",
    ]
    for param in mp.params:
        keyed = param.keyed
        ann = "None" if param.annotation is None else _render_type_ref(param.annotation)
        lines.append(
            "                        "
            f'MountParamSpec(name={param.name!r}, annotation={ann}, '
            f"keyed={keyed!r}, default_repr={param.default_repr!r}),"
        )
    lines.extend(
        [
            "                    ),",
            f"                    min_children={mp.min_children!r},",
            f"                    max_children={mp.max_children!r},",
            f"                    apply_method_name={mp.apply_method_name!r},",
            f"                    sync_method_name={mp.sync_method_name!r},",
            f"                    place_method_name={mp.place_method_name!r},",
            f"                    append_method_name={mp.append_method_name!r},",
            f"                    detach_method_name={mp.detach_method_name!r},",
            f"                    replay_kind=MountReplayKind.{mp.replay_kind.name},",
            f"                    prefer_sync={mp.prefer_sync!r},",
            "                ),",
        ]
    )
    return lines


def _render_widget_spec(kind: str, spec: UiWidgetSpec) -> list[str]:
    lines: list[str] = [f'        "{kind}": UiWidgetSpec(']
    lines.append(f'            kind={kind!r},')
    lines.append(f"            mounted_type_name={spec.mounted_type_name!r},")
    lines.append("            constructor_params=frozendict({")
    for name in sorted(spec.constructor_params.keys()):
        lines.append(f'                "{name}": ')
        lines.extend("                " + s for s in _render_ui_param(spec.constructor_params[name]))
    lines.append("            }),")
    lines.append("            props=frozendict({")
    for name in sorted(spec.props.keys()):
        lines.append(f'                "{name}": ')
        lines.extend("                " + s for s in _render_ui_prop(spec.props[name]))
    lines.append("            }),")
    lines.append("            methods=frozendict(),")
    lines.append(f"            child_policy=ChildPolicy.{spec.child_policy.name},")
    lines.append("            events=frozendict({")
    for name in sorted(spec.events.keys()):
        ev = spec.events[name]
        lines.extend(
            [
                f'                "{name}": UiEventSpec(',
                f'                    name={ev.name!r},',
                f'                    signal_name={ev.signal_name!r},',
                f"                    payload_policy=EventPayloadPolicy.{ev.payload_policy.name},",
                "                ),",
            ]
        )
    lines.append("            }),")
    lines.append("            mount_points=frozendict({")
    for name in sorted(spec.mount_points.keys()):
        lines.append(f'                "{name}": ')
        lines.extend("                " + s for s in _render_mount_point(spec.mount_points[name]))
    lines.append("            }),")
    lines.append(f"            default_child_mount_point_name={spec.default_child_mount_point_name!r},")
    if spec.default_attach_mount_point_names:
        da = "(" + ", ".join(f"{n!r}" for n in spec.default_attach_mount_point_names) + ",)"
    else:
        da = "()"
    lines.append(f"            default_attach_mount_point_names={da},")
    lines.append("        ),")
    return lines


def render_generated_library_py(specs: Mapping[str, UiWidgetSpec]) -> str:
    factories = _factories_needing_generated_classes(specs)
    lines: list[str] = [
        '"""Generated DearPyGui mountable specs (checked in; re-run ``generate_dearpygui_library --emit``)."""',
        "",
        "from __future__ import annotations",
        "",
        "from frozendict import frozendict",
        "",
        "from pyrolyze.backends.dearpygui.items import (",
        "    DpgFactoryContainerItem,",
        "    DpgFactoryItem,",
        ")",
        "from pyrolyze.backends.model import (",
        "    AccessorKind,",
        "    ChildPolicy,",
        "    EventPayloadPolicy,",
        "    MountParamSpec,",
        "    MountPointSpec,",
        "    MountReplayKind,",
        "    PropMode,",
        "    TypeRef,",
        "    UiEventSpec,",
        "    UiParamSpec,",
        "    UiPropSpec,",
        "    UiWidgetSpec,",
        ")",
        "",
    ]
    for factory, is_container in factories:
        base = "DpgFactoryContainerItem" if is_container else "DpgFactoryItem"
        lines.append(f"class M_{factory}({base}):")
        lines.append(f'    FACTORY = "{factory}"')
        lines.append("")
    lines.append("")
    lines.append("class DearPyGuiUiLibrary:")
    lines.append('    """Static widget specs for DearPyGui ``MountableEngine`` clients."""')
    lines.append("")
    lines.append("    WIDGET_SPECS: frozendict[str, UiWidgetSpec] = frozendict({")
    for kind in sorted(specs.keys()):
        lines.extend(_render_widget_spec(kind, specs[kind]))
    lines.append("    })")
    lines.append("")
    lines.append("")
    lines.append('__all__ = ["DearPyGuiUiLibrary"] + [')
    lines.extend(f'    "M_{factory}",' for factory, _ in factories)
    lines.append("]")
    return "\n".join(lines) + "\n"


def write_generated_library(
    output_path: Path | None = None,
    *,
    loaded: DpgLoadedDump | None = None,
) -> Path:
    here = Path(__file__).resolve()
    repo_pkg = here.parents[1] / "src" / "pyrolyze" / "backends" / "dearpygui" / "generated_library.py"
    path = repo_pkg if output_path is None else output_path
    specs = build_all_widget_specs(loaded=loaded)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_generated_library_py(specs), encoding="utf-8")
    return path


__all__ = [
    "build_all_widget_specs",
    "build_widget_spec",
    "render_generated_library_py",
    "write_generated_library",
]
