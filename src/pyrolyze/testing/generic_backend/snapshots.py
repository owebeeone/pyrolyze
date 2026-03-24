"""Snapshot helpers for the generic testing backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeAlias

from frozendict import frozendict

from pyrolyze.api import MountDirective, PyrolyzeMountAdvertisement, UIElement
from pyrolyze.backends.mountable_engine import MountedMountableNode
from pyrolyze.runtime import RenderContext

from .harness import PyroRenderHarness, PyroRenderResult
from .model import PyroNode
from .runtime import GeneratedPyroMountable


@dataclass(frozen=True, slots=True)
class PyroUiElement:
    kind: str
    props: frozendict[str, Any]
    children: tuple["PyroUiSnapshot", ...] = ()


@dataclass(frozen=True, slots=True)
class PyroUiMountDirective:
    selectors: tuple[object, ...]
    children: tuple["PyroUiSnapshot", ...] = ()


@dataclass(frozen=True, slots=True)
class PyroUiMountAdvertisement:
    key: object
    selectors: tuple[object, ...]
    default: bool = False


PyroUiSnapshot: TypeAlias = PyroUiElement | PyroUiMountDirective | PyroUiMountAdvertisement


def run_pyro_ui(value: object) -> object:
    roots = _extract_ui_roots(value)
    snapshots = tuple(_snapshot_ui_node(root) for root in roots)
    if len(snapshots) == 1:
        return snapshots[0]
    return snapshots


def run_pyro(value: object) -> object:
    roots = _extract_mounted_roots(value)
    snapshots = tuple(_snapshot_mounted_root(root) for root in roots)
    if len(snapshots) == 1:
        return snapshots[0]
    return snapshots


def _extract_ui_roots(value: object) -> tuple[object, ...]:
    if isinstance(value, PyroRenderHarness):
        return value.get().ui_roots
    if isinstance(value, PyroRenderResult):
        return value.ui_roots
    if isinstance(value, RenderContext):
        return value.committed_ui()
    if isinstance(value, UIElement | MountDirective | PyrolyzeMountAdvertisement):
        return (value,)
    if isinstance(value, tuple | list):
        return tuple(value)
    raise TypeError(f"unsupported UI snapshot input {type(value)!r}")


def _extract_mounted_roots(value: object) -> tuple[object, ...]:
    if isinstance(value, PyroRenderHarness):
        return value.get().mounted_roots
    if isinstance(value, PyroRenderResult):
        return value.mounted_roots
    if isinstance(value, MountedMountableNode | PyroNode):
        return (value,)
    if isinstance(value, tuple | list):
        return tuple(value)
    raise TypeError(f"unsupported mounted snapshot input {type(value)!r}")


def _snapshot_ui_node(node: object) -> PyroUiSnapshot:
    if isinstance(node, UIElement):
        return PyroUiElement(
            kind=node.kind,
            props=frozendict({key: _normalize_ui_value(value) for key, value in node.props.items()}),
            children=tuple(_snapshot_ui_node(child) for child in node.children),
        )
    if isinstance(node, MountDirective):
        return PyroUiMountDirective(
            selectors=node.selectors,
            children=tuple(_snapshot_ui_node(child) for child in node.children),
        )
    if isinstance(node, PyrolyzeMountAdvertisement):
        return PyroUiMountAdvertisement(
            key=node.key,
            selectors=node.selectors,
            default=node.default,
        )
    raise TypeError(f"unsupported UI node {type(node)!r}")


def _normalize_ui_value(value: Any) -> Any:
    if isinstance(value, dict):
        return frozendict({key: _normalize_ui_value(inner) for key, inner in value.items()})
    if isinstance(value, list | tuple):
        return tuple(_normalize_ui_value(inner) for inner in value)
    return value


def _snapshot_mounted_root(root: object) -> PyroNode:
    if isinstance(root, PyroNode):
        return root
    if isinstance(root, MountedMountableNode):
        mountable = root.mountable
        if not isinstance(mountable, GeneratedPyroMountable):
            raise TypeError(f"expected GeneratedPyroMountable, got {type(mountable)!r}")
        return mountable.to_pyro_node()
    raise TypeError(f"unsupported mounted root {type(root)!r}")


__all__ = [
    "PyroUiElement",
    "PyroUiMountAdvertisement",
    "PyroUiMountDirective",
    "run_pyro",
    "run_pyro_ui",
]
