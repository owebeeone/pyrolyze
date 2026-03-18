from __future__ import annotations

import ast
import copy
from dataclasses import dataclass

from ...artifacts import ComponentTransformPlan, ModuleTransformPlan
from ...diagnostics import error_from_node
from .builders import copy_reason_location


_PYROLYSE_DECORATORS = {"pyrolyse", "reactive_component"}


@dataclass(slots=True)
class _LoweringState:
    module_name: str
    slotted_helper_names: set[str]
    top_level_component_names: set[str]
    dirty_by_name: dict[str, ast.expr]
    in_class_scope: bool
    slot_index: int = 1

    def next_slot_id(self, *, reason: ast.AST) -> tuple[int, ast.Assign]:
        slot_index = self.slot_index
        self.slot_index += 1
        target = ast.Name(id=f"__pyr_slot_{slot_index}", ctx=ast.Store())
        value = ast.Call(
            func=_support_reference("__pyr_SlotId", in_class_scope=self.in_class_scope),
            args=[
                _support_reference("__pyr_module_id", in_class_scope=self.in_class_scope),
                ast.Constant(slot_index),
            ],
            keywords=[
                ast.keyword(
                    arg="line_no",
                    value=ast.Constant(getattr(reason, "lineno", None)),
                )
            ],
        )
        assign = ast.Assign(targets=[target], value=value)
        return slot_index, copy_reason_location(assign, reason)


def lower_module_plan(plan: ModuleTransformPlan) -> ast.Module:
    if not plan.component_plans:
        module_ast = copy.deepcopy(plan.module_ast)
        ast.fix_missing_locations(module_ast)
        return module_ast

    component_plans = {component.public_name: component for component in plan.component_plans}
    slotted_helper_names = _collect_slotted_helper_names(plan.module_ast)
    top_level_component_names = {
        component.public_name
        for component in plan.component_plans
        if "." not in component.public_name
    }

    new_body = _rewrite_body(
        plan.module_ast.body,
        component_plans=component_plans,
        slotted_helper_names=slotted_helper_names,
        top_level_component_names=top_level_component_names,
        module_name=plan.module_name,
        qual_prefix="",
    )
    new_body = _inject_module_scaffold(new_body)
    module_ast = ast.Module(
        body=new_body,
        type_ignores=copy.deepcopy(plan.module_ast.type_ignores),
    )
    ast.fix_missing_locations(module_ast)
    return module_ast


def lower_component(plan: ComponentTransformPlan) -> ast.FunctionDef | ast.AsyncFunctionDef:
    if isinstance(plan.node, ast.AsyncFunctionDef):
        raise error_from_node(
            plan.node,
            code="PYR-E-ASYNC-UNSUPPORTED",
            message="Phase 03 does not yet lower async @pyrolyse functions",
            module_name=plan.public_name,
            suggested_fix="rewrite_as_sync_phase3",
        )

    private_function, _wrapper = _lower_component_definition(
        plan,
        slotted_helper_names=set(),
        top_level_component_names=set(),
        module_name=plan.public_name,
        qual_prefix="",
    )
    ast.fix_missing_locations(private_function)
    return private_function


def lower_statement_group(group: list[ast.stmt]) -> list[ast.stmt]:
    lowered = copy.deepcopy(group)
    for statement in lowered:
        ast.fix_missing_locations(statement)
    return lowered


def _rewrite_body(
    body: list[ast.stmt],
    *,
    component_plans: dict[str, ComponentTransformPlan],
    slotted_helper_names: set[str],
    top_level_component_names: set[str],
    module_name: str,
    qual_prefix: str,
) -> list[ast.stmt]:
    rewritten: list[ast.stmt] = []
    for statement in body:
        if isinstance(statement, ast.ClassDef):
            class_copy = copy.deepcopy(statement)
            class_prefix = _qualified_name(qual_prefix, statement.name)
            class_copy.body = _rewrite_body(
                statement.body,
                component_plans=component_plans,
                slotted_helper_names=slotted_helper_names,
                top_level_component_names=top_level_component_names,
                module_name=module_name,
                qual_prefix=class_prefix,
            )
            rewritten.append(class_copy)
            continue

        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            qualified_name = _qualified_name(qual_prefix, statement.name)
            component_plan = component_plans.get(qualified_name)
            if component_plan is None:
                rewritten.append(copy.deepcopy(statement))
                continue
            private_function, wrapper = _lower_component_definition(
                component_plan,
                slotted_helper_names=slotted_helper_names,
                top_level_component_names=top_level_component_names,
                module_name=module_name,
                qual_prefix=qual_prefix,
            )
            rewritten.extend([private_function, wrapper])
            continue

        rewritten.append(copy.deepcopy(statement))

    return rewritten


def _lower_component_definition(
    plan: ComponentTransformPlan,
    *,
    slotted_helper_names: set[str],
    top_level_component_names: set[str],
    module_name: str,
    qual_prefix: str,
) -> tuple[ast.FunctionDef, ast.FunctionDef]:
    original = plan.node
    if isinstance(original, ast.AsyncFunctionDef):
        raise error_from_node(
            original,
            code="PYR-E-ASYNC-UNSUPPORTED",
            message="Phase 03 does not yet lower async @pyrolyse functions",
            module_name=module_name,
            suggested_fix="rewrite_as_sync_phase3",
        )

    private_function = copy.deepcopy(original)
    private_function.name = plan.generated_private_name
    private_function.decorator_list = []
    private_function.args = _private_args_for_component(original, qual_prefix=qual_prefix)
    private_function.body = [
        copy_reason_location(
            _build_pass_scope(
                _lower_component_body(
                    original,
                    slotted_helper_names=slotted_helper_names,
                    top_level_component_names=top_level_component_names,
                    module_name=module_name,
                    qual_prefix=qual_prefix,
                )
            ),
            original,
        )
    ]
    private_function.returns = None

    wrapper = copy.deepcopy(original)
    wrapper.decorator_list = _wrapper_decorators_for_component(original, plan)
    wrapper.body = [
        copy_reason_location(
            ast.Raise(
                exc=ast.Call(
                    func=_support_reference(
                        "__pyr_CallFromNonPyrolyzeContext",
                        in_class_scope=bool(qual_prefix),
                    ),
                    args=[ast.Constant(plan.public_name)],
                    keywords=[],
                ),
                cause=None,
            ),
            original,
        )
    ]

    ast.copy_location(private_function, original)
    ast.copy_location(wrapper, original)
    return private_function, wrapper


def _lower_component_body(
    component: ast.FunctionDef,
    *,
    slotted_helper_names: set[str],
    top_level_component_names: set[str],
    module_name: str,
    qual_prefix: str,
) -> list[ast.stmt]:
    state = _LoweringState(
        module_name=module_name,
        slotted_helper_names=slotted_helper_names,
        top_level_component_names=top_level_component_names,
        dirty_by_name=_initial_dirty_map(component, qual_prefix=qual_prefix),
        in_class_scope=bool(qual_prefix),
    )
    lowered: list[ast.stmt] = []
    for statement in component.body:
        lowered.extend(_lower_statement(statement, state=state))
    if not lowered:
        lowered.append(ast.Pass())
    return lowered


def _lower_statement(statement: ast.stmt, *, state: _LoweringState) -> list[ast.stmt]:
    if isinstance(statement, ast.Pass):
        return []
    if isinstance(statement, ast.Return) and statement.value is None:
        return []
    if isinstance(statement, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try, ast.Match)):
        raise error_from_node(
            statement,
            code="PYR-E-PHASE3-STRUCTURE",
            message="Phase 03 only supports straight-line @pyrolyse bodies",
            module_name=state.module_name,
            suggested_fix="defer_to_phase4",
        )
    if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_reactive_component(statement):
        raise error_from_node(
            statement,
            code="PYR-E-PHASE3-NESTED-COMPONENT",
            message="Phase 03 does not yet lower nested @pyrolyse definitions",
            module_name=state.module_name,
            suggested_fix="defer_to_later_phase",
        )
    if isinstance(statement, ast.Assign):
        return _lower_assign(statement, state=state)
    if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
        return _lower_expr_call(statement, state=state)

    return [copy.deepcopy(statement)]


def _lower_assign(statement: ast.Assign, *, state: _LoweringState) -> list[ast.stmt]:
    if len(statement.targets) != 1:
        return [copy.deepcopy(statement)]

    target = statement.targets[0]
    if isinstance(statement.value, ast.Call) and _is_slotted_helper_call(statement.value, state.slotted_helper_names):
        return _lower_slotted_assign(statement, target=target, call=statement.value, state=state)

    lowered = [copy.deepcopy(statement)]
    if isinstance(target, ast.Name):
        dirty_expr = _dirty_expr_for_value(statement.value, state.dirty_by_name)
        if _is_false_expr(dirty_expr):
            state.dirty_by_name[target.id] = ast.Constant(False)
        else:
            dirty_name = _dirty_name_for(target.id)
            lowered.append(
                copy_reason_location(
                    ast.Assign(
                        targets=[ast.Name(id=dirty_name, ctx=ast.Store())],
                        value=dirty_expr,
                    ),
                    statement,
                )
            )
            state.dirty_by_name[target.id] = ast.Name(id=dirty_name, ctx=ast.Load())

    ast.copy_location(lowered[0], statement)
    return lowered


def _lower_slotted_assign(
    statement: ast.Assign,
    *,
    target: ast.expr,
    call: ast.Call,
    state: _LoweringState,
) -> list[ast.stmt]:
    _slot_index, slot_assign = state.next_slot_id(reason=statement)
    slot_name = ast.Name(id=slot_assign.targets[0].id, ctx=ast.Load())
    call_expr = ast.Call(
        func=ast.Attribute(value=ast.Name(id="ctx", ctx=ast.Load()), attr="call_plain", ctx=ast.Load()),
        args=[slot_name, copy.deepcopy(call.func), *[copy.deepcopy(arg) for arg in call.args]],
        keywords=[copy.deepcopy(keyword) for keyword in call.keywords],
    )

    names = _bound_names(target)
    if len(names) == 1 and isinstance(target, ast.Name):
        dirty_name = _dirty_name_for(names[0])
        lowered_assign = ast.Assign(
            targets=[
                ast.Tuple(
                    elts=[
                        ast.Name(id=dirty_name, ctx=ast.Store()),
                        ast.Name(id=target.id, ctx=ast.Store()),
                    ],
                    ctx=ast.Store(),
                )
            ],
            value=call_expr,
        )
        state.dirty_by_name[target.id] = ast.Name(id=dirty_name, ctx=ast.Load())
    elif isinstance(target, ast.Tuple) and all(isinstance(element, ast.Name) for element in target.elts):
        dirty_tuple = ast.Tuple(
            elts=[ast.Name(id=_dirty_name_for(name), ctx=ast.Store()) for name in names],
            ctx=ast.Store(),
        )
        value_tuple = ast.Tuple(
            elts=[ast.Name(id=name, ctx=ast.Store()) for name in names],
            ctx=ast.Store(),
        )
        call_expr.keywords.append(
            ast.keyword(
                arg="result_shape",
                value=ast.Tuple(
                    elts=[ast.Constant("tuple"), ast.Constant(len(names))],
                    ctx=ast.Load(),
                ),
            )
        )
        lowered_assign = ast.Assign(
            targets=[ast.Tuple(elts=[dirty_tuple, value_tuple], ctx=ast.Store())],
            value=call_expr,
        )
        for name in names:
            state.dirty_by_name[name] = ast.Name(id=_dirty_name_for(name), ctx=ast.Load())
    else:
        raise error_from_node(
            statement,
            code="PYR-E-PHASE3-DESTRUCTURE",
            message="Phase 03 only supports name and tuple-name slotted assignments",
            module_name=state.module_name,
            suggested_fix="simplify_assignment_shape",
        )

    return [slot_assign, copy_reason_location(lowered_assign, statement)]


def _lower_expr_call(statement: ast.Expr, *, state: _LoweringState) -> list[ast.stmt]:
    call = statement.value
    if _is_call_native_expr(call):
        raise error_from_node(
            statement,
            code="PYR-E-PHASE3-CALL-NATIVE",
            message="Phase 03 does not yet lower call_native(...) emitters",
            module_name=state.module_name,
            suggested_fix="defer_to_later_phase",
        )

    call_name = _call_name(call)
    if call_name in state.top_level_component_names:
        raise error_from_node(
            statement,
            code="PYR-E-PHASE3-COMPONENT-CALL",
            message="Phase 03 does not yet lower statement-position @pyrolyse calls",
            module_name=state.module_name,
            suggested_fix="defer_to_later_phase",
        )

    _slot_index, slot_assign = state.next_slot_id(reason=statement)
    slot_name = ast.Name(id=slot_assign.targets[0].id, ctx=ast.Load())
    dirty_parts = [
        _dirty_expr_for_value(call.func, state.dirty_by_name),
        *[_dirty_expr_for_value(arg, state.dirty_by_name) for arg in call.args],
        *[_dirty_expr_for_value(keyword.value, state.dirty_by_name) for keyword in call.keywords],
    ]
    guard_parts = [expr for expr in dirty_parts if not _is_false_expr(expr)]
    guard_parts.append(
        ast.Call(
            func=ast.Attribute(value=ast.Name(id="ctx", ctx=ast.Load()), attr="visit_slot_and_dirty", ctx=ast.Load()),
            args=[slot_name],
            keywords=[],
        )
    )
    leaf_call = ast.Expr(
        value=ast.Call(
            func=ast.Attribute(value=ast.Name(id="ctx", ctx=ast.Load()), attr="leaf_call", ctx=ast.Load()),
            args=[slot_name, copy.deepcopy(call.func), *[copy.deepcopy(arg) for arg in call.args]],
            keywords=[copy.deepcopy(keyword) for keyword in call.keywords],
        )
    )
    if_statement = ast.If(
        test=_or_expression(guard_parts),
        body=[leaf_call],
        orelse=[],
    )
    return [slot_assign, copy_reason_location(if_statement, statement)]


def _inject_module_scaffold(body: list[ast.stmt]) -> list[ast.stmt]:
    if not body:
        return body

    insert_at = 1 if _is_module_docstring(body[0]) else 0
    scaffold = [
        ast.ImportFrom(
            module="pyrolyze.api",
            names=[
                ast.alias(name="CallFromNonPyrolyzeContext", asname="__pyr_CallFromNonPyrolyzeContext"),
                ast.alias(name="ComponentMetadata", asname="__pyr_ComponentMetadata"),
                ast.alias(name="pyrolyze_component_ref", asname="__pyr_component_ref"),
            ],
            level=0,
        ),
        ast.ImportFrom(
            module="pyrolyze.runtime",
            names=[
                ast.alias(name="SlotId", asname="__pyr_SlotId"),
                ast.alias(name="module_registry", asname="__pyr_module_registry"),
            ],
            level=0,
        ),
        ast.Assign(
            targets=[ast.Name(id="__pyr_module_id", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="__pyr_module_registry", ctx=ast.Load()),
                    attr="module_id",
                    ctx=ast.Load(),
                ),
                args=[ast.Name(id="__name__", ctx=ast.Load())],
                keywords=[],
            ),
        ),
    ]
    return [*body[:insert_at], *scaffold, *body[insert_at:]]


def _private_args_for_component(
    original: ast.FunctionDef,
    *,
    qual_prefix: str,
) -> ast.arguments:
    args = copy.deepcopy(original.args)
    ctx_arg = ast.arg(arg="ctx")
    dirty_arg = ast.arg(arg="__pyr_dirty_state")
    method_kind = _method_kind(original, qual_prefix=qual_prefix)
    if method_kind in {"instance", "class"} and args.args:
        args.args = [args.args[0], ctx_arg, dirty_arg, *args.args[1:]]
    else:
        args.args = [ctx_arg, dirty_arg, *args.args]
    return args


def _wrapper_decorators_for_component(
    original: ast.FunctionDef,
    plan: ComponentTransformPlan,
) -> list[ast.expr]:
    in_class_scope = "." in plan.public_name
    remaining = [
        copy.deepcopy(decorator)
        for decorator in original.decorator_list
        if _decorator_name(decorator) not in _PYROLYSE_DECORATORS
    ]
    remaining.append(
        ast.Call(
            func=_support_reference("__pyr_component_ref", in_class_scope=in_class_scope),
            args=[
                ast.Call(
                    func=_support_reference("__pyr_ComponentMetadata", in_class_scope=in_class_scope),
                    args=[
                        ast.Constant(plan.public_name),
                        ast.Name(id=plan.generated_private_name, ctx=ast.Load()),
                    ],
                    keywords=[],
                )
            ],
            keywords=[],
        )
    )
    return remaining


def _build_pass_scope(body: list[ast.stmt]) -> ast.With:
    return ast.With(
        items=[
            ast.withitem(
                context_expr=ast.Call(
                    func=ast.Attribute(value=ast.Name(id="ctx", ctx=ast.Load()), attr="pass_scope", ctx=ast.Load()),
                    args=[],
                    keywords=[],
                ),
                optional_vars=None,
            )
        ],
        body=body,
    )


def _initial_dirty_map(
    component: ast.FunctionDef,
    *,
    qual_prefix: str,
) -> dict[str, ast.expr]:
    method_kind = _method_kind(component, qual_prefix=qual_prefix)
    args = list(component.args.args)
    if method_kind in {"instance", "class"} and args:
        args = args[1:]
    source_args = [*component.args.posonlyargs, *args, *component.args.kwonlyargs]
    return {
        argument.arg: ast.Attribute(
            value=ast.Name(id="__pyr_dirty_state", ctx=ast.Load()),
            attr=argument.arg,
            ctx=ast.Load(),
        )
        for argument in source_args
    }


def _dirty_expr_for_value(value: ast.AST, dirty_by_name: dict[str, ast.expr]) -> ast.expr:
    dirty_parts: list[ast.expr] = []
    seen_names: set[str] = set()
    for node in ast.walk(value):
        if not isinstance(node, ast.Name):
            continue
        dirty_expr = dirty_by_name.get(node.id)
        if dirty_expr is None or node.id in seen_names:
            continue
        seen_names.add(node.id)
        dirty_parts.append(copy.deepcopy(dirty_expr))
    return _or_expression(dirty_parts)


def _or_expression(expressions: list[ast.expr]) -> ast.expr:
    filtered = [expression for expression in expressions if not _is_false_expr(expression)]
    if not filtered:
        return ast.Constant(False)
    if len(filtered) == 1:
        return filtered[0]
    return ast.BoolOp(op=ast.Or(), values=filtered)


def _bound_names(target: ast.expr) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, ast.Tuple):
        names: list[str] = []
        for element in target.elts:
            if not isinstance(element, ast.Name):
                raise TypeError("only simple tuple-name destructuring is supported")
            names.append(element.id)
        return names
    raise TypeError("unsupported assignment target")


def _dirty_name_for(name: str) -> str:
    return f"__pyr_{name}_dirty"


def _is_false_expr(expression: ast.expr) -> bool:
    return isinstance(expression, ast.Constant) and expression.value is False


def _collect_slotted_helper_names(module_ast: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(module_ast):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_pyrolyze_slotted(node):
            names.add(node.name)
    return names


def _is_slotted_helper_call(call: ast.Call, slotted_helper_names: set[str]) -> bool:
    call_name = _call_name(call)
    return call_name is not None and call_name in slotted_helper_names


def _is_call_native_expr(call: ast.Call) -> bool:
    return isinstance(call.func, ast.Call) and _call_name(call.func) == "call_native"


def _method_kind(node: ast.FunctionDef, *, qual_prefix: str) -> str:
    if not qual_prefix:
        return "top_level"
    decorator_names = {_decorator_name(decorator) for decorator in node.decorator_list}
    if "staticmethod" in decorator_names:
        return "static"
    if "classmethod" in decorator_names:
        return "class"
    return "instance"


def _qualified_name(prefix: str, name: str) -> str:
    if not prefix:
        return name
    return f"{prefix}.{name}"


def _is_module_docstring(statement: ast.stmt) -> bool:
    return isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str)


def _is_reactive_component(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(_decorator_name(decorator) in _PYROLYSE_DECORATORS for decorator in node.decorator_list)


def _is_pyrolyze_slotted(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(_decorator_name(decorator) == "pyrolyze_slotted" for decorator in node.decorator_list)


def _decorator_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _call_name(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _support_reference(name: str, *, in_class_scope: bool) -> ast.expr:
    if not in_class_scope:
        return ast.Name(id=name, ctx=ast.Load())
    return ast.Subscript(
        value=ast.Call(func=ast.Name(id="globals", ctx=ast.Load()), args=[], keywords=[]),
        slice=ast.Constant(name),
        ctx=ast.Load(),
    )
