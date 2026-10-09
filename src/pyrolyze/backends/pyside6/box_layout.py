"""Shared physical placement for Qt box-layout widget and layout mounts."""

from __future__ import annotations

from typing import Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QLayout, QLayoutItem, QWidget

from pyrolyze.backends.model import MountState
from pyrolyze.backends.mountable_engine import MountedMountableNode


def reconcile_box_layout_children(
    parent: QBoxLayout,
    children: list[MountedMountableNode],
    states: Mapping[tuple[object, ...], MountState],
) -> None:
    # Both mount routes share one index space. Keep the flattened authored order
    # rather than independently replaying each route's local indices.
    state_by_child = {
        id(reference.value): state
        for state in states.values()
        for reference in state.objects
    }
    ordered = [child.mountable for child in children if id(child.mountable) in state_by_child]
    items: dict[int, tuple[QLayoutItem, int]] = {}
    physical: list[object] = []
    for index in range(parent.count()):
        item = parent.itemAt(index)
        child = item.widget() if item.widget() is not None else item.layout()
        if child is None:
            raise ValueError("box-layout child placement does not support unmanaged spacer items")
        items[id(child)] = (item, parent.stretch(index))
        physical.append(child)
    same_order = len(physical) == len(ordered) and all(
        current is desired for current, desired in zip(physical, ordered, strict=True)
    )
    if not same_order:
        # Reverse removal avoids repeated front-removal shifts. Reuse layout
        # items, preserving nested layout ownership and widget identity.
        for index in range(parent.count() - 1, -1, -1):
            parent.takeAt(index)
        for child in ordered:
            existing = items.get(id(child))
            if existing is not None:
                parent.addItem(existing[0])
            elif isinstance(child, QWidget):
                parent.addWidget(child)
            elif isinstance(child, QLayout):
                parent.addLayout(child)
            else:
                raise TypeError(f"unsupported box-layout child {type(child).__name__}")
    for index, child in enumerate(ordered):
        state = state_by_child[id(child)]
        stretch = state.values.get("stretch")
        if stretch is None:
            existing = items.get(id(child))
            stretch = 0 if existing is None else existing[1]
        parent.setStretch(index, int(stretch))
        alignment = state.values.get("alignment")
        if alignment is not None:
            parent.itemAt(index).setAlignment(Qt.AlignmentFlag(alignment))
