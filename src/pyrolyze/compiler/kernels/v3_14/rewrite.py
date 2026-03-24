from __future__ import annotations

import ast
import copy
import importlib
import inspect
from dataclasses import dataclass, field
from typing import Annotated, Any, cast, get_args, get_origin, get_type_hints

from ...artifacts import ComponentTransformPlan, ModuleTransformPlan
from ...diagnostics import error_from_node
from .builders import copy_reason_location


_REACTIVE_DECORATORS = {"pyrolyze", "reactive_component"}
_SLOTTED_DECORATORS = {"pyrolyze_slotted"}
_EVENT_HANDLER_TYPES = {"PyrolyzeHandler", "PyrolyteHandler"}
_MOUNT_HELPERS = {"mount"}
_APP_CONTEXT_OVERRIDE_HELPER = "app_context_override"
_CALLABLE_KIND_COMPONENT_REF = "component_ref"
_CALLABLE_KIND_SLOT_CALLABLE = "slot_callable"
_CALLABLE_KIND_PLAIN_CALLABLE = "plain_callable"


@dataclass(slots=True)
class _LoweringShared:
    slot_index: int = 1
    call_site_index: int = 1
    hoist_slots: bool = True
    slot_declarations: list[ast.Assign] = field(default_factory=list)


@dataclass(slots=True)
class _LoweringState:
    module_name: str
    reactive_decorator_names: set[str]
    slotted_helper_names: set[str]
    top_level_component_names: set[str]
    component_param_names: dict[str, tuple[str, ...]]
    component_event_params: dict[str, frozenset[str]]
    callable_kinds: dict[str, str]
    callable_return_kinds: dict[str, str]
    legacy_container_names: set[str]
    mount_helper_names: set[str]
    event_handler_type_names: set[str]
    dirty_by_name: dict[str, ast.expr]
    in_class_scope: bool
    context_name: str
    shared: _LoweringShared

    def next_slot_id(self, *, reason: ast.AST) -> tuple[int, ast.expr, list[ast.stmt]]:
        slot_index = self.shared.slot_index
        self.shared.slot_index += 1
        slot_name = f"__pyr_slot_{slot_index}"
        target = ast.Name(id=slot_name, ctx=ast.Store())
        value = ast.Call(
            func=ast.Name(id="__pyr_SlotId", ctx=ast.Load()),
            args=[
                ast.Name(id="__pyr_module_id", ctx=ast.Load()),
                ast.Constant(slot_index),
            ],
            keywords=[
                ast.keyword(
                    arg="line_no",
                    value=ast.Constant(getattr(reason, "lineno", None)),
                ),
                ast.keyword(
                    arg="is_top_level",
                    value=ast.Constant(True),
                ),
            ],
        )
        assign = copy_reason_location(ast.Assign(targets=[target], value=value), reason)
        slot_ref = _support_reference(slot_name, in_class_scope=self.in_class_scope)
        if self.shared.hoist_slots:
            self.shared.slot_declarations.append(assign)
            return slot_index, slot_ref, []
        return slot_index, ast.Name(id=slot_name, ctx=ast.Load()), [assign]

    def context_ref(self) -> ast.Name:
        return ast.Name(id=self.context_name, ctx=ast.Load())

    def next_call_site_id(self, *, reason: ast.AST) -> int:
        _ = reason
        call_site_id = self.shared.call_site_index
        self.shared.call_site_index += 1
        return call_site_id

    def child(
        self,
        *,
        context_name: str | None = None,
        dirty_by_name: dict[str, ast.expr] | None = None,
    ) -> _LoweringState:
        return _LoweringState(
            module_name=self.module_name,
            reactive_decorator_names=self.reactive_decorator_names,
            slotted_helper_names=self.slotted_helper_names,
            top_level_component_names=self.top_level_component_names,
            component_param_names=self.component_param_names,
            component_event_params=self.component_event_params,
            callable_kinds=dict(self.callable_kinds),
            callable_return_kinds=self.callable_return_kinds,
            legacy_container_names=self.legacy_container_names,
            mount_helper_names=self.mount_helper_names,
            event_handler_type_names=self.event_handler_type_names,
            dirty_by_name=self.dirty_by_name if dirty_by_name is None else dirty_by_name,
            in_class_scope=self.in_class_scope,
            context_name=self.context_name if context_name is None else context_name,
            shared=self.shared,
        )


@dataclass(frozen=True, slots=True)
class _PackedNativeComponentSpec:
    factory: ast.expr
    kind_keyword: ast.keyword


def _collect_packed_native_helper_names(body: list[ast.stmt]) -> set[str]:
    return {
        statement.name
        for statement in body
        if isinstance(statement, ast.FunctionDef) and _is_packed_native_helper(statement)
    }


def _is_packed_native_helper(function: ast.FunctionDef) -> bool:
    if function.name != "__element":
        return False
    if function.args.vararg is not None or function.args.kwarg is not None:
        return False
    if len(function.args.kwonlyargs) != 2:
        return False
    kind_arg, kwds_arg = function.args.kwonlyargs
    if kind_arg.arg != "kind" or kwds_arg.arg != "kwds":
        return False
    return _is_dict_annotation(kwds_arg.annotation)


def _is_dict_annotation(annotation: ast.expr | None) -> bool:
    if annotation is None:
        return False
    if isinstance(annotation, ast.Name):
        return annotation.id in {"dict", "Dict"}
    if isinstance(annotation, ast.Subscript):
        return _is_dict_annotation(annotation.value)
    if isinstance(annotation, ast.Attribute):
        return annotation.attr == "Dict"
    return False


def _packed_native_component_spec(
    original: ast.FunctionDef,
    *,
    packed_native_helper_names: set[str],
    qual_prefix: str,
) -> _PackedNativeComponentSpec | None:
    if len(original.body) != 1 or not isinstance(original.body[0], ast.Expr):
        return None
    call = original.body[0].value
    if not isinstance(call, ast.Call) or not _is_call_native_expr(call):
        return None
    if call.args:
        return None
    if not isinstance(call.func, ast.Call) or not call.func.args:
        return None
    factory = call.func.args[0]
    if not _is_packed_native_factory(factory, packed_native_helper_names=packed_native_helper_names):
        return None

    param_names = set(_function_parameter_names(original, qual_prefix=qual_prefix))
    kind_keyword: ast.keyword | None = None
    for keyword in call.keywords:
        if keyword.arg == "kind":
            kind_keyword = copy.deepcopy(keyword)
            continue
        if keyword.arg is None:
            return None
        if keyword.arg not in param_names:
            return None
        if not isinstance(keyword.value, ast.Name) or keyword.value.id != keyword.arg:
            return None
    if kind_keyword is None:
        return None
    return _PackedNativeComponentSpec(factory=copy.deepcopy(factory), kind_keyword=kind_keyword)


def _is_packed_native_factory(
    factory: ast.expr,
    *,
    packed_native_helper_names: set[str],
) -> bool:
    if isinstance(factory, ast.Name):
        return factory.id in packed_native_helper_names
    if isinstance(factory, ast.Attribute):
        return factory.attr in packed_native_helper_names
    return False


def _function_parameter_names(function: ast.FunctionDef, *, qual_prefix: str) -> tuple[str, ...]:
    args = list(function.args.args)
    if _method_kind(function, qual_prefix=qual_prefix) in {"instance", "class"} and args:
        args = args[1:]
    source_args = [*function.args.posonlyargs, *args, *function.args.kwonlyargs]
    return tuple(argument.arg for argument in source_args)


def _next_call_site_id(shared: _LoweringShared) -> int:
    call_site_id = shared.call_site_index
    shared.call_site_index += 1
    return call_site_id


def _lower_packed_native_component_body(
    original: ast.FunctionDef,
    *,
    factory: ast.expr,
    kind_keyword: ast.keyword,
    state_call_site_shared: _LoweringShared,
) -> list[ast.stmt]:
    call_site_id = _next_call_site_id(state_call_site_shared)
    lowered = ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="__pyr_ctx", ctx=ast.Load()),
                attr="call_native",
                ctx=ast.Load(),
            ),
            args=[copy.deepcopy(factory)],
            keywords=[
                copy.deepcopy(kind_keyword),
                ast.keyword(
                    arg="kwds",
                    value=ast.Name(id="kwds", ctx=ast.Load()),
                ),
                ast.keyword(arg="__pyr_call_site_id", value=ast.Constant(call_site_id)),
            ],
        )
    )
    return [copy_reason_location(lowered, original)]


def lower_module_plan(plan: ModuleTransformPlan) -> ast.Module:
    if not plan.component_plans:
        module_ast = copy.deepcopy(plan.module_ast)
        ast.fix_missing_locations(module_ast)
        return module_ast

    reactive_decorator_names, slotted_decorator_names, event_handler_type_names = _collect_source_api_aliases(
        plan.module_ast
    )
    mount_helper_names = _collect_mount_helper_names(plan.module_ast)
    shared = _LoweringShared(hoist_slots=True)
    component_plans = {component.public_name: component for component in plan.component_plans}
    (
        imported_slotted_names,
        imported_component_names,
        imported_component_param_names,
        imported_component_event_params,
        imported_return_kinds,
    ) = _collect_imported_annotated_symbols(plan.module_ast)
    slotted_helper_names = _collect_slotted_helper_names(
        plan.module_ast,
        slotted_decorator_names=slotted_decorator_names,
    )
    slotted_helper_names.update(imported_slotted_names)
    component_param_names = {
        component.public_name: _component_parameter_names(component)
        for component in plan.component_plans
    }
    component_param_names.update(imported_component_param_names)
    component_event_params = {
        component.public_name: _parameter_event_names(
            component.node,
            event_handler_type_names=event_handler_type_names,
        )
        for component in plan.component_plans
    }
    component_event_params.update(imported_component_event_params)
    callable_return_kinds = _collect_local_callable_return_kinds(plan.module_ast)
    callable_return_kinds.update(imported_return_kinds)
    top_level_component_names = {
        component.public_name
        for component in plan.component_plans
        if "." not in component.public_name
    }
    top_level_component_names.update(imported_component_names)
    legacy_container_names = _collect_legacy_container_names(plan.module_ast)

    new_body = _rewrite_body(
        plan.module_ast.body,
        component_plans=component_plans,
        reactive_decorator_names=reactive_decorator_names,
        slotted_helper_names=slotted_helper_names,
        top_level_component_names=top_level_component_names,
        component_param_names=component_param_names,
        component_event_params=component_event_params,
        callable_return_kinds=callable_return_kinds,
        legacy_container_names=legacy_container_names,
        mount_helper_names=mount_helper_names,
        event_handler_type_names=event_handler_type_names,
        module_name=plan.module_name,
        qual_prefix="",
        in_class_scope=False,
        shared=shared,
    )
    new_body = _inject_module_scaffold(new_body, slot_declarations=shared.slot_declarations)
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
            message="Phase 03 does not yet lower async @pyrolyze functions",
            module_name=plan.public_name,
            suggested_fix="rewrite_as_sync_phase3",
        )

    private_function, _wrapper = _lower_component_definition(
        plan,
        reactive_decorator_names=set(_REACTIVE_DECORATORS),
        slotted_helper_names=set(),
        top_level_component_names=set(),
        component_param_names={plan.public_name: _component_parameter_names(plan)},
        component_event_params={
            plan.public_name: _parameter_event_names(
                plan.node,
                event_handler_type_names=set(_EVENT_HANDLER_TYPES),
            )
        },
        callable_return_kinds={},
        legacy_container_names=set(),
        mount_helper_names=set(_MOUNT_HELPERS),
        event_handler_type_names=set(_EVENT_HANDLER_TYPES),
        packed_native_helper_names=set(),
        module_name=plan.public_name,
        qual_prefix="",
        in_class_scope=False,
        shared=_LoweringShared(hoist_slots=False),
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
    reactive_decorator_names: set[str],
    slotted_helper_names: set[str],
    top_level_component_names: set[str],
    component_param_names: dict[str, tuple[str, ...]],
    component_event_params: dict[str, frozenset[str]],
    callable_return_kinds: dict[str, str],
    legacy_container_names: set[str],
    mount_helper_names: set[str],
    event_handler_type_names: set[str],
    module_name: str,
    qual_prefix: str,
    in_class_scope: bool,
    shared: _LoweringShared,
) -> list[ast.stmt]:
    rewritten: list[ast.stmt] = []
    packed_native_helper_names = _collect_packed_native_helper_names(body)
    for statement in body:
        if isinstance(statement, ast.ClassDef):
            class_copy = copy.deepcopy(statement)
            class_prefix = _qualified_name(qual_prefix, statement.name)
            class_copy.body = _rewrite_body(
                statement.body,
                component_plans=component_plans,
                reactive_decorator_names=reactive_decorator_names,
                slotted_helper_names=slotted_helper_names,
                top_level_component_names=top_level_component_names,
                component_param_names=component_param_names,
                component_event_params=component_event_params,
                callable_return_kinds=callable_return_kinds,
                legacy_container_names=legacy_container_names,
                mount_helper_names=mount_helper_names,
                event_handler_type_names=event_handler_type_names,
                module_name=module_name,
                qual_prefix=class_prefix,
                in_class_scope=True,
                shared=shared,
            )
            rewritten.append(class_copy)
            continue

        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            qualified_name = _qualified_name(qual_prefix, statement.name)
            component_plan = component_plans.get(qualified_name)
            if component_plan is None:
                function_copy = copy.deepcopy(statement)
                function_copy.body = _rewrite_body(
                    statement.body,
                    component_plans=component_plans,
                    reactive_decorator_names=reactive_decorator_names,
                    slotted_helper_names=slotted_helper_names,
                    top_level_component_names=top_level_component_names,
                    component_param_names=component_param_names,
                    component_event_params=component_event_params,
                    callable_return_kinds=callable_return_kinds,
                    legacy_container_names=legacy_container_names,
                    mount_helper_names=mount_helper_names,
                    event_handler_type_names=event_handler_type_names,
                    module_name=module_name,
                    qual_prefix=f"{qualified_name}.<locals>",
                    in_class_scope=in_class_scope,
                    shared=shared,
                )
                rewritten.append(function_copy)
                continue
            private_function, wrapper = _lower_component_definition(
                component_plan,
                reactive_decorator_names=reactive_decorator_names,
                slotted_helper_names=slotted_helper_names,
                top_level_component_names=top_level_component_names,
                component_param_names=component_param_names,
                component_event_params=component_event_params,
                callable_return_kinds=callable_return_kinds,
                legacy_container_names=legacy_container_names,
                mount_helper_names=mount_helper_names,
                event_handler_type_names=event_handler_type_names,
                packed_native_helper_names=packed_native_helper_names,
                module_name=module_name,
                qual_prefix=qual_prefix,
                in_class_scope=in_class_scope,
                shared=shared,
            )
            rewritten.extend([private_function, wrapper])
            continue

        rewritten.append(copy.deepcopy(statement))

    return rewritten


def _lower_component_definition(
    plan: ComponentTransformPlan,
    *,
    reactive_decorator_names: set[str],
    slotted_helper_names: set[str],
    top_level_component_names: set[str],
    component_param_names: dict[str, tuple[str, ...]],
    component_event_params: dict[str, frozenset[str]],
    callable_return_kinds: dict[str, str],
    legacy_container_names: set[str],
    mount_helper_names: set[str],
    event_handler_type_names: set[str],
    packed_native_helper_names: set[str],
    module_name: str,
    qual_prefix: str,
    in_class_scope: bool,
    shared: _LoweringShared,
) -> tuple[ast.FunctionDef, ast.FunctionDef]:
    original = plan.node
    if isinstance(original, ast.AsyncFunctionDef):
        raise error_from_node(
            original,
            code="PYR-E-ASYNC-UNSUPPORTED",
            message="Phase 03 does not yet lower async @pyrolyze functions",
            module_name=module_name,
            suggested_fix="rewrite_as_sync_phase3",
        )

    private_function = copy.deepcopy(original)
    private_function.name = plan.generated_private_name
    private_function.decorator_list = []
    packed_native_spec = _packed_native_component_spec(
        original,
        packed_native_helper_names=packed_native_helper_names,
        qual_prefix=qual_prefix,
    )
    private_function.args = _private_args_for_component(
        original,
        qual_prefix=qual_prefix,
        packed_native=packed_native_spec is not None,
    )
    if packed_native_spec is not None:
        private_body = _lower_packed_native_component_body(
            original,
            factory=packed_native_spec.factory,
            kind_keyword=packed_native_spec.kind_keyword,
            state_call_site_shared=shared,
        )
    else:
        private_body = _lower_component_body(
            original,
            reactive_decorator_names=reactive_decorator_names,
            slotted_helper_names=slotted_helper_names,
            top_level_component_names=top_level_component_names,
            component_param_names=component_param_names,
            component_event_params=component_event_params,
            callable_return_kinds=callable_return_kinds,
            legacy_container_names=legacy_container_names,
            mount_helper_names=mount_helper_names,
            event_handler_type_names=event_handler_type_names,
            module_name=module_name,
            qual_prefix=qual_prefix,
            in_class_scope=in_class_scope,
            shared=shared,
        )
    private_function.body = [
        copy_reason_location(
            _build_pass_scope(private_body),
            original,
        )
    ]
    private_function.returns = None

    wrapper = copy.deepcopy(original)
    wrapper.decorator_list = _wrapper_decorators_for_component(
        original,
        plan,
        reactive_decorator_names=reactive_decorator_names,
        in_class_scope=in_class_scope,
        packed_kwarg_param_names=_component_parameter_names(plan) if packed_native_spec is not None else (),
    )
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
    reactive_decorator_names: set[str],
    slotted_helper_names: set[str],
    top_level_component_names: set[str],
    component_param_names: dict[str, tuple[str, ...]],
    component_event_params: dict[str, frozenset[str]],
    callable_return_kinds: dict[str, str],
    legacy_container_names: set[str],
    mount_helper_names: set[str],
    event_handler_type_names: set[str],
    module_name: str,
    qual_prefix: str,
    in_class_scope: bool,
    shared: _LoweringShared,
) -> list[ast.stmt]:
    state = _LoweringState(
        module_name=module_name,
        reactive_decorator_names=reactive_decorator_names,
        slotted_helper_names=slotted_helper_names,
        top_level_component_names=top_level_component_names,
        component_param_names=component_param_names,
        component_event_params=component_event_params,
        callable_kinds=_parameter_callable_kinds(component),
        callable_return_kinds=callable_return_kinds,
        legacy_container_names=legacy_container_names,
        mount_helper_names=mount_helper_names,
        event_handler_type_names=event_handler_type_names,
        dirty_by_name=_initial_dirty_map(component, qual_prefix=qual_prefix),
        in_class_scope=in_class_scope,
        context_name="__pyr_ctx",
        shared=shared,
    )
    lowered = _lower_block(component.body, state=state)
    if not lowered:
        lowered.append(ast.Pass())
    return lowered


def _lower_block(
    body: list[ast.stmt],
    *,
    state: _LoweringState,
) -> list[ast.stmt]:
    lowered: list[ast.stmt] = []
    for statement in body:
        lowered.extend(_lower_statement(statement, state=state))
    return lowered


def _lower_statement(statement: ast.stmt, *, state: _LoweringState) -> list[ast.stmt]:
    if isinstance(statement, ast.Pass):
        return []
    if isinstance(statement, ast.Return) and statement.value is None:
        return []
    if isinstance(statement, ast.If):
        return _lower_if(statement, state=state)
    if isinstance(statement, ast.For):
        return _lower_keyed_for(statement, state=state)
    if isinstance(statement, ast.With):
        return _lower_container_with(statement, state=state)
    if isinstance(statement, (ast.AsyncFor, ast.While, ast.AsyncWith, ast.Try, ast.Match)):
        raise error_from_node(
            statement,
            code="PYR-E-PHASE4-STRUCTURE",
            message="Phase 04 does not yet lower this control-flow form",
            module_name=state.module_name,
            suggested_fix="defer_to_later_phase",
        )
    if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_reactive_component(
        statement,
        reactive_decorator_names=state.reactive_decorator_names,
    ):
        raise error_from_node(
            statement,
            code="PYR-E-PHASE4-NESTED-COMPONENT",
            message="Phase 04 does not yet lower nested @pyrolyze definitions",
            module_name=state.module_name,
            suggested_fix="defer_to_later_phase",
        )
    if isinstance(statement, ast.Assign):
        return _lower_assign(statement, state=state)
    if isinstance(statement, ast.AnnAssign):
        return _lower_ann_assign(statement, state=state)
    if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
        return _lower_expr_call(statement, state=state)

    return [copy.deepcopy(statement)]


def _lower_if(statement: ast.If, *, state: _LoweringState) -> list[ast.stmt]:
    body = _lower_block(statement.body, state=state.child(dirty_by_name=dict(state.dirty_by_name)))
    orelse = _lower_block(statement.orelse, state=state.child(dirty_by_name=dict(state.dirty_by_name)))
    lowered = ast.If(
        test=copy.deepcopy(statement.test),
        body=body or [ast.Pass()],
        orelse=orelse,
    )
    return [copy_reason_location(lowered, statement)]


def _lower_container_with(statement: ast.With, *, state: _LoweringState) -> list[ast.stmt]:
    if len(statement.items) != 1:
        raise error_from_node(
            statement,
            code="PYR-E-PHASE4-WITH-SHAPE",
            message="Phase 04 only supports single-item with statements in render scope",
            module_name=state.module_name,
            suggested_fix="split_with_items",
        )

    item = statement.items[0]
    if item.optional_vars is not None:
        if isinstance(item.context_expr, ast.Call) and _is_pyrolyze_sensitive_call(item.context_expr, state=state):
            raise error_from_node(
                statement,
                code="PYR-E-PHASE4-WITH-AS",
                message="'with ... as ...' is ordinary Python context-manager syntax and cannot target PyRolyze helpers",
                module_name=state.module_name,
                suggested_fix="remove_as_or_use_plain_context_manager",
            )
        lowered = copy.deepcopy(statement)
        lowered.body = _lower_block(statement.body, state=state)
        return [copy_reason_location(lowered, statement)]
    if not isinstance(item.context_expr, ast.Call):
        raise error_from_node(
            statement,
            code="PYR-E-PHASE4-WITH-SHAPE",
            message="'with expr:' without 'as' is reserved for PyRolyze container syntax",
            module_name=state.module_name,
            suggested_fix="use_container_helper_without_as",
        )

    slot_index, slot_name, slot_setup = state.next_slot_id(reason=statement)
    context_expr = cast(ast.Call, item.context_expr)
    if _is_mount_call(context_expr, state=state):
        return _lower_mount_with(
            statement,
            slot_index=slot_index,
            slot_name=slot_name,
            slot_setup=slot_setup,
            call=context_expr,
            state=state,
        )
    if _is_app_context_override_call(context_expr):
        return _lower_app_context_override_with(
            statement,
            slot_index=slot_index,
            slot_name=slot_name,
            slot_setup=slot_setup,
            call=context_expr,
            state=state,
        )
    if not _is_container_candidate_call(context_expr, state=state):
        raise error_from_node(
            statement,
            code="PYR-E-PHASE4-WITH-CONTAINER",
            message="'with expr:' without 'as' is reserved for PyRolyze container syntax",
            module_name=state.module_name,
            suggested_fix="use_plain_context_manager_with_as",
        )
    container_ctx_name = _context_name_for_slot(slot_index)
    child_state = state.child(context_name=container_ctx_name)
    lowered_body = _lower_block(statement.body, state=child_state)
    call_name = _call_name(context_expr)
    param_names = state.component_param_names.get(call_name) if call_name is not None else None
    event_param_names = state.component_event_params.get(call_name, frozenset()) if call_name is not None else frozenset()
    dirty_keywords: list[ast.keyword] = []
    if param_names is not None:
        for param_name, arg in zip(param_names, context_expr.args):
            dirty_keywords.append(
                ast.keyword(
                    arg=param_name,
                    value=_dirty_expr_for_value(arg, state.dirty_by_name),
                )
            )
        for keyword in context_expr.keywords:
            if keyword.arg is None:
                continue
            dirty_keywords.append(
                ast.keyword(
                    arg=keyword.arg,
                    value=_dirty_expr_for_value(keyword.value, state.dirty_by_name),
                )
            )

    event_slot_setup, lowered_args, lowered_keywords = _lower_eventful_call_arguments(
        args=list(context_expr.args),
        keywords=list(context_expr.keywords),
        param_names=param_names,
        event_param_names=event_param_names,
        state=state,
        reason=statement,
    )
    container_with = ast.With(
        items=[
            ast.withitem(
                context_expr=ast.Call(
                    func=ast.Attribute(
                        value=state.context_ref(),
                        attr="container_call",
                        ctx=ast.Load(),
                    ),
                    args=[
                        slot_name,
                        copy.deepcopy(context_expr.func),
                        *lowered_args,
                    ],
                    keywords=[
                        *lowered_keywords,
                        ast.keyword(
                            arg="dirty_state",
                            value=ast.Call(
                                func=_support_reference("__pyr_dirtyof", in_class_scope=state.in_class_scope),
                                args=[],
                                keywords=dirty_keywords,
                            ),
                        ),
                    ],
                ),
                optional_vars=ast.Name(id=container_ctx_name, ctx=ast.Store()),
            )
        ],
        body=lowered_body or [ast.Pass()],
    )
    guard = _or_expression(
        [
            _dirty_expr_for_value(context_expr, state.dirty_by_name),
            _dirty_expr_for_statements(statement.body, state.dirty_by_name),
            ast.Call(
                func=ast.Attribute(
                    value=state.context_ref(),
                    attr="visit_slot_and_dirty",
                    ctx=ast.Load(),
                ),
                args=[slot_name],
                keywords=[],
            ),
        ]
    )
    lowered = ast.If(test=guard, body=[container_with], orelse=[])
    return [*slot_setup, *event_slot_setup, copy_reason_location(lowered, statement)]


def _lower_mount_with(
    statement: ast.With,
    *,
    slot_index: int,
    slot_name: ast.expr,
    slot_setup: list[ast.stmt],
    call: ast.Call,
    state: _LoweringState,
) -> list[ast.stmt]:
    if call.keywords:
        raise error_from_node(
            statement,
            code="PYR-E-MOUNT-KEYWORDS",
            message="mount(...) accepts selector terms as positional arguments only",
            module_name=state.module_name,
            suggested_fix="pass_selector_values_positionally",
        )

    mount_ctx_name = _context_name_for_slot(slot_index)
    child_state = state.child(context_name=mount_ctx_name)
    lowered_body = _lower_block(statement.body, state=child_state)
    directive_with = ast.With(
        items=[
            ast.withitem(
                context_expr=ast.Call(
                    func=ast.Attribute(
                        value=state.context_ref(),
                        attr="open_directive",
                        ctx=ast.Load(),
                    ),
                    args=[
                        slot_name,
                        _support_reference(
                            "__pyr_validate_mount_selectors",
                            in_class_scope=state.in_class_scope,
                        ),
                        *copy.deepcopy(call.args),
                    ],
                    keywords=[],
                ),
                optional_vars=ast.Name(id=mount_ctx_name, ctx=ast.Store()),
            )
        ],
        body=lowered_body or [ast.Pass()],
    )
    guard = _or_expression(
        [
            _dirty_expr_for_value(call, state.dirty_by_name),
            _dirty_expr_for_statements(statement.body, state.dirty_by_name),
            ast.Call(
                func=ast.Attribute(
                    value=state.context_ref(),
                    attr="visit_slot_and_dirty",
                    ctx=ast.Load(),
                ),
                args=[slot_name],
                keywords=[],
            ),
        ]
    )
    lowered = ast.If(test=guard, body=[directive_with], orelse=[])
    return [*slot_setup, copy_reason_location(lowered, statement)]


def _lower_app_context_override_with(
    statement: ast.With,
    *,
    slot_index: int,
    slot_name: ast.expr,
    slot_setup: list[ast.stmt],
    call: ast.Call,
    state: _LoweringState,
) -> list[ast.stmt]:
    if call.keywords:
        raise error_from_node(
            statement,
            code="PYR-E-APP-CONTEXT-OVERRIDE-KEYWORDS",
            message="app_context_override[...] accepts override values as positional arguments only",
            module_name=state.module_name,
            suggested_fix="pass_override_values_positionally",
        )

    keys = _app_context_override_key_exprs(call, state=state, error_node=statement)
    has_starred_args = any(isinstance(arg, ast.Starred) for arg in call.args)
    if not has_starred_args and len(call.args) != len(keys):
        raise error_from_node(
            statement,
            code="PYR-E-APP-CONTEXT-OVERRIDE-ARITY",
            message="app_context_override[...] requires the same number of values as fixed keys",
            module_name=state.module_name,
            suggested_fix="match_override_key_value_arity",
        )

    override_ctx_name = _context_name_for_slot(slot_index)
    child_state = state.child(context_name=override_ctx_name)
    lowered_body = _lower_block(statement.body, state=child_state)
    keys_tuple = ast.Tuple(elts=[copy.deepcopy(key) for key in keys], ctx=ast.Load())
    override_with = ast.With(
        items=[
            ast.withitem(
                context_expr=ast.Call(
                    func=ast.Attribute(
                        value=state.context_ref(),
                        attr="open_app_context_override",
                        ctx=ast.Load(),
                    ),
                    args=[
                        slot_name,
                        keys_tuple,
                        *copy.deepcopy(call.args),
                    ],
                    keywords=[],
                ),
                optional_vars=ast.Name(id=override_ctx_name, ctx=ast.Store()),
            )
        ],
        body=lowered_body or [ast.Pass()],
    )
    guard = _or_expression(
        [
            _dirty_expr_for_value(call, state.dirty_by_name),
            _dirty_expr_for_statements(statement.body, state.dirty_by_name),
            ast.Call(
                func=ast.Attribute(
                    value=state.context_ref(),
                    attr="visit_slot_and_dirty",
                    ctx=ast.Load(),
                ),
                args=[slot_name],
                keywords=[],
            ),
        ]
    )
    lowered = ast.If(test=guard, body=[override_with], orelse=[])
    return [*slot_setup, copy_reason_location(lowered, statement)]


def _lower_keyed_for(statement: ast.For, *, state: _LoweringState) -> list[ast.stmt]:
    if statement.orelse:
        raise error_from_node(
            statement,
            code="PYR-E-PHASE4-FOR-ELSE",
            message="Phase 04 does not yet lower for-else in render scope",
            module_name=state.module_name,
            suggested_fix="remove_for_else",
        )
    if not _is_keyed_call(statement.iter):
        raise error_from_node(
            statement,
            code="PYR-E-MISSING-KEY",
            message="Mutable loop must use keyed(items, key=...)",
            module_name=state.module_name,
            suggested_fix="use_keyed_loop",
        )

    iter_call = cast(ast.Call, statement.iter)
    if not iter_call.args:
        raise error_from_node(
            statement,
            code="PYR-E-PHASE4-KEYED-SHAPE",
            message="keyed(...) must receive the iterable as its first argument",
            module_name=state.module_name,
            suggested_fix="pass_items_to_keyed",
        )
    key_arg = _keyed_key_arg(iter_call)
    if key_arg is None:
        raise error_from_node(
            statement,
            code="PYR-E-MISSING-KEY",
            message="Mutable loop must use keyed(items, key=...)",
            module_name=state.module_name,
            suggested_fix="use_keyed_loop",
        )

    slot_index, slot_name, slot_setup = state.next_slot_id(reason=statement)
    item_ctx_name = _keyed_context_name_for_slot(slot_index)
    loop_dirty_by_name = {
        **state.dirty_by_name,
        **_dirty_state_bindings(statement.target, module_name=state.module_name, reason=statement),
    }
    loop_state = state.child(
        context_name=item_ctx_name,
        dirty_by_name=dict(loop_dirty_by_name),
    )
    lowered_body = _lower_block(statement.body, state=loop_state)
    current_assignments = _build_loop_current_assignments(
        statement.target,
        item_ctx_name=item_ctx_name,
        module_name=state.module_name,
        reason=statement,
    )
    item_guard = _or_expression(
        [
            _dirty_expr_for_value(iter_call.args[0], state.dirty_by_name),
            _dirty_expr_for_value(key_arg, state.dirty_by_name),
            _dirty_expr_for_statements(statement.body, loop_dirty_by_name),
            ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=item_ctx_name, ctx=ast.Load()),
                    attr="visit_self_and_dirty",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        ]
    )
    loop_for = ast.For(
        target=ast.Name(id=item_ctx_name, ctx=ast.Store()),
        iter=ast.Call(
            func=ast.Attribute(
                value=state.context_ref(),
                attr="keyed_loop",
                ctx=ast.Load(),
            ),
            args=[slot_name, copy.deepcopy(iter_call.args[0])],
            keywords=[ast.keyword(arg="key_fn", value=copy.deepcopy(key_arg))],
        ),
        body=[
            ast.With(
                items=[
                    ast.withitem(
                        context_expr=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id=item_ctx_name, ctx=ast.Load()),
                                attr="pass_scope",
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        ),
                        optional_vars=None,
                    )
                ],
                body=[
                    *current_assignments,
                    ast.If(
                        test=ast.UnaryOp(op=ast.Not(), operand=item_guard),
                        body=[ast.Continue()],
                        orelse=[],
                    ),
                    *lowered_body,
                ],
            )
        ],
        orelse=[],
    )
    guard = _or_expression(
        [
            _dirty_expr_for_value(iter_call.args[0], state.dirty_by_name),
            _dirty_expr_for_value(key_arg, state.dirty_by_name),
            _dirty_expr_for_statements(statement.body, state.dirty_by_name),
            ast.Call(
                func=ast.Attribute(
                    value=state.context_ref(),
                    attr="visit_slot_and_dirty",
                    ctx=ast.Load(),
                ),
                args=[slot_name],
                keywords=[],
            ),
        ]
    )
    lowered = ast.If(test=guard, body=[loop_for], orelse=[])
    return [*slot_setup, copy_reason_location(lowered, statement)]


def _lower_assign(statement: ast.Assign, *, state: _LoweringState) -> list[ast.stmt]:
    if len(statement.targets) != 1:
        return [copy.deepcopy(statement)]

    target = statement.targets[0]
    if isinstance(statement.value, ast.Call) and _is_slotted_helper_call(statement.value, state=state):
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
        _update_callable_kind_from_assignment(target, statement.value, state=state)

    ast.copy_location(lowered[0], statement)
    return lowered


def _lower_ann_assign(statement: ast.AnnAssign, *, state: _LoweringState) -> list[ast.stmt]:
    if isinstance(statement.target, ast.Name):
        callable_kind = _callable_kind_from_annotation(statement.annotation)
        if callable_kind is not None:
            state.callable_kinds[statement.target.id] = callable_kind

    if statement.value is None:
        return [copy.deepcopy(statement)]

    synthetic_assign = ast.Assign(
        targets=[copy.deepcopy(statement.target)],
        value=copy.deepcopy(statement.value),
    )
    ast.copy_location(synthetic_assign, statement)
    return _lower_assign(synthetic_assign, state=state)


def _lower_slotted_assign(
    statement: ast.Assign,
    *,
    target: ast.expr,
    call: ast.Call,
    state: _LoweringState,
) -> list[ast.stmt]:
    _slot_index, slot_name, slot_setup = state.next_slot_id(reason=statement)
    call_expr = ast.Call(
        func=ast.Attribute(value=state.context_ref(), attr="call_plain", ctx=ast.Load()),
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

    return [*slot_setup, copy_reason_location(lowered_assign, statement)]


def _lower_expr_call(statement: ast.Expr, *, state: _LoweringState) -> list[ast.stmt]:
    call = statement.value
    if _is_call_native_expr(call):
        return _lower_call_native_expr(statement, call=call, state=state)
    if _is_slotted_helper_call(call, state=state):
        return _lower_slotted_expr_call(statement, call=call, state=state)

    call_name = _call_name(call)
    if call_name is not None and _callable_kind_for_name(call_name, state=state) == _CALLABLE_KIND_COMPONENT_REF:
        return _lower_component_expr_call(statement, call=call, state=state)

    return [copy_reason_location(ast.Expr(value=copy.deepcopy(call)), statement)]


def _lower_slotted_expr_call(
    statement: ast.Expr,
    *,
    call: ast.Call,
    state: _LoweringState,
) -> list[ast.stmt]:
    _slot_index, slot_name, slot_setup = state.next_slot_id(reason=statement)
    lowered = ast.Expr(
        value=ast.Call(
            func=ast.Attribute(value=state.context_ref(), attr="call_plain", ctx=ast.Load()),
            args=[slot_name, copy.deepcopy(call.func), *[copy.deepcopy(arg) for arg in call.args]],
            keywords=[copy.deepcopy(keyword) for keyword in call.keywords],
        )
    )
    return [*slot_setup, copy_reason_location(lowered, statement)]


def _lower_component_expr_call(
    statement: ast.Expr,
    *,
    call: ast.Call,
    state: _LoweringState,
) -> list[ast.stmt]:
    call_name = _call_name(call)
    if call_name is None:
        raise error_from_node(
            statement,
            code="PYR-E-PHASE5-COMPONENT-CALL",
            message="Phase 05 direct component lowering requires a named component ref",
            module_name=state.module_name,
            suggested_fix="call_named_component_ref",
        )

    param_names = state.component_param_names.get(call_name)
    if param_names is None:
        raise error_from_node(
            statement,
            code="PYR-E-PHASE5-COMPONENT-CALL",
            message="Phase 05 could not resolve parameter names for this component call",
            module_name=state.module_name,
            suggested_fix="use_direct_component_ref_call",
        )

    if any(keyword.arg is None for keyword in call.keywords):
        raise error_from_node(
            statement,
            code="PYR-E-PHASE5-COMPONENT-CALL",
            message="Phase 05 does not yet lower starred keyword component calls",
            module_name=state.module_name,
            suggested_fix="use_explicit_component_arguments",
        )

    _slot_index, slot_name, slot_setup = state.next_slot_id(reason=statement)
    dirty_keywords: list[ast.keyword] = []
    for param_name, arg in zip(param_names, call.args):
        dirty_keywords.append(
            ast.keyword(
                arg=param_name,
                value=_dirty_expr_for_value(arg, state.dirty_by_name),
            )
        )
    for keyword in call.keywords:
        if keyword.arg is None:
            continue
        dirty_keywords.append(
            ast.keyword(
                arg=keyword.arg,
                value=_dirty_expr_for_value(keyword.value, state.dirty_by_name),
            )
        )

    event_param_names = state.component_event_params.get(call_name, frozenset())
    event_slot_setup, lowered_args, lowered_keywords = _lower_eventful_call_arguments(
        args=list(call.args),
        keywords=list(call.keywords),
        param_names=param_names,
        event_param_names=event_param_names,
        state=state,
        reason=statement,
    )
    component_call = ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=state.context_ref(),
                attr="component_call",
                ctx=ast.Load(),
            ),
            args=[slot_name, copy.deepcopy(call.func), *lowered_args],
            keywords=[
                *lowered_keywords,
                ast.keyword(
                    arg="dirty_state",
                    value=ast.Call(
                        func=_support_reference("__pyr_dirtyof", in_class_scope=state.in_class_scope),
                        args=[],
                        keywords=dirty_keywords,
                    ),
                ),
            ],
        )
    )
    guard = _or_expression(
        [
            _dirty_expr_for_value(call.func, state.dirty_by_name),
            *[_dirty_expr_for_value(arg, state.dirty_by_name) for arg in call.args],
            *[_dirty_expr_for_value(keyword.value, state.dirty_by_name) for keyword in call.keywords],
            ast.Call(
                func=ast.Attribute(
                    value=state.context_ref(),
                    attr="visit_slot_and_dirty",
                    ctx=ast.Load(),
                ),
                args=[slot_name],
                keywords=[],
            ),
        ]
    )
    lowered = ast.If(test=guard, body=[component_call], orelse=[])
    return [*slot_setup, *event_slot_setup, copy_reason_location(lowered, statement)]


def _lower_call_native_expr(
    statement: ast.Expr,
    *,
    call: ast.Call,
    state: _LoweringState,
) -> list[ast.stmt]:
    if not isinstance(call.func, ast.Call) or _call_name(call.func) != "call_native" or not call.func.args:
        raise error_from_node(
            statement,
            code="PYR-E-PHASE7-CALL-NATIVE",
            message="call_native(...) lowering requires call_native(factory)(...) shape",
            module_name=state.module_name,
            suggested_fix="use_call_native_factory_call",
        )

    call_site_id = state.next_call_site_id(reason=statement)
    factory = call.func.args[0]
    lowered = ast.Expr(
        value=ast.Call(
            func=ast.Attribute(
                value=state.context_ref(),
                attr="call_native",
                ctx=ast.Load(),
            ),
            args=[copy.deepcopy(factory), *[copy.deepcopy(arg) for arg in call.args]],
            keywords=[
                *[copy.deepcopy(keyword) for keyword in call.keywords],
                ast.keyword(arg="__pyr_call_site_id", value=ast.Constant(call_site_id)),
            ],
        )
    )
    return [copy_reason_location(lowered, statement)]


def _inject_module_scaffold(
    body: list[ast.stmt],
    *,
    slot_declarations: list[ast.Assign],
) -> list[ast.stmt]:
    if not body:
        return body

    insert_at = 1 if _is_module_docstring(body[0]) else 0
    while insert_at < len(body) and _is_future_import(body[insert_at]):
        insert_at += 1
    api_names = [
        ast.alias(name="CallFromNonPyrolyzeContext", asname="__pyr_CallFromNonPyrolyzeContext"),
        ast.alias(name="ComponentMetadata", asname="__pyr_ComponentMetadata"),
        ast.alias(name="pyrolyze_component_ref", asname="__pyr_component_ref"),
    ]
    if _body_uses_support_name(body, "__pyr_validate_mount_selectors"):
        api_names.append(
            ast.alias(name="validate_mount_selectors", asname="__pyr_validate_mount_selectors")
        )
    scaffold = [
        ast.ImportFrom(
            module="pyrolyze.api",
            names=api_names,
            level=0,
        ),
        ast.ImportFrom(
            module="pyrolyze.runtime",
            names=[
                ast.alias(name="SlotId", asname="__pyr_SlotId"),
                ast.alias(name="dirtyof", asname="__pyr_dirtyof"),
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
    return [*body[:insert_at], *scaffold, *slot_declarations, *body[insert_at:]]


def _body_uses_support_name(body: list[ast.stmt], name: str) -> bool:
    for statement in body:
        for node in ast.walk(statement):
            if isinstance(node, ast.Name) and node.id == name:
                return True
            if isinstance(node, ast.Constant) and node.value == name:
                return True
    return False


def _is_future_import(statement: ast.stmt) -> bool:
    return isinstance(statement, ast.ImportFrom) and statement.module == "__future__"


def _private_args_for_component(
    original: ast.FunctionDef,
    *,
    qual_prefix: str,
    packed_native: bool,
) -> ast.arguments:
    ctx_arg = ast.arg(arg="__pyr_ctx")
    dirty_arg = ast.arg(arg="__pyr_dirty_state")
    method_kind = _method_kind(original, qual_prefix=qual_prefix)
    if packed_native:
        args = ast.arguments(
            posonlyargs=[],
            args=[],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=ast.arg(arg="kwds"),
            defaults=[],
        )
        if method_kind in {"instance", "class"} and original.args.args:
            args.args = [copy.deepcopy(original.args.args[0]), ctx_arg, dirty_arg]
        else:
            args.args = [ctx_arg, dirty_arg]
        return args

    args = copy.deepcopy(original.args)
    if method_kind in {"instance", "class"} and args.args:
        args.args = [args.args[0], ctx_arg, dirty_arg, *args.args[1:]]
    else:
        args.args = [ctx_arg, dirty_arg, *args.args]
    return args


def _wrapper_decorators_for_component(
    original: ast.FunctionDef,
    plan: ComponentTransformPlan,
    *,
    reactive_decorator_names: set[str],
    in_class_scope: bool,
    packed_kwarg_param_names: tuple[str, ...],
) -> list[ast.expr]:
    remaining = [
        copy.deepcopy(decorator)
        for decorator in original.decorator_list
        if _decorator_name(decorator) not in reactive_decorator_names
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
                    keywords=[
                        *(
                            [
                                ast.keyword(arg="packed_kwargs", value=ast.Constant(True)),
                                ast.keyword(
                                    arg="packed_kwarg_param_names",
                                    value=ast.Tuple(
                                        elts=[ast.Constant(name) for name in packed_kwarg_param_names],
                                        ctx=ast.Load(),
                                    ),
                                ),
                            ]
                            if packed_kwarg_param_names
                            else []
                        )
                    ],
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
                    func=ast.Attribute(value=ast.Name(id="__pyr_ctx", ctx=ast.Load()), attr="pass_scope", ctx=ast.Load()),
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


def _component_parameter_names(component: ComponentTransformPlan) -> tuple[str, ...]:
    qual_prefix = component.public_name.rpartition(".")[0]
    node = component.node
    args = list(node.args.args)
    if _method_kind(node, qual_prefix=qual_prefix) in {"instance", "class"} and args:
        args = args[1:]
    source_args = [*node.args.posonlyargs, *args, *node.args.kwonlyargs]
    return tuple(argument.arg for argument in source_args)


def _parameter_callable_kinds(component: ast.FunctionDef) -> dict[str, str]:
    return {
        argument.arg: callable_kind
        for argument in [*component.args.posonlyargs, *component.args.args, *component.args.kwonlyargs]
        if (callable_kind := _callable_kind_from_annotation(argument.annotation)) is not None
    }


def _parameter_event_names(
    component: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    event_handler_type_names: set[str],
) -> frozenset[str]:
    return frozenset(
        argument.arg
        for argument in [*component.args.posonlyargs, *component.args.args, *component.args.kwonlyargs]
        if _annotation_contains_event_handler(
            argument.annotation,
            event_handler_type_names=event_handler_type_names,
        )
    )


def _collect_local_callable_return_kinds(module_ast: ast.Module) -> dict[str, str]:
    kinds: dict[str, str] = {}
    for node in ast.walk(module_ast):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        callable_kind = _callable_kind_from_annotation(node.returns)
        if callable_kind is not None:
            kinds[node.name] = callable_kind
    return kinds


def _collect_legacy_container_names(module_ast: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(module_ast):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(_decorator_name(decorator) == "contextmanager" for decorator in node.decorator_list):
            names.add(node.name)
    return names


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


def _dirty_expr_for_statements(
    statements: list[ast.stmt],
    dirty_by_name: dict[str, ast.expr],
) -> ast.expr:
    dirty_parts: list[ast.expr] = []
    seen_names: set[str] = set()
    for statement in statements:
        for node in ast.walk(statement):
            if not isinstance(node, ast.Name):
                continue
            dirty_expr = dirty_by_name.get(node.id)
            if dirty_expr is None or node.id in seen_names:
                continue
            seen_names.add(node.id)
            dirty_parts.append(copy.deepcopy(dirty_expr))
    return _or_expression(dirty_parts)


def _event_handler_expression(
    callback: ast.expr,
    *,
    slot_ref: ast.expr,
    state: _LoweringState,
) -> ast.expr:
    return ast.Call(
        func=ast.Attribute(
            value=state.context_ref(),
            attr="event_handler_binding",
            ctx=ast.Load(),
        ),
        args=[slot_ref],
        keywords=[
            ast.keyword(
                arg="dirty",
                value=_dirty_expr_for_value(callback, state.dirty_by_name),
            ),
            ast.keyword(arg="callback", value=copy.deepcopy(callback)),
        ],
    )


def _lower_eventful_call_arguments(
    *,
    args: list[ast.expr],
    keywords: list[ast.keyword],
    param_names: tuple[str, ...] | None,
    event_param_names: frozenset[str],
    state: _LoweringState,
    reason: ast.AST,
) -> tuple[list[ast.stmt], list[ast.expr], list[ast.keyword]]:
    if not event_param_names or param_names is None:
        return [], [copy.deepcopy(arg) for arg in args], [copy.deepcopy(keyword) for keyword in keywords]

    slot_setup: list[ast.stmt] = []
    lowered_args: list[ast.expr] = []
    for index, arg in enumerate(args):
        param_name = param_names[index] if index < len(param_names) else None
        if param_name is not None and param_name in event_param_names and not _is_none_literal(arg):
            _event_slot_index, event_slot_ref, event_slot_setup = state.next_slot_id(reason=reason)
            slot_setup.extend(event_slot_setup)
            lowered_args.append(
                copy_reason_location(
                    _event_handler_expression(
                        arg,
                        slot_ref=event_slot_ref,
                        state=state,
                    ),
                    arg,
                )
            )
        else:
            lowered_args.append(copy.deepcopy(arg))

    lowered_keywords: list[ast.keyword] = []
    for keyword in keywords:
        if keyword.arg is not None and keyword.arg in event_param_names and not _is_none_literal(keyword.value):
            _event_slot_index, event_slot_ref, event_slot_setup = state.next_slot_id(reason=reason)
            slot_setup.extend(event_slot_setup)
            lowered_keywords.append(
                ast.keyword(
                    arg=keyword.arg,
                    value=copy_reason_location(
                        _event_handler_expression(
                            keyword.value,
                            slot_ref=event_slot_ref,
                            state=state,
                        ),
                        keyword.value,
                    ),
                )
            )
            continue
        lowered_keywords.append(copy.deepcopy(keyword))

    return slot_setup, lowered_args, lowered_keywords


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
            names.extend(_bound_names(element))
        return names
    raise TypeError("unsupported assignment target")


def _bound_target_store(target: ast.expr, *, module_name: str, reason: ast.AST) -> ast.expr:
    if isinstance(target, ast.Name):
        return ast.Name(id=target.id, ctx=ast.Store())
    if isinstance(target, ast.Tuple):
        return ast.Tuple(
            elts=[_bound_target_store(element, module_name=module_name, reason=reason) for element in target.elts],
            ctx=ast.Store(),
        )
    raise error_from_node(
        reason,
        code="PYR-E-PHASE4-FOR-TARGET",
        message="Phase 04 only supports name and tuple destructuring targets in keyed loops",
        module_name=module_name,
        suggested_fix="simplify_loop_target",
    )


def _dirty_target_store(target: ast.expr, *, module_name: str, reason: ast.AST) -> ast.expr:
    if isinstance(target, ast.Name):
        return ast.Name(id=_dirty_name_for(target.id), ctx=ast.Store())
    if isinstance(target, ast.Tuple):
        return ast.Tuple(
            elts=[_dirty_target_store(element, module_name=module_name, reason=reason) for element in target.elts],
            ctx=ast.Store(),
        )
    raise error_from_node(
        reason,
        code="PYR-E-PHASE4-FOR-TARGET",
        message="Phase 04 only supports name and tuple destructuring targets in keyed loops",
        module_name=module_name,
        suggested_fix="simplify_loop_target",
    )


def _dirty_state_bindings(target: ast.expr, *, module_name: str, reason: ast.AST) -> dict[str, ast.expr]:
    try:
        names = _bound_names(target)
    except TypeError:
        raise error_from_node(
            reason,
            code="PYR-E-PHASE4-FOR-TARGET",
            message="Phase 04 only supports name and tuple destructuring targets in keyed loops",
            module_name=module_name,
            suggested_fix="simplify_loop_target",
        ) from None
    return {name: ast.Name(id=_dirty_name_for(name), ctx=ast.Load()) for name in names}


def _build_loop_current_assignments(
    target: ast.expr,
    *,
    item_ctx_name: str,
    module_name: str,
    reason: ast.AST,
) -> list[ast.stmt]:
    current_value = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id=item_ctx_name, ctx=ast.Load()),
            attr="current_value",
            ctx=ast.Load(),
        ),
        args=[],
        keywords=[],
    )
    if isinstance(target, ast.Name):
        return [
            copy_reason_location(
                ast.Assign(
                    targets=[
                        ast.Tuple(
                            elts=[
                                ast.Name(id=_dirty_name_for(target.id), ctx=ast.Store()),
                                ast.Name(id=target.id, ctx=ast.Store()),
                            ],
                            ctx=ast.Store(),
                        )
                    ],
                    value=current_value,
                ),
                reason,
            )
        ]

    return [
        copy_reason_location(
            ast.Assign(
                targets=[
                    ast.Tuple(
                        elts=[
                            ast.Name(id="__pyr_item_dirty", ctx=ast.Store()),
                            ast.Name(id="__pyr_item_value", ctx=ast.Store()),
                        ],
                        ctx=ast.Store(),
                    )
                ],
                value=current_value,
            ),
            reason,
        ),
        copy_reason_location(
            ast.Assign(
                targets=[_dirty_target_store(target, module_name=module_name, reason=reason)],
                value=ast.Name(id="__pyr_item_dirty", ctx=ast.Load()),
            ),
            reason,
        ),
        copy_reason_location(
            ast.Assign(
                targets=[_bound_target_store(target, module_name=module_name, reason=reason)],
                value=ast.Name(id="__pyr_item_value", ctx=ast.Load()),
            ),
            reason,
        ),
    ]


def _dirty_name_for(name: str) -> str:
    return f"__pyr_{name}_dirty"


def _context_name_for_slot(slot_index: int) -> str:
    return f"__pyr_ctx_slot_{slot_index}"


def _keyed_context_name_for_slot(slot_index: int) -> str:
    return f"__pyr_ctx_slot_{slot_index}_k"


def _is_false_expr(expression: ast.expr) -> bool:
    return isinstance(expression, ast.Constant) and expression.value is False


def _is_none_literal(expression: ast.AST) -> bool:
    return isinstance(expression, ast.Constant) and expression.value is None


def _collect_slotted_helper_names(
    module_ast: ast.Module,
    *,
    slotted_decorator_names: set[str],
) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(module_ast):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_pyrolyze_slotted(
            node,
            slotted_decorator_names=slotted_decorator_names,
        ):
            names.add(node.name)
    return names


def _is_slotted_helper_call(call: ast.Call, *, state: _LoweringState) -> bool:
    call_name = _call_name(call)
    return call_name is not None and _callable_kind_for_name(call_name, state=state) == _CALLABLE_KIND_SLOT_CALLABLE


def _is_call_native_expr(call: ast.Call) -> bool:
    return isinstance(call.func, ast.Call) and _call_name(call.func) == "call_native"


def _is_keyed_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and _call_name(node) == "keyed"


def _keyed_key_arg(node: ast.Call) -> ast.expr | None:
    for keyword in node.keywords:
        if keyword.arg == "key":
            return keyword.value
    if len(node.args) >= 2:
        return node.args[1]
    return None


def _method_kind(node: ast.FunctionDef, *, qual_prefix: str) -> str:
    if not _in_class_scope(qual_prefix):
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


def _is_reactive_component(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    reactive_decorator_names: set[str],
) -> bool:
    return any(_decorator_name(decorator) in reactive_decorator_names for decorator in node.decorator_list)


def _is_pyrolyze_slotted(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    slotted_decorator_names: set[str],
) -> bool:
    return any(_decorator_name(decorator) in slotted_decorator_names for decorator in node.decorator_list)


def _in_class_scope(qual_prefix: str) -> bool:
    return bool(qual_prefix) and "<locals>" not in qual_prefix.split(".")


def _collect_source_api_aliases(module_ast: ast.Module) -> tuple[set[str], set[str], set[str]]:
    reactive = set(_REACTIVE_DECORATORS)
    slotted = set(_SLOTTED_DECORATORS)
    event_handlers = set(_EVENT_HANDLER_TYPES)
    for statement in module_ast.body:
        if not isinstance(statement, ast.ImportFrom) or statement.module != "pyrolyze.api":
            continue
        for alias in statement.names:
            local_name = alias.asname or alias.name
            if alias.name in _REACTIVE_DECORATORS:
                reactive.add(local_name)
            if alias.name in _SLOTTED_DECORATORS:
                slotted.add(local_name)
            if alias.name in _EVENT_HANDLER_TYPES:
                event_handlers.add(local_name)
    return reactive, slotted, event_handlers


def _collect_mount_helper_names(module_ast: ast.Module) -> set[str]:
    mount_names = set(_MOUNT_HELPERS)
    for statement in module_ast.body:
        if not isinstance(statement, ast.ImportFrom) or statement.module != "pyrolyze.api":
            continue
        for alias in statement.names:
            if alias.name in _MOUNT_HELPERS:
                mount_names.add(alias.asname or alias.name)
    return mount_names


def _collect_imported_annotated_symbols(
    module_ast: ast.Module,
) -> tuple[set[str], set[str], dict[str, tuple[str, ...]], dict[str, frozenset[str]], dict[str, str]]:
    slotted_names: set[str] = set()
    component_names: set[str] = set()
    component_param_names: dict[str, tuple[str, ...]] = {}
    component_event_params: dict[str, frozenset[str]] = {}
    return_kinds: dict[str, str] = {}

    for statement in module_ast.body:
        if not isinstance(statement, ast.ImportFrom):
            continue
        if statement.level != 0 or statement.module is None:
            continue
        try:
            imported_module = importlib.import_module(statement.module)
        except Exception:
            continue

        for alias in statement.names:
            if alias.name == "*":
                continue
            imported_value = getattr(imported_module, alias.name, None)
            if imported_value is None:
                continue

            local_name = alias.asname or alias.name
            resolved_hints = _resolve_runtime_type_hints(imported_value)
            if getattr(imported_value, "_pyrolyze_slotted", False) or _is_slot_backed_imported_helper(
                imported_value,
                resolved_hints=resolved_hints,
            ):
                slotted_names.add(local_name)

            if getattr(imported_value, "_pyrolyze_meta", None) is None:
                callable_kind = _callable_kind_from_runtime_annotation(
                    resolved_hints.get(
                        "return",
                        getattr(imported_value, "__annotations__", {}).get("return", inspect.Signature.empty),
                    )
                )
                if callable_kind is not None:
                    return_kinds[local_name] = callable_kind
            else:
                component_names.add(local_name)
                try:
                    signature = inspect.signature(imported_value)
                except (TypeError, ValueError):
                    signature = None

                if signature is not None:
                    component_param_names[local_name] = tuple(
                        parameter.name
                        for parameter in signature.parameters.values()
                        if parameter.kind
                        in {
                            inspect.Parameter.POSITIONAL_ONLY,
                            inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            inspect.Parameter.KEYWORD_ONLY,
                        }
                    )
                    component_event_params[local_name] = frozenset(
                        parameter.name
                        for parameter in signature.parameters.values()
                        if parameter.kind
                        in {
                            inspect.Parameter.POSITIONAL_ONLY,
                            inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            inspect.Parameter.KEYWORD_ONLY,
                        }
                        and _runtime_annotation_is_event_handler(
                            resolved_hints.get(parameter.name, parameter.annotation)
                        )
                    )

            if inspect.isclass(imported_value):
                ui_interface = getattr(imported_value, "UI_INTERFACE", None)
                if ui_interface is not None:
                    for public_name in ui_interface.entries:
                        attribute_value = getattr(imported_value, public_name, None)
                        if attribute_value is None:
                            continue
                        qualified_name = f"{local_name}.{public_name}"
                        component_names.add(qualified_name)
                        try:
                            attribute_signature = inspect.signature(attribute_value)
                        except (TypeError, ValueError):
                            continue
                        attribute_hints = _resolve_runtime_type_hints(attribute_value)
                        param_names = tuple(
                            parameter.name
                            for parameter in attribute_signature.parameters.values()
                            if parameter.kind
                            in {
                                inspect.Parameter.POSITIONAL_ONLY,
                                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                inspect.Parameter.KEYWORD_ONLY,
                            }
                        )
                        event_names = frozenset(
                            parameter.name
                            for parameter in attribute_signature.parameters.values()
                            if parameter.kind
                            in {
                                inspect.Parameter.POSITIONAL_ONLY,
                                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                inspect.Parameter.KEYWORD_ONLY,
                            }
                            and _runtime_annotation_is_event_handler(
                                attribute_hints.get(parameter.name, parameter.annotation)
                            )
                        )
                        component_param_names[qualified_name] = param_names
                        component_event_params[qualified_name] = event_names

    return slotted_names, component_names, component_param_names, component_event_params, return_kinds


def _resolve_runtime_type_hints(value: Any) -> dict[str, Any]:
    module = inspect.getmodule(value)
    globalns: dict[str, Any] = {}
    if module is not None:
        globalns.update(vars(module))
    for module_name in ("pyrolyze.runtime", "pyrolyze.api"):
        try:
            globalns.update(vars(importlib.import_module(module_name)))
        except Exception:
            continue
    try:
        return get_type_hints(value, globalns=globalns, include_extras=True)
    except Exception:
        return {}


def _is_slot_backed_imported_helper(
    imported_value: Any,
    *,
    resolved_hints: dict[str, Any],
) -> bool:
    try:
        signature = inspect.signature(imported_value)
    except (TypeError, ValueError):
        signature = None

    if signature is not None:
        for parameter in signature.parameters.values():
            annotation = resolved_hints.get(parameter.name, parameter.annotation)
            if _is_plain_call_runtime_context_annotation(annotation):
                return True

    return _is_plain_call_carrier_annotation(
        resolved_hints.get(
            "return",
            getattr(imported_value, "__annotations__", {}).get("return", inspect.Signature.empty),
        )
    )


def _is_plain_call_runtime_context_annotation(annotation: Any) -> bool:
    return _runtime_annotation_matches(annotation, {"PlainCallRuntimeContext"})


def _is_plain_call_carrier_annotation(annotation: Any) -> bool:
    return _runtime_annotation_matches(
        annotation,
        {
            "ExternalStoreRef",
            "PyrolyzeMountAdvertisementRequest",
            "UseEffectRequest",
            "UseEffectAsyncRequest",
        },
    )


def _runtime_annotation_matches(annotation: Any, type_names: set[str]) -> bool:
    if annotation is None or annotation is inspect.Signature.empty:
        return False
    if isinstance(annotation, str):
        return any(name in annotation for name in type_names)
    if getattr(annotation, "__name__", None) in type_names:
        return True
    origin = get_origin(annotation)
    if origin is not None:
        if getattr(origin, "__name__", None) in type_names:
            return True
        if origin is Annotated:
            args = get_args(annotation)
            return bool(args) and _runtime_annotation_matches(args[0], type_names)
    return any(name in repr(annotation) for name in type_names)


def _runtime_annotation_is_event_handler(annotation: Any) -> bool:
    return _runtime_annotation_matches(
        annotation,
        {
            "PyrolyzeHandler",
            "PyrolyteHandler",
            "PyrolyzeEventParam",
        },
    )


def _annotation_contains_event_handler(
    annotation: ast.AST | None,
    *,
    event_handler_type_names: set[str],
) -> bool:
    if annotation is None:
        return False
    for node in ast.walk(annotation):
        if isinstance(node, ast.Name) and node.id in event_handler_type_names:
            return True
        if isinstance(node, ast.Attribute) and node.attr in _EVENT_HANDLER_TYPES:
            return True
    return False


def _callable_kind_for_name(name: str, *, state: _LoweringState) -> str | None:
    if name in state.top_level_component_names:
        return _CALLABLE_KIND_COMPONENT_REF
    if name in state.slotted_helper_names:
        return _CALLABLE_KIND_SLOT_CALLABLE
    return state.callable_kinds.get(name)


def _is_pyrolyze_sensitive_call(call: ast.Call, *, state: _LoweringState) -> bool:
    if _is_app_context_override_call(call):
        return True
    call_name = _call_name(call)
    if call_name is None:
        return False
    if call_name in state.mount_helper_names:
        return True
    callable_kind = _callable_kind_for_name(call_name, state=state)
    return callable_kind in {_CALLABLE_KIND_COMPONENT_REF, _CALLABLE_KIND_SLOT_CALLABLE}


def _is_container_candidate_call(call: ast.Call, *, state: _LoweringState) -> bool:
    call_name = _call_name(call)
    return call_name is not None and _callable_kind_for_name(call_name, state=state) == _CALLABLE_KIND_COMPONENT_REF


def _is_mount_call(call: ast.Call, *, state: _LoweringState) -> bool:
    call_name = _call_name(call)
    return call_name is not None and call_name in state.mount_helper_names


def _is_app_context_override_call(call: ast.Call) -> bool:
    if not isinstance(call.func, ast.Subscript):
        return False
    return _call_qualified_name(call.func.value) == _APP_CONTEXT_OVERRIDE_HELPER


def _app_context_override_key_exprs(
    call: ast.Call,
    *,
    state: _LoweringState,
    error_node: ast.AST,
) -> tuple[ast.expr, ...]:
    if not isinstance(call.func, ast.Subscript):
        raise error_from_node(
            error_node,
            code="PYR-E-APP-CONTEXT-OVERRIDE-SHAPE",
            message="app_context_override must be subscripted with one or more fixed keys",
            module_name=state.module_name,
            suggested_fix="use_app_context_override_with_fixed_keys",
        )
    slice_node = call.func.slice
    raw_keys = tuple(slice_node.elts) if isinstance(slice_node, ast.Tuple) else (slice_node,)
    if not raw_keys:
        raise error_from_node(
            error_node,
            code="PYR-E-APP-CONTEXT-OVERRIDE-EMPTY",
            message="app_context_override[...] requires at least one fixed key",
            module_name=state.module_name,
            suggested_fix="provide_one_or_more_fixed_keys",
        )
    invalid = next((expr for expr in raw_keys if not _is_static_app_context_key_expr(expr, state=state)), None)
    if invalid is not None:
        raise error_from_node(
            invalid,
            code="PYR-E-APP-CONTEXT-OVERRIDE-KEYS",
            message="app_context_override[...] requires static key references like NAME, module.NAME, or Class.NAME",
            module_name=state.module_name,
            suggested_fix="replace_computed_key_with_static_reference",
        )
    return cast(tuple[ast.expr, ...], raw_keys)


def _is_static_app_context_key_expr(expr: ast.expr, *, state: _LoweringState) -> bool:
    if isinstance(expr, ast.Name):
        return expr.id not in state.dirty_by_name
    if isinstance(expr, ast.Attribute):
        return _is_static_app_context_key_expr(cast(ast.expr, expr.value), state=state)
    return False


def _update_callable_kind_from_assignment(target: ast.expr, value: ast.AST, *, state: _LoweringState) -> None:
    if not isinstance(target, ast.Name):
        return
    if isinstance(value, ast.Name):
        callable_kind = state.callable_kinds.get(value.id)
        if callable_kind is not None:
            state.callable_kinds[target.id] = callable_kind
        return
    if isinstance(value, ast.Call):
        call_name = _call_name(value)
        if call_name is None:
            return
        callable_kind = state.callable_return_kinds.get(call_name)
        if callable_kind is not None:
            state.callable_kinds[target.id] = callable_kind


def _callable_kind_from_annotation(annotation: ast.AST | None) -> str | None:
    if annotation is None:
        return None
    saw_callable = False
    for node in ast.walk(annotation):
        if isinstance(node, ast.Name):
            if node.id == "SlotCallable":
                return _CALLABLE_KIND_SLOT_CALLABLE
            if node.id == "ComponentRef":
                return _CALLABLE_KIND_COMPONENT_REF
            if node.id == "Callable":
                saw_callable = True
        if isinstance(node, ast.Attribute):
            if node.attr == "SlotCallable":
                return _CALLABLE_KIND_SLOT_CALLABLE
            if node.attr == "ComponentRef":
                return _CALLABLE_KIND_COMPONENT_REF
            if node.attr == "Callable":
                saw_callable = True
    if saw_callable:
        return _CALLABLE_KIND_PLAIN_CALLABLE
    return None


def _callable_kind_from_runtime_annotation(annotation: Any) -> str | None:
    if annotation in {None, inspect.Signature.empty}:
        return None
    if isinstance(annotation, str):
        compact = annotation.replace(" ", "")
        if "SlotCallable[" in compact or "PyrolyzeSlottedParam" in compact:
            return _CALLABLE_KIND_SLOT_CALLABLE
        if "ComponentRef[" in compact or compact.endswith(".ComponentRef"):
            return _CALLABLE_KIND_COMPONENT_REF
        if compact in {"Callable", "typing.Callable", "collections.abc.Callable"} or compact.startswith(
            ("Callable[", "typing.Callable[", "collections.abc.Callable[")
        ):
            return _CALLABLE_KIND_PLAIN_CALLABLE
        return None

    origin = get_origin(annotation)
    if origin is not None:
        origin_name = getattr(origin, "__name__", None)
        if origin_name == "ComponentRef":
            return _CALLABLE_KIND_COMPONENT_REF
        if origin_name == "Callable":
            return _CALLABLE_KIND_PLAIN_CALLABLE
        if str(origin) in {"typing.Callable", "collections.abc.Callable"}:
            return _CALLABLE_KIND_PLAIN_CALLABLE
        if str(origin) == "typing.Annotated":
            args = get_args(annotation)
            if args:
                extras = args[1:]
                if any(type(extra).__name__ == "PyrolyzeSlottedParam" for extra in extras):
                    return _CALLABLE_KIND_SLOT_CALLABLE
                return _callable_kind_from_runtime_annotation(args[0])
    text = repr(annotation)
    if text.startswith("typing.Callable") or text.startswith("collections.abc.Callable"):
        return _CALLABLE_KIND_PLAIN_CALLABLE
    if "SlotCallable" in text or "PyrolyzeSlottedParam" in text:
        return _CALLABLE_KIND_SLOT_CALLABLE
    if text.startswith("ComponentRef") or ".ComponentRef" in text:
        return _CALLABLE_KIND_COMPONENT_REF
    return None


def _decorator_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _call_name(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    return _call_qualified_name(node.func)


def _call_qualified_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_qualified_name(node.value)
        if parent is None:
            return None
        return f"{parent}.{node.attr}"
    return None


def _support_reference(name: str, *, in_class_scope: bool) -> ast.expr:
    if not in_class_scope:
        return ast.Name(id=name, ctx=ast.Load())
    return ast.Subscript(
        value=ast.Call(func=ast.Name(id="globals", ctx=ast.Load()), args=[], keywords=[]),
        slice=ast.Constant(name),
        ctx=ast.Load(),
    )
