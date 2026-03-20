from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import pytest

from pyrolyze.api import UIElement
from pyrolyze.runtime.context import ModuleRegistry, SlotId
from pyrolyze.runtime.ui_nodes import (
    FROZEN_V1_REGISTRY,
    UiBackendAdapter,
    UiNode,
    UiNodeDescriptorRegistry,
    UiNodeId,
    UiNodeSpec,
    UiOwnerCommitState,
    changed_events,
    changed_props,
    normalize_ui_elements,
    reconcile_owner,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.ui_reconciliation")
_OWNER_SLOT = SlotId(_MODULE_ID, 1, line_no=10)


def _node_id(index: int) -> UiNodeId:
    return UiNodeId(owner_slot_id=_OWNER_SLOT, region_index=index)


def _button_spec(
    *,
    node_id: UiNodeId,
    label: str = "Run",
    enabled: bool = True,
    on_press: Callable[..., None] | None = None,
) -> UiNodeSpec:
    return UiNodeSpec(
        node_id=node_id,
        kind="button",
        props={"label": label, "enabled": enabled, "tone": "default", "visible": True},
        event_props={"on_press": on_press},
    )


def _badge_spec(
    *,
    node_id: UiNodeId,
    text: str = "Ready",
) -> UiNodeSpec:
    return UiNodeSpec(
        node_id=node_id,
        kind="badge",
        props={"text": text, "tone": None, "visible": True},
        event_props={},
    )


@dataclass
class _FakeBinding:
    spec: UiNodeSpec
    label: str
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
    backend_id: str = "fake"
    create_calls: list[str] = field(default_factory=list)

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        parent_binding: Any | None,
    ) -> _FakeBinding:
        del parent_binding
        self.create_calls.append(spec.kind)
        return _FakeBinding(spec=spec, label=f"{spec.kind}:{len(self.create_calls)}")

    def can_reuse(self, current: UiNode, next_spec: UiNodeSpec) -> bool:
        return True

    def assert_ui_thread(self) -> None:
        return None

    def post_to_ui(self, callback: Callable[[], None]) -> None:
        callback()


def test_changed_props_uses_declared_diff_modes() -> None:
    registry = UiNodeDescriptorRegistry(
        descriptors={
            "sample": FROZEN_V1_REGISTRY.descriptor_for("button").__class__(
                kind="sample",
                role="input",
                child_policy="none",
                props={
                    "same": FROZEN_V1_REGISTRY.descriptor_for("button").props["label"].__class__(
                        "same", required=True
                    ),
                    "identity_value": FROZEN_V1_REGISTRY.descriptor_for("button").props["label"].__class__(
                        "identity_value", required=True, diff_mode="identity"
                    ),
                    "always": FROZEN_V1_REGISTRY.descriptor_for("button").props["label"].__class__(
                        "always", required=True, diff_mode="always_dirty"
                    ),
                },
                events={},
            )
        }
    )
    descriptor = registry.descriptor_for("sample")
    shared = ["same"]
    prev = UiNodeSpec(
        node_id=_node_id(1),
        kind="sample",
        props={"same": [1, 2], "identity_value": shared, "always": "x"},
        event_props={},
    )
    next_spec = UiNodeSpec(
        node_id=_node_id(1),
        kind="sample",
        props={"same": [1, 2], "identity_value": ["same"], "always": "x"},
        event_props={},
    )

    assert changed_props(prev, next_spec, descriptor=descriptor) == {
        "identity_value": ["same"],
        "always": "x",
    }


def test_reconcile_owner_mounts_initial_nodes_and_places_in_order() -> None:
    backend = _FakeBackend()
    parent = _FakeBinding(spec=_badge_spec(node_id=_node_id(99)), label="parent")
    owner = UiOwnerCommitState(owner_id=_OWNER_SLOT)
    specs = (
        _button_spec(node_id=_node_id(1), label="One"),
        _badge_spec(node_id=_node_id(2), text="Two"),
    )

    reconcile_owner(owner, specs, backend=backend, parent_binding=parent)

    assert backend.create_calls == ["button", "badge"]
    assert [node.spec.node_id for node in owner.mounted_nodes] == [_node_id(1), _node_id(2)]
    assert [child.spec.kind for child in parent.attached] == ["button", "badge"]


def test_reconcile_owner_updates_only_changed_props_and_events_for_reused_node() -> None:
    backend = _FakeBackend()
    parent = _FakeBinding(spec=_badge_spec(node_id=_node_id(99)), label="parent")
    owner = UiOwnerCommitState(owner_id=_OWNER_SLOT)
    press_a = lambda: None
    press_b = lambda: None
    initial = (_button_spec(node_id=_node_id(1), label="One", on_press=press_a),)

    reconcile_owner(owner, initial, backend=backend, parent_binding=parent)

    next_specs = (_button_spec(node_id=_node_id(1), label="Two", on_press=press_b),)
    reconcile_owner(owner, next_specs, backend=backend, parent_binding=parent)

    binding = owner.mounted_nodes[0].binding
    assert backend.create_calls == ["button"]
    assert binding.update_calls == [
        ({"label": "Two"}, {"on_press": press_b}),
    ]


def test_reconcile_owner_reorders_reused_nodes_without_recreating_them() -> None:
    backend = _FakeBackend()
    parent = _FakeBinding(spec=_badge_spec(node_id=_node_id(99)), label="parent")
    owner = UiOwnerCommitState(owner_id=_OWNER_SLOT)
    first = (
        _button_spec(node_id=_node_id(1), label="One"),
        _button_spec(node_id=_node_id(2), label="Two"),
    )
    reconcile_owner(owner, first, backend=backend, parent_binding=parent)
    created = tuple(owner.mounted_nodes)

    second = (
        _button_spec(node_id=_node_id(2), label="Two"),
        _button_spec(node_id=_node_id(1), label="One"),
    )
    reconcile_owner(owner, second, backend=backend, parent_binding=parent)

    assert backend.create_calls == ["button", "button"]
    assert owner.mounted_nodes == [created[1], created[0]]
    assert [node.spec.node_id for node in parent.attached] == [_node_id(2), _node_id(1)]


def test_reconcile_owner_reuses_normalized_ui_elements_by_call_site_identity() -> None:
    backend = _FakeBackend()
    parent = _FakeBinding(spec=_badge_spec(node_id=_node_id(99)), label="parent")
    owner = UiOwnerCommitState(owner_id=_OWNER_SLOT)
    first_specs = normalize_ui_elements(
        _OWNER_SLOT,
        (
            UIElement(kind="badge", props={"text": "One", "visible": True}, call_site_id=1),
            UIElement(kind="badge", props={"text": "Two", "visible": True}, call_site_id=2),
        ),
    )
    reconcile_owner(owner, first_specs, backend=backend, parent_binding=parent)
    created = tuple(owner.mounted_nodes)

    second_specs = normalize_ui_elements(
        _OWNER_SLOT,
        (
            UIElement(kind="badge", props={"text": "Two", "visible": True}, call_site_id=2),
            UIElement(kind="badge", props={"text": "One", "visible": True}, call_site_id=1),
        ),
    )
    reconcile_owner(owner, second_specs, backend=backend, parent_binding=parent)

    assert backend.create_calls == ["badge", "badge"]
    assert owner.mounted_nodes == [created[1], created[0]]


def test_reconcile_owner_replaces_incompatible_node_and_disposes_old_subtree() -> None:
    @dataclass
    class _ReplacingBackend(_FakeBackend):
        def can_reuse(self, current: UiNode, next_spec: UiNodeSpec) -> bool:
            return current.spec.kind == next_spec.kind

    backend = _ReplacingBackend()
    parent = _FakeBinding(spec=_badge_spec(node_id=_node_id(99)), label="parent")
    owner = UiOwnerCommitState(owner_id=_OWNER_SLOT)
    reconcile_owner(owner, (_button_spec(node_id=_node_id(1)),), backend=backend, parent_binding=parent)
    old_node = owner.mounted_nodes[0]

    reconcile_owner(owner, (_badge_spec(node_id=_node_id(1), text="Now badge"),), backend=backend, parent_binding=parent)

    assert backend.create_calls == ["button", "badge"]
    assert old_node.binding.disposed is True
    assert owner.mounted_nodes[0].spec.kind == "badge"


def test_reconcile_owner_removes_missing_nodes_and_disposes_them() -> None:
    backend = _FakeBackend()
    parent = _FakeBinding(spec=_badge_spec(node_id=_node_id(99)), label="parent")
    owner = UiOwnerCommitState(owner_id=_OWNER_SLOT)
    reconcile_owner(
        owner,
        (
            _button_spec(node_id=_node_id(1)),
            _button_spec(node_id=_node_id(2)),
        ),
        backend=backend,
        parent_binding=parent,
    )
    removed = owner.mounted_nodes[1]

    reconcile_owner(owner, (_button_spec(node_id=_node_id(1)),), backend=backend, parent_binding=parent)

    assert removed.binding.disposed is True
    assert [node.spec.node_id for node in owner.mounted_nodes] == [_node_id(1)]
    assert [node.spec.node_id for node in parent.attached] == [_node_id(1)]


def test_reconcile_owner_rolls_back_to_previous_specs_on_failure() -> None:
    backend = _FakeBackend()
    parent = _FakeBinding(spec=_badge_spec(node_id=_node_id(99)), label="parent")
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
                _badge_spec(node_id=_node_id(2), text="Explode"),
            ),
            backend=backend,
            parent_binding=parent,
        )

    assert [node.spec.kind for node in owner.mounted_nodes] == ["button", "button"]
    assert [node.spec.node_id for node in parent.attached] == [_node_id(1), _node_id(2)]
