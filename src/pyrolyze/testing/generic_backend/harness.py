"""Render harness for the generic testing backend."""

from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Any

from pyrolyze.api import EmittedNode, UIElement
from pyrolyze.backends.mountable_engine import MountedMountableNode
from pyrolyze.runtime import RenderContext, dirtyof

from .engine import PyroNodeEngine


@dataclass(frozen=True, slots=True)
class PyroRenderResult:
    ui_roots: tuple[EmittedNode, ...]
    mounted_roots: tuple[MountedMountableNode, ...]


class PyroRenderHarness:
    def __init__(
        self,
        *,
        engine: PyroNodeEngine,
        component: object,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        initial_generation: int,
    ) -> None:
        self._engine = engine
        self._component = component
        self._args = args
        self._kwargs = dict(kwargs)
        self._signature = inspect.signature(component)
        self._bound_args = self._bind_args(args, kwargs)
        self._render_context = RenderContext()
        self._generation = initial_generation
        self._mounted_roots: list[MountedMountableNode] = []
        self._result: PyroRenderResult | None = None
        self._mounted = False

    @property
    def generation(self) -> int:
        return self._generation

    def get(self) -> PyroRenderResult:
        if self._result is None:
            self._render_once(self._all_dirty_state())
        assert self._result is not None
        return self._result

    def run(self, *args: Any, generation: int | None = None, **kwargs: Any) -> PyroRenderHarness:
        if generation is None:
            self._generation += 1
        else:
            self._generation = generation
        if args or kwargs:
            next_bound_args = self._bind_args(args, kwargs)
            dirty_state = self._diff_dirty_state(self._bound_args, next_bound_args)
            self._args = args
            self._kwargs = dict(kwargs)
            self._bound_args = next_bound_args
        else:
            dirty_state = self._diff_dirty_state(self._bound_args, self._bound_args)
        self._render_once(dirty_state)
        return self

    def ui(self) -> object:
        from .snapshots import run_pyro_ui

        return run_pyro_ui(self.get())

    def graph(self) -> object:
        from .snapshots import run_pyro

        return run_pyro(self.get())

    def _render_once(self, dirty_state: object) -> None:
        callback = lambda: self._component._pyrolyze_meta._func(  # noqa: E731
            self._render_context,
            dirty_state,
            *self._args,
            **self._kwargs,
        )
        self._render_context.mount(callback)
        self._mounted = True
        committed = self._render_context.committed_ui()
        ui_roots = tuple(node for node in committed if isinstance(node, UIElement))
        self._mounted_roots = _reconcile_mounted_roots(
            engine=self._engine,
            roots=ui_roots,
            mounted_roots=self._mounted_roots,
            generation=self._generation,
        )
        self._result = PyroRenderResult(
            ui_roots=committed,
            mounted_roots=tuple(self._mounted_roots),
        )

    def _bind_args(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> inspect.BoundArguments:
        bound = self._signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    def _all_dirty_state(self) -> object:
        return dirtyof(**{name: True for name in self._bound_args.arguments})

    def _diff_dirty_state(
        self,
        previous: inspect.BoundArguments,
        current: inspect.BoundArguments,
    ) -> object:
        return dirtyof(
            **{
                name: previous.arguments.get(name) != current.arguments.get(name)
                for name in current.arguments
            }
        )


def _reconcile_mounted_roots(
    *,
    engine: PyroNodeEngine,
    roots: tuple[UIElement, ...],
    mounted_roots: list[MountedMountableNode],
    generation: int,
) -> list[MountedMountableNode]:
    next_roots: list[MountedMountableNode] = []
    for index, root in enumerate(roots):
        if index < len(mounted_roots):
            next_roots.append(
                engine.update(
                    mounted_roots[index],
                    root,
                    slot_id=("root", index),
                    call_site_id=index,
                    generation=generation,
                )
            )
            continue
        next_roots.append(
            engine.mount(
                root,
                slot_id=("root", index),
                call_site_id=index,
                generation=generation,
            )
        )
    return next_roots


__all__ = ["PyroRenderHarness", "PyroRenderResult"]
