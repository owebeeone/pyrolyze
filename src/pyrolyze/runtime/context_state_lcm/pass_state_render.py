"""Lifecycle-owned visitation and invalidation consumption."""

from __future__ import annotations

from dataclasses import dataclass

from .container_render import _ContainerRenderCompletion


@dataclass(eq=False, slots=True)
class _PassStateRenderCompletion(_ContainerRenderCompletion):
    pass_state_selection_enabled = True
