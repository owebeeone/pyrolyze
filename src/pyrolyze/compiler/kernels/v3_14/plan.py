from __future__ import annotations

import ast
import re

from ...artifacts import ComponentDetection, ComponentTransformPlan, DetectionResult, ModuleTransformPlan, ProvenanceRecord


def build_transform_plan(
    detection: DetectionResult,
    *,
    module_name: str,
) -> ModuleTransformPlan:
    component_plans = tuple(_build_component_plan(component) for component in detection.components)
    provenance_records = tuple(
        ProvenanceRecord(
            generated_symbol=component.generated_private_name,
            source_line=component.source_line,
            source_column=getattr(component.node, "col_offset", -1),
            reason="component_definition",
        )
        for component in component_plans
    )
    return ModuleTransformPlan(
        module_name=module_name,
        filename=detection.filename,
        module_ast=detection.module_ast,
        component_plans=component_plans,
        diagnostics=detection.diagnostics,
        provenance_records=provenance_records,
    )


def allocate_slot_ids(component: ComponentTransformPlan) -> dict[str, int]:
    del component
    return {}


def build_dirty_state_schema(component: ComponentTransformPlan) -> dict[str, str]:
    parameter_names = [argument.arg for argument in component.node.args.args]
    return {name: "bool" for name in parameter_names}


def infer_result_shape(target: ast.AST) -> object | None:
    if isinstance(target, ast.Tuple):
        return ("tuple", len(target.elts))
    return None


def _build_component_plan(component: ComponentDetection) -> ComponentTransformPlan:
    return ComponentTransformPlan(
        public_name=component.name,
        generated_private_name=_generated_private_name(component.name),
        node=component.node,
        hooks=component.hooks,
        kind="method" if "." in component.name else "function",
        source_line=int(getattr(component.node, "lineno", -1)),
        has_if=component.has_if,
        has_for=component.has_for,
    )


def _generated_private_name(component_name: str) -> str:
    normalized = re.sub(r"[^0-9a-zA-Z_]", "_", component_name.replace(".", "__"))
    return f"__pyr_{normalized}"
