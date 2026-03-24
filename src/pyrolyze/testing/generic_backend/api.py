"""Top-level builder for the generic testing backend."""

from __future__ import annotations

import inspect
import sys
import types
from typing import Any

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    MountSelector,
    UIElement,
    pyrolyze_component_ref,
)
from pyrolyze.compiler import load_transformed_namespace

from .engine import PyroNodeEngine
from .harness import PyroRenderHarness
from .runtime import build_runtime_types
from .sourcegen import build_source_module_text
from .specs import NodeGenSpec, ParamSpec, validate_node_specs

class BuildPyroNodeBackend:
    def __init__(
        self,
        node_specs: tuple[NodeGenSpec, ...] | list[NodeGenSpec],
        *,
        module_name: str = "pyrolyze.testing.generic_backend.generated",
    ) -> None:
        self.node_specs = validate_node_specs(node_specs)
        self.module_name = module_name
        self._runtime_types = build_runtime_types(self.node_specs)
        self._direct_funcs = {
            spec.name: _build_direct_component_ref(spec)
            for spec in self.node_specs
        }
        self._selector_families = {
            mount.name: MountSelector.named(mount.name)
            for spec in self.node_specs
            for mount in spec.mounts
        }
        self._source_text: str | None = None
        self._source_namespace: dict[str, object] | None = None

    def pyro_func(self, name: str) -> object:
        return self._direct_funcs[name]

    def pyro_class(self, name: str) -> type[object]:
        return self._runtime_types[name]

    def selector_family(self, name: str) -> MountSelector:
        return self._selector_families[name]

    def engine(
        self,
        *,
        initial_generation: int = 0,
        strict_compatibility: bool = True,
    ) -> PyroNodeEngine:
        return PyroNodeEngine(
            self.node_specs,
            initial_generation=initial_generation,
            strict_compatibility=strict_compatibility,
        )

    def context(
        self,
        component: object,
        *args: Any,
        initial_generation: int = 0,
        **kwargs: Any,
    ) -> PyroRenderHarness:
        return PyroRenderHarness(
            engine=self.engine(initial_generation=initial_generation),
            component=component,
            args=args,
            kwargs=kwargs,
            initial_generation=initial_generation,
        )

    def source_module_text(self) -> str:
        if self._source_text is None:
            self._source_text = build_source_module_text(self.node_specs)
        return self._source_text

    def source_namespace(self) -> dict[str, object]:
        if self._source_namespace is None:
            module_name = self.module_name
            filename = f"/virtual/{module_name.replace('.', '/')}.py"
            namespace = load_transformed_namespace(
                self.source_module_text(),
                module_name=module_name,
                filename=filename,
            )
            module = types.ModuleType(module_name)
            module.__dict__.update(namespace)
            sys.modules[module_name] = module
            self._source_namespace = namespace
        return self._source_namespace


def _build_direct_component_ref(spec: NodeGenSpec) -> object:
    signature = _signature_for_constructor(spec.constructor)
    annotations = {
        param.name: _annotation_expr(param)
        for param in spec.constructor
    }
    annotations["return"] = "None"

    def direct_impl(ctx: object, dirty_state: object, *args: Any, **kwargs: Any) -> None:
        del dirty_state
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        with ctx.pass_scope():
            ctx.call_native(
                UIElement,
                kind=spec.name,
                props=dict(bound.arguments),
            )

    def direct_ref(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise CallFromNonPyrolyzeContext(spec.name)

    direct_ref.__name__ = spec.name
    direct_ref.__qualname__ = spec.name
    direct_ref.__annotations__ = annotations
    direct_ref.__signature__ = signature
    direct_ref.__doc__ = f"Direct generic backend helper for {spec.name!r}."
    return pyrolyze_component_ref(ComponentMetadata(spec.name, direct_impl))(direct_ref)


def _signature_for_constructor(params: tuple[ParamSpec, ...]) -> inspect.Signature:
    signature_params = [
        inspect.Parameter(
            name=param.name,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=(
                inspect._empty
                if param.default_repr is None
                else eval(param.default_repr, {}, {})
            ),
            annotation=_annotation_expr(param),
        )
        for param in params
    ]
    return inspect.Signature(parameters=signature_params, return_annotation="None")


def _annotation_expr(param: ParamSpec) -> str:
    return "object" if param.annotation is None else param.annotation.expr


__all__ = ["BuildPyroNodeBackend"]
