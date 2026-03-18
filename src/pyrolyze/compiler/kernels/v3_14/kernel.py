from __future__ import annotations

from .detect import detect_module
from .eligibility import parse_module, should_transform_module
from .emit import emit_code, emit_module_ast, emit_source, exec_module_ast
from .plan import allocate_slot_ids, build_dirty_state_schema, build_transform_plan, infer_result_shape
from .rewrite import lower_component, lower_module_plan, lower_statement_group
from .validate import validate_generated_signatures, validate_module_ast, validate_plan, validate_provenance

__all__ = [
    "allocate_slot_ids",
    "build_dirty_state_schema",
    "build_transform_plan",
    "detect_module",
    "emit_code",
    "emit_module_ast",
    "emit_source",
    "exec_module_ast",
    "infer_result_shape",
    "lower_component",
    "lower_module_plan",
    "lower_statement_group",
    "parse_module",
    "should_transform_module",
    "validate_generated_signatures",
    "validate_module_ast",
    "validate_plan",
    "validate_provenance",
]
