from __future__ import annotations

from enum import StrEnum


class ContextKind(StrEnum):
    # Visitor/debug classification only.
    # This is not intended to drive runtime dispatch; the runtime should prefer
    # class polymorphism and explicit APIs for behavior. The graph visitor uses
    # this stable label to describe captured contexts without relying on Python
    # class names in the exported capture format.
    RENDER_ROOT = "render_root"
    COMPONENT_RENDER = "component_render"
    APP_CONTEXT_OVERRIDE = "app_context_override"
    CONTAINER = "container"
    SLOT_CALL = "slot_call"
    COMPONENT_CALL = "component_call"
    KEYED_LOOP = "keyed_loop"
    LOOP_ITEM = "loop_item"
    EVENT_HANDLER = "event_handler"
    LEAF = "leaf"
    SLOT = "slot"


__all__ = ["ContextKind"]
