from __future__ import annotations

from dataclasses import dataclass
from html import escape as html_escape
from pathlib import Path
import shutil
import subprocess
from typing import Iterable

from pyrolyze.backends.mountable_engine import MountedMountableNode
from pyrolyze.runtime import RenderContext, SlotId, SlotIdPath
from pyrolyze.testing.generic_backend.harness import PyroRenderHarness, PyroRenderResult
from pyrolyze.visitor import CapturedContext, capture_context_graph


_ACTIVE_FILL = "#d9f7be"
_INACTIVE_FILL = "#e5e7eb"
_RENDER_FILL = "#dbeafe"
_RENDER_EDGE = "#1d4ed8"


@dataclass(frozen=True, slots=True)
class _SlotCluster:
    cluster_id: str
    node_id: str
    cluster_key: tuple[object, ...]
    slot_path: SlotIdPath
    slot_id: SlotId | None
    label: str
    active: bool


def render_context_to_dot(
    value: RenderContext | PyroRenderHarness,
    *,
    mounted: PyroRenderResult | tuple[MountedMountableNode, ...] | list[MountedMountableNode] | None = None,
    inactive_slot_ids: Iterable[SlotId] = (),
) -> str:
    context = _render_context_from(value)
    mounted_roots = _mounted_roots_from(value, mounted=mounted)
    capture = capture_context_graph(context)

    lines = [
        "digraph PyrolyzeContextRender {",
        '  graph [rankdir="TB", compound=true];',
        '  node [shape=box, style="filled,rounded"];',
        '  edge [penwidth=1.4];',
    ]

    clusters: dict[tuple[object, ...], _SlotCluster] = {}
    clusters_by_slot_id: dict[SlotId | None, list[_SlotCluster]] = {}
    cluster_contents: dict[str, list[str]] = {}
    render_nodes_by_cluster: dict[str, int] = {}
    next_slot_id = 0
    next_render_id = 0
    module_aliases: dict[str, str] = {}

    def fresh_slot_ids() -> tuple[str, str]:
        nonlocal next_slot_id
        cluster_id = f"cluster_slot_{next_slot_id}"
        node_id = f"slot_{next_slot_id}"
        next_slot_id += 1
        return cluster_id, node_id

    def ensure_cluster(
        cluster_key: tuple[object, ...],
        slot_path: SlotIdPath,
        slot_id: SlotId | None,
        *,
        label: str,
        active: bool,
    ) -> _SlotCluster:
        existing = clusters.get(cluster_key)
        if existing is not None:
            return existing
        cluster_id, node_id = fresh_slot_ids()
        info = _SlotCluster(
            cluster_id=cluster_id,
            node_id=node_id,
            cluster_key=cluster_key,
            slot_path=slot_path,
            slot_id=slot_id,
            label=label,
            active=active,
        )
        clusters[cluster_key] = info
        clusters_by_slot_id.setdefault(slot_id, []).append(info)
        cluster_contents[cluster_id] = []
        fill = _ACTIVE_FILL if active else _INACTIVE_FILL
        cluster_contents[cluster_id].append(
            f'    {node_id} [label=<{_html_multiline_label(label)}>, fillcolor="{fill}", color="black"];'
        )
        return info

    def add_context(
        context_node: CapturedContext,
        parent_cluster_key: tuple[object, ...] = (),
        parent_slot_path: SlotIdPath = SlotIdPath.empty(),
    ) -> None:
        slot_path = parent_slot_path.child(context_node.slot_id)
        cluster_key = parent_cluster_key + ((context_node.kind, context_node.slot_id),)
        cluster = ensure_cluster(
            cluster_key,
            slot_path,
            context_node.slot_id,
            label=_slot_label(context_node.kind, context_node.slot_id, module_aliases),
            active=True,
        )
        if parent_cluster_key:
            parent = clusters[parent_cluster_key]
            lines.append(f'  {parent.node_id} -> {cluster.node_id} [color="black"];')
        for child in context_node.children:
            add_context(child, cluster_key, slot_path)

    add_context(capture.root)

    for inactive_slot_id in inactive_slot_ids:
        existing_for_slot = clusters_by_slot_id.get(inactive_slot_id, ())
        if existing_for_slot:
            continue
        parent_slot_id = _slot_parent_id(inactive_slot_id)
        parent_cluster = _best_owner_cluster(parent_slot_id, clusters_by_slot_id) if parent_slot_id is not None else None
        base_slot_path = parent_cluster.slot_path if parent_cluster is not None else SlotIdPath.empty()
        cluster_key_base = parent_cluster.cluster_key if parent_cluster is not None else ()
        slot_path = base_slot_path.child(inactive_slot_id)
        cluster_key = cluster_key_base + (("inactive", inactive_slot_id),)
        cluster = ensure_cluster(
            cluster_key,
            slot_path,
            inactive_slot_id,
            label=_slot_label("inactive", inactive_slot_id, module_aliases),
            active=False,
        )
        if parent_cluster is not None:
            lines.append(f'  {parent_cluster.node_id} -> {cluster.node_id} [color="black", style="dashed"];')

    def owner_cluster_for_in_scope(
        slot_id: SlotIdPath | SlotId | None,
        parent_owner_cluster: _SlotCluster | None,
    ) -> _SlotCluster:
        target_slot_id = _last_render_slot_id(slot_id)
        candidates = clusters_by_slot_id.get(target_slot_id, ())
        if parent_owner_cluster is not None:
            scoped = [
                cluster
                for cluster in candidates
                if cluster.slot_path.items[: len(parent_owner_cluster.slot_path.items)]
                == parent_owner_cluster.slot_path.items
            ]
            if scoped:
                candidates = scoped
        for cluster in candidates:
            if render_nodes_by_cluster.get(cluster.cluster_id, 0) == 0:
                return cluster
        if candidates:
            return candidates[0]
        root_cluster = _best_owner_cluster(None, clusters_by_slot_id)
        assert root_cluster is not None
        return root_cluster

    def add_render_node(
        node: MountedMountableNode,
        parent_render_id: str | None = None,
        parent_owner_cluster: _SlotCluster | None = None,
    ) -> None:
        nonlocal next_render_id
        render_id = f"render_{next_render_id}"
        next_render_id += 1
        owner = owner_cluster_for_in_scope(node.element.slot_id, parent_owner_cluster)
        node_name = getattr(node.mountable, "_pyro_constructor_kwargs", {}).get("name")
        render_label = (
            type(node.mountable).__name__
            if node_name is None
            else f"{type(node.mountable).__name__}\n{node_name}"
        )
        cluster_contents[owner.cluster_id].append(
            f'    {render_id} [label=<{_html_multiline_label(render_label)}>, fillcolor="{_RENDER_FILL}", color="{_RENDER_EDGE}"];'
        )
        render_nodes_by_cluster[owner.cluster_id] = render_nodes_by_cluster.get(owner.cluster_id, 0) + 1
        if parent_render_id is not None:
            lines.append(f'  {parent_render_id} -> {render_id} [color="{_RENDER_EDGE}"];')
        for child in node.child_nodes:
            add_render_node(child, render_id, owner)

    for root in mounted_roots:
        add_render_node(root)

    for info in clusters.values():
        lines.append(f"  subgraph {info.cluster_id} {{")
        lines.append('    style="rounded";')
        lines.append('    color="#94a3b8";')
        lines.extend(cluster_contents[info.cluster_id])
        lines.append("  }")

    if module_aliases:
        legend_lines = [f"{alias} = {canonical}" for canonical, alias in module_aliases.items()]
        legend_label = _html_multiline_label("Modules\n" + "\n".join(legend_lines))
        lines.append(
            f'  module_legend [shape=note, style="filled", fillcolor="#fff7cc", label=<{legend_label}>];'
        )

    lines.append("}")
    return "\n".join(lines)


def _best_owner_cluster(
    slot_id: SlotId | None,
    clusters_by_slot_id: dict[SlotId | None, list[_SlotCluster]],
) -> _SlotCluster | None:
    candidates = clusters_by_slot_id.get(slot_id, ())
    return candidates[0] if candidates else None


def write_render_context_graph(
    value: RenderContext | PyroRenderHarness,
    output_stem: Path,
    *,
    mounted: PyroRenderResult | tuple[MountedMountableNode, ...] | list[MountedMountableNode] | None = None,
    inactive_slot_ids: Iterable[SlotId] = (),
) -> tuple[Path, Path | None]:
    dot_path = output_stem.with_suffix(".dot")
    svg_path = output_stem.with_suffix(".svg")
    dot_path.parent.mkdir(parents=True, exist_ok=True)
    dot_path.write_text(
        render_context_to_dot(value, mounted=mounted, inactive_slot_ids=inactive_slot_ids),
        encoding="utf-8",
    )
    if shutil.which("dot") is None:
        return dot_path, None
    subprocess.run(
        ["dot", "-Tsvg", str(dot_path), "-o", str(svg_path)],
        check=True,
    )
    return dot_path, svg_path


def _render_context_from(value: RenderContext | PyroRenderHarness) -> RenderContext:
    if isinstance(value, RenderContext):
        return value
    return value._render_context


def _mounted_roots_from(
    value: RenderContext | PyroRenderHarness,
    *,
    mounted: PyroRenderResult | tuple[MountedMountableNode, ...] | list[MountedMountableNode] | None,
) -> tuple[MountedMountableNode, ...]:
    if mounted is None:
        if isinstance(value, PyroRenderHarness):
            return tuple(value.get().mounted_roots)
        return ()
    if isinstance(mounted, PyroRenderResult):
        return tuple(mounted.mounted_roots)
    return tuple(mounted)


def _slot_label(kind: str, slot_id: SlotId | None, module_aliases: dict[str, str]) -> str:
    if slot_id is None:
        return kind
    alias = _module_alias(slot_id.module_id.canonical_name, module_aliases)
    return (
        f"{kind}\n"
        f"Slot({alias}, {slot_id.slot_index}, {slot_id.line_no}, {slot_id.key_path!r})"
    )


def _last_render_slot_id(slot_id: SlotIdPath | SlotId | None) -> SlotId | None:
    if isinstance(slot_id, SlotIdPath):
        return slot_id.items[-1] if slot_id.items else None
    if isinstance(slot_id, SlotId) or slot_id is None:
        return slot_id
    return None


def _module_alias(canonical_name: str, module_aliases: dict[str, str]) -> str:
    existing = module_aliases.get(canonical_name)
    if existing is not None:
        return existing
    alias = f"M{len(module_aliases) + 1}"
    module_aliases[canonical_name] = alias
    return alias


def _slot_parent_id(slot_id: SlotId | None) -> SlotId | None:
    if slot_id is None:
        return None
    return None


def _html_multiline_label(value: str) -> str:
    lines = [html_escape(line) for line in value.splitlines() if line]
    if not lines:
        return ""
    return "<BR/>".join(lines)


__all__ = [
    "render_context_to_dot",
    "write_render_context_graph",
]
