"""Private checkpoint: lifecycle-owned visitation and invalidation consumption."""

from __future__ import annotations

from dataclasses import dataclass

from .container_render import _ContainerRenderCompletion, _enable_container_render
from .render_context import RenderContextStateMgr


@dataclass(eq=False, slots=True)
class _PassStateRenderCompletion(_ContainerRenderCompletion):
    pass_state_selection_enabled = True


def _enable_pass_state_render(root: RenderContextStateMgr) -> None:
    _enable_container_render(root)
    root._field_only_completion = _PassStateRenderCompletion(root)
