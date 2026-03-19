"""Committed context-graph capture and diff helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from pyrolyze.api import UIElement
from pyrolyze.runtime.context import ComponentCallSlotContext, ContainerSlotContext, ContextBase, RenderContext, SlotContext, SlotId


@dataclass(frozen=True, slots=True)
class ContextVisitRecord:
    kind: str
    slot_id: SlotId | None
    generation_id: int


@dataclass(frozen=True, slots=True)
class UiVisitRecord:
    slot_id: SlotId | None
    render_owner_slot_id: SlotId | None
    generation_id: int
    element: UIElement


class ContextGraphListener(Protocol):
    def open_context(self, context: ContextVisitRecord) -> None: ...

    def close_context(self, context: ContextVisitRecord) -> None: ...

    def add_ui_element(self, element: UiVisitRecord) -> None: ...


@dataclass(frozen=True, slots=True)
class CapturedUiElement:
    slot_id: SlotId | None
    render_owner_slot_id: SlotId | None
    generation_id: int
    element: UIElement


@dataclass(frozen=True, slots=True)
class CapturedContext:
    kind: str
    slot_id: SlotId | None
    generation_id: int
    children: tuple["CapturedContext", ...]
    ui: tuple[CapturedUiElement, ...]


@dataclass(frozen=True, slots=True)
class CapturedContextGraph:
    generation_id: int
    root: CapturedContext


@dataclass(frozen=True, slots=True)
class ContextChange:
    path: tuple[SlotId, ...]
    before: CapturedContext
    after: CapturedContext


@dataclass(frozen=True, slots=True)
class CapturedContextAtPath:
    path: tuple[SlotId, ...]
    context: CapturedContext


@dataclass(frozen=True, slots=True)
class CapturedUiElementAtPath:
    context_path: tuple[SlotId, ...]
    index: int
    ui: CapturedUiElement


@dataclass(frozen=True, slots=True)
class ContextGraphDiff:
    generation_before: int
    generation_after: int
    changed_contexts: tuple[ContextChange, ...]
    added_contexts: tuple[CapturedContextAtPath, ...]
    removed_contexts: tuple[CapturedContextAtPath, ...]
    added_ui: tuple[CapturedUiElementAtPath, ...]
    removed_ui: tuple[CapturedUiElementAtPath, ...]


@dataclass(slots=True)
class _MutableContext:
    record: ContextVisitRecord
    children: list[CapturedContext] = field(default_factory=list)
    ui: list[CapturedUiElement] = field(default_factory=list)


class ContextGraphCaptureListener:
    def __init__(self) -> None:
        self._stack: list[_MutableContext] = []
        self._root: CapturedContext | None = None

    def open_context(self, context: ContextVisitRecord) -> None:
        self._stack.append(_MutableContext(record=context))

    def close_context(self, context: ContextVisitRecord) -> None:
        current = self._stack.pop()
        if current.record != context:
            raise RuntimeError("context close order mismatch")
        captured = CapturedContext(
            kind=context.kind,
            slot_id=context.slot_id,
            generation_id=context.generation_id,
            children=tuple(current.children),
            ui=tuple(current.ui),
        )
        if self._stack:
            self._stack[-1].children.append(captured)
        else:
            self._root = captured

    def add_ui_element(self, element: UiVisitRecord) -> None:
        if not self._stack:
            raise RuntimeError("ui element recorded without an open context")
        self._stack[-1].ui.append(
            CapturedUiElement(
                slot_id=element.slot_id,
                render_owner_slot_id=element.render_owner_slot_id,
                generation_id=element.generation_id,
                element=element.element,
            )
        )

    def build(self) -> CapturedContextGraph:
        root = self._root
        if root is None:
            raise RuntimeError("no captured context graph")
        return CapturedContextGraph(generation_id=root.generation_id, root=root)


def capture_context_graph(context: RenderContext) -> CapturedContextGraph:
    listener = ContextGraphCaptureListener()
    walk_context_graph(context, listener)
    return listener.build()


def walk_context_graph(context: RenderContext, listener: ContextGraphListener) -> None:
    _walk_context_node(
        _LogicalContext(
            kind=context.context_kind(),
            slot_id=context.current_slot_id(),
            generation_id=context.current_generation_id(),
            own_ui=_own_ui_records(context),
            children=tuple(_logical_children(context)),
        ),
        listener,
        render_owner_slot_id=None,
    )


def compare_context_graphs(
    before: CapturedContextGraph,
    after: CapturedContextGraph,
) -> ContextGraphDiff:
    before_contexts = _flatten_contexts(before.root)
    after_contexts = _flatten_contexts(after.root)

    changed_contexts: list[ContextChange] = []
    added_contexts: list[CapturedContextAtPath] = []
    removed_contexts: list[CapturedContextAtPath] = []

    for path, before_context in before_contexts.items():
        after_context = after_contexts.get(path)
        if after_context is None:
            removed_contexts.append(CapturedContextAtPath(path=path, context=before_context))
            continue
        if _context_identity(before_context) != _context_identity(after_context):
            changed_contexts.append(ContextChange(path=path, before=before_context, after=after_context))

    for path, after_context in after_contexts.items():
        if path not in before_contexts:
            added_contexts.append(CapturedContextAtPath(path=path, context=after_context))

    before_ui = _flatten_ui(before.root)
    after_ui = _flatten_ui(after.root)
    added_ui: list[CapturedUiElementAtPath] = []
    removed_ui: list[CapturedUiElementAtPath] = []

    for path, before_element in before_ui.items():
        after_element = after_ui.get(path)
        if after_element is None:
            removed_ui.append(CapturedUiElementAtPath(context_path=path[0], index=path[1], ui=before_element))
            continue
        if before_element != after_element:
            removed_ui.append(CapturedUiElementAtPath(context_path=path[0], index=path[1], ui=before_element))
            added_ui.append(CapturedUiElementAtPath(context_path=path[0], index=path[1], ui=after_element))

    for path, after_element in after_ui.items():
        if path not in before_ui:
            added_ui.append(CapturedUiElementAtPath(context_path=path[0], index=path[1], ui=after_element))

    return ContextGraphDiff(
        generation_before=before.generation_id,
        generation_after=after.generation_id,
        changed_contexts=tuple(changed_contexts),
        added_contexts=tuple(added_contexts),
        removed_contexts=tuple(removed_contexts),
        added_ui=tuple(added_ui),
        removed_ui=tuple(removed_ui),
    )


@dataclass(frozen=True, slots=True)
class _LogicalContext:
    kind: str
    slot_id: SlotId | None
    generation_id: int
    own_ui: tuple[CapturedUiElement, ...]
    children: tuple["_LogicalContext", ...]


def _walk_context_node(
    context: _LogicalContext,
    listener: ContextGraphListener,
    *,
    render_owner_slot_id: SlotId | None,
) -> None:
    record = ContextVisitRecord(
        kind=context.kind,
        slot_id=context.slot_id,
        generation_id=context.generation_id,
    )
    listener.open_context(record)
    for element in context.own_ui:
        listener.add_ui_element(
            UiVisitRecord(
                slot_id=context.slot_id,
                render_owner_slot_id=render_owner_slot_id,
                generation_id=element.generation_id,
                element=element.element,
            )
        )

    next_render_owner = render_owner_slot_id
    if context.kind == "container":
        next_render_owner = context.slot_id

    for child in context.children:
        _walk_context_node(child, listener, render_owner_slot_id=next_render_owner)
    listener.close_context(record)


def _logical_children(context: ContextBase) -> list[_LogicalContext]:
    children: list[_LogicalContext] = []
    for child in context._children.values():
        if isinstance(child, ComponentCallSlotContext) and child.child_context is not None:
            children.append(
                _LogicalContext(
                    kind=child.context_kind(),
                    slot_id=child.current_slot_id(),
                    generation_id=child.current_generation_id(),
                    own_ui=_own_ui_records(child.child_context),
                    children=tuple(_logical_children(child.child_context)),
                )
            )
            continue
        if isinstance(child, ContextBase):
            children.append(
                _LogicalContext(
                    kind=child.context_kind(),
                    slot_id=child.current_slot_id(),
                    generation_id=child.current_generation_id(),
                    own_ui=_own_ui_records(child),
                    children=tuple(_logical_children(child)),
                )
            )
            continue
        if isinstance(child, SlotContext):
            children.append(
                _LogicalContext(
                    kind=child.context_kind(),
                    slot_id=child.current_slot_id(),
                    generation_id=child.current_generation_id(),
                    own_ui=(),
                    children=(),
                )
            )
    return children


def _own_ui_records(context: ContextBase) -> tuple[CapturedUiElement, ...]:
    committed_entries = getattr(context, "_own_committed_ui_entries", None)
    if committed_entries:
        return tuple(
            CapturedUiElement(
                slot_id=context.current_slot_id(),
                render_owner_slot_id=None,
                generation_id=entry.generation_id,
                element=entry.element,
            )
            for entry in committed_entries
        )
    return tuple(
        CapturedUiElement(
            slot_id=context.current_slot_id(),
            render_owner_slot_id=None,
            generation_id=context.current_generation_id(),
            element=element,
        )
        for element in context._own_committed_ui
    )


def _flatten_contexts(root: CapturedContext) -> dict[tuple[SlotId, ...], CapturedContext]:
    flattened: dict[tuple[SlotId, ...], CapturedContext] = {}

    def walk(node: CapturedContext, path: tuple[SlotId, ...]) -> None:
        flattened[path] = node
        for child in node.children:
            if child.slot_id is None:
                child_path = path
            else:
                child_path = path + (child.slot_id,)
            walk(child, child_path)

    walk(root, ())
    return flattened


def _flatten_ui(root: CapturedContext) -> dict[tuple[tuple[SlotId, ...], int], CapturedUiElement]:
    flattened: dict[tuple[tuple[SlotId, ...], int], CapturedUiElement] = {}

    def walk(node: CapturedContext, path: tuple[SlotId, ...]) -> None:
        for index, ui in enumerate(node.ui):
            flattened[(path, index)] = ui
        for child in node.children:
            if child.slot_id is None:
                child_path = path
            else:
                child_path = path + (child.slot_id,)
            walk(child, child_path)

    walk(root, ())
    return flattened


def _context_identity(context: CapturedContext) -> tuple[str, SlotId | None, int]:
    return (context.kind, context.slot_id, context.generation_id)


__all__ = [
    "CapturedContext",
    "CapturedContextAtPath",
    "CapturedContextGraph",
    "CapturedUiElement",
    "CapturedUiElementAtPath",
    "ContextChange",
    "ContextGraphCaptureListener",
    "ContextGraphDiff",
    "ContextGraphListener",
    "ContextVisitRecord",
    "UiVisitRecord",
    "capture_context_graph",
    "compare_context_graphs",
    "walk_context_graph",
]
