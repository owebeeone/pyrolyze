from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import pytest

from pyrolyze.runtime.context import ModuleRegistry, SlotId
from pyrolyze.runtime.mount_reconciler import reconcile_owner
from pyrolyze.runtime.ui_nodes import (
    UiBackendAdapter,
    UiNode,
    UiNodeId,
    UiNodeSpec,
    UiOwnerCommitState,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.mount_reconciler")
_OWNER_SLOT = SlotId(_MODULE_ID, 1, line_no=10)


def _node_id(index: int) -> UiNodeId:
    return UiNodeId(owner_slot_id=_OWNER_SLOT, region_index=index)


def _button_spec(
    *,
    node_id: UiNodeId,
    label: str = "Run",
    enabled: bool = True,
    on_press: Callable[..., None] | None = None,
    children: tuple[UiNodeSpec, ...] = (),
) -> UiNodeSpec:
    return UiNodeSpec(
        node_id=node_id,
        kind="button",
        props={"label": label, "enabled": enabled, "tone": "default", "visible": True},
        event_props={"on_press": on_press},
        children=children,
    )


def _section_spec(
    *,
    node_id: UiNodeId,
    title: str = "Section",
    children: tuple[UiNodeSpec, ...] = (),
) -> UiNodeSpec:
    return UiNodeSpec(
        node_id=node_id,
        kind="section",
        props={"title": title, "accent": None, "visible": True},
        event_props={},
        children=children,
    )


@dataclass
class _FakeBinding:
    spec: UiNodeSpec
    accepts_children: bool = False
    attached: list[UiNode] = field(default_factory=list)
    update_calls: list[tuple[dict[str, Any], dict[str, Any]]] = field(default_factory=list)
    detach_calls: list[UiNode] = field(default_factory=list)
    place_calls: list[tuple[str, int]] = field(default_factory=list)
    disposed: bool = False
    fail_on_place_index: int | None = None
    fail_on_place_once: bool = False

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: dict[str, Any],
        changed_events: dict[str, Callable[..., None] | None],
    ) -> None:
        self.spec = next_spec
        self.update_calls.append((changed_props, changed_events))

    def place_child(self, child: UiNode, index: int) -> None:
        if not self.accepts_children:
            raise ValueError("binding does not accept children")
        if self.fail_on_place_index == index:
            if self.fail_on_place_once:
                self.fail_on_place_index = None
            raise RuntimeError(f"place failed at index {index}")
        self.place_calls.append((child.spec.kind, index))
        if child in self.attached:
            self.attached.remove(child)
        self.attached.insert(index, child)

    def detach_child(self, child: UiNode) -> None:
        self.detach_calls.append(child)
        if child in self.attached:
            self.attached.remove(child)

    def dispose(self) -> None:
        self.disposed = True
        self.attached.clear()


@dataclass
class _FakeBackend(UiBackendAdapter):
    backend_id: str = "fake-mount"
    create_calls: list[str] = field(default_factory=list)

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        parent_binding: Any | None,
    ) -> _FakeBinding:
        del parent_binding
        self.create_calls.append(spec.kind)
        return _FakeBinding(spec=spec, accepts_children=spec.kind == "section")

    def can_reuse(self, current: UiNode, next_spec: UiNodeSpec) -> bool:
        return current.spec.kind == next_spec.kind

    def assert_ui_thread(self) -> None:
        return None

    def post_to_ui(self, callback: Callable[[], None]) -> None:
        callback()


def test_mount_reconciler_mounts_initial_nodes_and_places_in_order() -> None:
    backend = _FakeBackend()
    parent = _FakeBinding(spec=_section_spec(node_id=_node_id(99)), accepts_children=True)
    owner = UiOwnerCommitState(owner_id=_OWNER_SLOT)
    specs = (
        _button_spec(node_id=_node_id(1), label="One"),
        _button_spec(node_id=_node_id(2), label="Two"),
    )

    reconcile_owner(owner, specs, backend=backend, parent_binding=parent)

    assert backend.create_calls == ["button", "button"]
    assert [node.spec.node_id for node in owner.mounted_nodes] == [_node_id(1), _node_id(2)]
    assert [child.spec.node_id for child in parent.attached] == [_node_id(1), _node_id(2)]


def test_mount_reconciler_updates_reused_nodes_and_reconciles_children() -> None:
    backend = _FakeBackend()
    parent = _FakeBinding(spec=_section_spec(node_id=_node_id(99)), accepts_children=True)
    owner = UiOwnerCommitState(owner_id=_OWNER_SLOT)
    initial = (
        _section_spec(
            node_id=_node_id(1),
            title="Panel",
            children=(
                _button_spec(node_id=_node_id(10), label="First"),
                _button_spec(node_id=_node_id(11), label="Second"),
            ),
        ),
    )

    reconcile_owner(owner, initial, backend=backend, parent_binding=parent)
    section_node = owner.mounted_nodes[0]
    section_binding = section_node.binding
    assert isinstance(section_binding, _FakeBinding)
    section_binding.place_calls.clear()

    updated = (
        _section_spec(
            node_id=_node_id(1),
            title="Panel+",
            children=(
                _button_spec(node_id=_node_id(11), label="Second"),
                _button_spec(node_id=_node_id(10), label="First"),
            ),
        ),
    )
    reconcile_owner(owner, updated, backend=backend, parent_binding=parent)

    assert owner.mounted_nodes[0] is section_node
    assert section_binding.update_calls == [({"title": "Panel+"}, {})]
    assert [child.spec.node_id for child in section_node.children] == [_node_id(11), _node_id(10)]
    assert section_binding.place_calls == [("button", 0)]


def test_mount_reconciler_backend_swap_forces_full_remount() -> None:
    owner = UiOwnerCommitState(owner_id=_OWNER_SLOT)
    parent = _FakeBinding(spec=_section_spec(node_id=_node_id(99)), accepts_children=True)
    first_backend = _FakeBackend(backend_id="fake-a")
    specs = (
        _button_spec(node_id=_node_id(1), label="One"),
        _button_spec(node_id=_node_id(2), label="Two"),
    )

    reconcile_owner(owner, specs, backend=first_backend, parent_binding=parent)
    original_nodes = tuple(owner.mounted_nodes)
    parent.detach_calls.clear()

    second_backend = _FakeBackend(backend_id="fake-b")
    reconcile_owner(owner, specs, backend=second_backend, parent_binding=parent)

    assert second_backend.create_calls == ["button", "button"]
    assert {id(node) for node in parent.detach_calls} == {id(node) for node in original_nodes}
    assert all(node.binding.disposed for node in original_nodes)


def test_mount_reconciler_rolls_back_to_previous_specs_on_failure() -> None:
    backend = _FakeBackend()
    parent = _FakeBinding(spec=_section_spec(node_id=_node_id(99)), accepts_children=True)
    owner = UiOwnerCommitState(owner_id=_OWNER_SLOT)
    stable = (
        _button_spec(node_id=_node_id(1), label="Stable"),
        _button_spec(node_id=_node_id(2), label="Before"),
    )
    reconcile_owner(owner, stable, backend=backend, parent_binding=parent)

    parent.fail_on_place_index = 1
    parent.fail_on_place_once = True
    with pytest.raises(RuntimeError, match="place failed"):
        reconcile_owner(
            owner,
            (
                _button_spec(node_id=_node_id(1), label="Stable"),
                _section_spec(node_id=_node_id(2), title="Explode"),
            ),
            backend=backend,
            parent_binding=parent,
        )

    assert [node.spec.kind for node in owner.mounted_nodes] == ["button", "button"]
    assert [node.spec.node_id for node in parent.attached] == [_node_id(1), _node_id(2)]
