from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
from typing import Any, Callable

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    ComponentRef,
    pyrolyze_component_ref,
    pyrolyze_slotted,
)
from pyrolyze.compiler import load_transformed_namespace

from tests.external_store_test_utils import StoreProbe


LOG: list[tuple[object, ...]] = []
DATASTORE: dict[str, StoreProbe[object]] = {}


def reset_shape_stores() -> None:
    LOG.clear()
    DATASTORE.clear()


def set_shape_value(key: str, value: object) -> None:
    probe = DATASTORE.get(key)
    if probe is None:
        DATASTORE[key] = StoreProbe(key, value, LOG)
        return
    probe.value = value


def notify_shape_value(key: str, value: object) -> None:
    probe = DATASTORE.get(key)
    if probe is None:
        probe = StoreProbe(key, value, LOG)
        DATASTORE[key] = probe
    probe.notify(value)


@pyrolyze_slotted
def use_stored(key: str):
    probe = DATASTORE.get(key)
    if probe is None:
        raise KeyError(f"no shape store for key {key!r}")
    return probe.ref()


def bind_component_call(
    component: ComponentRef[Any],
    /,
    *args: Any,
    **kwargs: Any,
) -> ComponentRef[[]]:
    meta = component._pyrolyze_meta

    def bound_runtime_impl(__pyr_ctx: object, __pyr_dirty_state: object) -> None:
        meta._func(__pyr_ctx, __pyr_dirty_state, *args, **kwargs)

    def bound_public() -> None:
        raise CallFromNonPyrolyzeContext(meta.name)

    bound_public.__name__ = f"{meta.name}_bound"
    bound_public.__qualname__ = bound_public.__name__
    bound_public.__annotations__ = {"return": "None"}

    return pyrolyze_component_ref(
        ComponentMetadata(
            name=bound_public.__name__,
            _func=bound_runtime_impl,
            param_names=(),
        )
    )(bound_public)


@dataclass(frozen=True, slots=True)
class CallShape:
    call: ComponentRef[[]] | None

    @classmethod
    def capture(
        cls,
        func: ComponentRef[Any] | None,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> "CallShape":
        if func is None:
            return cls.none()
        return cls(bind_component_call(func, *args, **kwargs))

    @classmethod
    def none(cls) -> "CallShape":
        return cls(None)

    def __bool__(self) -> bool:
        return self.call is not None


@dataclass(frozen=True, slots=True)
class ShapeBasic:
    top_leaf: CallShape
    container: CallShape
    children: tuple[CallShape, ...]
    bottom_leaf: CallShape


@dataclass(frozen=True, slots=True)
class ShapeRoot:
    container: CallShape
    child: CallShape


_PYRO_SHAPES_SOURCE = """
from pyrolyze.api import ComponentRef, keyed, pyrolyze
from tests.basic_pyro_shapes import CallShape, ShapeBasic, ShapeRoot, use_stored

@pyrolyze
def shape_basic(key: str) -> None:
    sd: ShapeBasic = use_stored(key)

    if sd.top_leaf:
        top_leaf_call: ComponentRef[[]] = sd.top_leaf.call
        top_leaf_call()

    if sd.container:
        container_call: ComponentRef[[]] = sd.container.call
        with container_call():
            for _index, child in keyed(enumerate(sd.children), key=lambda item: item[0]):
                if child:
                    child_call: ComponentRef[[]] = child.call
                    child_call()

    if sd.bottom_leaf:
        bottom_leaf_call: ComponentRef[[]] = sd.bottom_leaf.call
        bottom_leaf_call()

@pyrolyze
def shape_root(key: str) -> None:
    sd: ShapeRoot = use_stored(key)

    if sd.container:
        container_call: ComponentRef[[]] = sd.container.call
        with container_call():
            if sd.child:
                child_call: ComponentRef[[]] = sd.child.call
                child_call()
"""


def load_basic_shapes_namespace(*, module_name: str = "example.pyro_shapes.basic") -> dict[str, object]:
    return load_transformed_namespace(
        _PYRO_SHAPES_SOURCE,
        module_name=module_name,
        filename=f"/virtual/{module_name.replace('.', '/')}.py",
    )


def _snapshot_roots(snapshot: object) -> tuple[object, ...]:
    if isinstance(snapshot, tuple):
        return snapshot
    return (snapshot,)


def snapshot_to_dot(snapshot: object) -> str:
    lines = ["digraph PyroSnapshot {", '  rankdir="TB";', '  node [shape=box];']
    seen: set[int] = set()
    next_id = 0
    ids: dict[int, str] = {}

    def node_id(obj: object) -> str:
        nonlocal next_id
        key = id(obj)
        existing = ids.get(key)
        if existing is not None:
            return existing
        value = f"n{next_id}"
        next_id += 1
        ids[key] = value
        return value

    def emit_node(node: object) -> None:
        key = id(node)
        if key in seen:
            return
        seen.add(key)
        current_id = node_id(node)
        node_type = getattr(node, "node_type", type(node).__name__)
        kwargs = dict(getattr(node, "kwargs", {}))
        name = kwargs.get("name", "")
        label = f"{node_type}\\n{name}" if name else node_type
        lines.append(f'  {current_id} [label="{label}"];')

        mounts = getattr(node, "mounts", {})
        for mount_name, buckets in mounts.items():
            for bucket in buckets:
                for entry in bucket.entries:
                    child = entry.node
                    child_id = node_id(child)
                    lines.append(f'  {current_id} -> {child_id} [label="{mount_name}"];')
                    emit_node(child)

        host_surfaces = getattr(node, "host_surfaces", {})
        for surface_name, surface in host_surfaces.items():
            for entry in surface.entries:
                child = entry.node
                child_id = node_id(child)
                lines.append(f'  {current_id} -> {child_id} [style=dashed,label="{surface_name}"];')
                emit_node(child)

    roots = _snapshot_roots(snapshot)
    for index, root in enumerate(roots):
        root_marker = f"root{index}"
        lines.append(f'  {root_marker} [shape=point,label=""];')
        target_id = node_id(root)
        lines.append(f"  {root_marker} -> {target_id};")
        emit_node(root)

    lines.append("}")
    return "\n".join(lines)


def write_snapshot_graph(snapshot: object, output_stem: Path) -> tuple[Path, Path | None]:
    dot_path = output_stem.with_suffix(".dot")
    svg_path = output_stem.with_suffix(".svg")
    dot_path.parent.mkdir(parents=True, exist_ok=True)
    dot_path.write_text(snapshot_to_dot(snapshot))
    if shutil.which("dot") is None:
        return dot_path, None
    subprocess.run(
        ["dot", "-Tsvg", str(dot_path), "-o", str(svg_path)],
        check=True,
    )
    return dot_path, svg_path


def scratch_test_output_stem(test_name: str) -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    return repo_root / "scratch" / "tests" / test_name / "basic_shape_snapshot"
