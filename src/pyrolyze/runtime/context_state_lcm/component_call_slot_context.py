from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable

from .lifecycle_adapter import const, local_store, managed, managed_context
from pyrolyze.runtime.slot_kinds import ContextKind

from ._base import USE_FACTORY, USE_OWNER, _copy_parent_state_mgr, _copy_slot_id
from ._support import REFRACTOR_CLASSES
from ._support import (
    _BOUND_METHOD_SELF_MISSING,
    _bind_pending_event_plain_value,
    _clean_dirty_state,
    _component_call_key,
    _resolve_runtime_component_func,
    _unwrap,
    dirtyof_values,
    DirtyStateContext,
)
from pyrolyze.runtime.function_arg_helpers import build_function_arg_dirty_map, pack_function_args

from .context_base import PASS_TX_KEY
from .field_only_render import _field_only_completion
from .rerunnable_slot_context import RerunnableSlotContextStateMgr


def _freeze_call_value(value: Any) -> Any:
    # Preserve the old record's value-conversion contract without re-inspecting
    # dataclass annotations or allocating an intermediate invocation record.
    convert = getattr(value, "to_frozen", None)
    return convert() if callable(convert) else value


@dataclass(frozen=True, slots=True)
class _ComponentSelection:
    identity: Any = None
    schema: tuple[int, tuple[str, ...]] = (0, ())
    child: Any = None


@managed_context
class ComponentCallSlotContextStateMgr(RerunnableSlotContextStateMgr):
    _parent_state_mgr: Any = const(init=False, default_factory=_copy_parent_state_mgr)
    _slot_id: Any = const(init=False, default_factory=_copy_slot_id)
    # The compatibility route retains its last-attempt selection until adoption.
    _legacy_selection: _ComponentSelection = local_store(
        default_factory=_ComponentSelection
    )
    _selection: _ComponentSelection = managed(
        default_factory=_ComponentSelection,
        init=False,
        compare="identity",
        tx_key=PASS_TX_KEY,
    )
    _pass_owned_event_handler_order: tuple[Any, ...] = local_store(default_factory=tuple)
    _call_runtime_func: Callable[..., Any] | None = managed(
        init=False, default=None, tx_key=PASS_TX_KEY
    )
    _call_bound_receiver: Any = managed(
        init=False, default=_BOUND_METHOD_SELF_MISSING, tx_key=PASS_TX_KEY
    )
    _call_args: tuple[Any, ...] = managed(init=False, default=(), tx_key=PASS_TX_KEY)
    _call_kwargs: dict[str, Any] | None = managed(
        init=False, default=None, tx_key=PASS_TX_KEY
    )
    _call_author_args: tuple[Any, ...] = managed(
        init=False, default=(), tx_key=PASS_TX_KEY
    )
    _call_author_kwargs: dict[str, Any] | None = managed(
        init=False, default=None, tx_key=PASS_TX_KEY
    )
    _call_dirty_state: DirtyStateContext | None = managed(
        init=False, default=None, tx_key=PASS_TX_KEY
    )
    _call_pending_dirty_state: DirtyStateContext | None = managed(
        init=False, default=None, tx_key=PASS_TX_KEY
    )
    _call_uses_dirty_state_api: bool = managed(
        init=False, default=False, tx_key=PASS_TX_KEY
    )
    _call_packed_kwargs: bool = managed(init=False, default=False, tx_key=PASS_TX_KEY)
    _call_packed_kwarg_param_names: tuple[str, ...] = managed(
        init=False, default=(), tx_key=PASS_TX_KEY
    )
    _call_param_names: tuple[str, ...] = managed(
        init=False, default=(), tx_key=PASS_TX_KEY
    )

    def _selection_record(self) -> _ComponentSelection:
        completion = _field_only_completion(self)
        if completion is not None and completion.component_selection_enabled:
            return self._selection
        return self._legacy_selection

    def _set_selection(self, selection: _ComponentSelection) -> None:
        completion = _field_only_completion(self)
        if getattr(completion, "component_selection_enabled", False):
            assert completion.active is not None
            completion.active._require_open()
            completion.active._require_identity()
            self._selection = selection
        else:
            self._legacy_selection = selection

    @property
    def _component_identity(self) -> Any:
        return self._selection_record().identity

    @property
    def _schema(self) -> tuple[int, tuple[str, ...]]:
        return self._selection_record().schema

    @property
    def _child_context_state_mgr(self) -> Any:
        return self._selection_record().child

    @_child_context_state_mgr.setter
    def _child_context_state_mgr(self, child: Any) -> None:
        self._set_selection(replace(self._selection_record(), child=child))

    def invoke(
        self,
        component: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        owner_slot_facade: Any = USE_OWNER,
        scheduler_root_facade: Any = USE_OWNER,
        render_context_factory: Callable[..., Any] | object = USE_FACTORY,
        dirty_state: DirtyStateContext | None = None,
        _pyr_param_names: tuple[str, ...] | None = None,
        _pyr_args_dirty: tuple[Any, ...] | None = None,
        _pyr_kwargs_dirty: dict[str, Any] | None = None,
    ) -> Any:
        owner_slot_facade = self._resolve_owner_arg(owner_slot_facade)
        scheduler_root_facade = self._resolve_owner_arg(scheduler_root_facade)
        if render_context_factory is USE_FACTORY:
            render_context_cls = REFRACTOR_CLASSES.render_context_cls
            if render_context_cls is None:
                raise RuntimeError("render context class is not configured")
            render_context_factory = render_context_cls
        raw_component, _ = _unwrap(component)
        metadata, bound_receiver = _component_call_key(raw_component)
        runtime_func = _resolve_runtime_component_func(getattr(metadata, "_func", None))
        if metadata is None or runtime_func is None:
            runtime_func = raw_component
            bound_receiver = _BOUND_METHOD_SELF_MISSING
            identity_key = raw_component
            param_names: tuple[str, ...] = ()
            packed_kwargs = False
            packed_kwarg_param_names: tuple[str, ...] = ()
        else:
            if bound_receiver is _BOUND_METHOD_SELF_MISSING:
                identity_key = raw_component
            else:
                underlying = getattr(raw_component, "__func__", None)
                identity_key = ("bound_component", id(bound_receiver), underlying)
            param_names = tuple(getattr(metadata, "param_names", ()))
            packed_kwargs = bool(getattr(metadata, "packed_kwargs", False))
            packed_kwarg_param_names = tuple(getattr(metadata, "packed_kwarg_param_names", ()))

        schema = (len(args), tuple(sorted(kwargs)))
        if self._child_context_state_mgr is None or self._component_identity != identity_key or self._schema != schema:
            completion = _field_only_completion(self)
            if getattr(completion, "component_selection_enabled", False):
                # Keep the accepted child alive until the outer decision. The
                # empty candidate allows construction of its replacement.
                self._set_selection(_ComponentSelection())
            elif completion is not None and self._child_context_state_mgr is not None:
                completion.reject("component replacement is not admitted by SC2")
            else:
                self._dispose_child_context()
            child_context = render_context_factory(
                owner_slot=owner_slot_facade,
                scheduler_root=scheduler_root_facade,
                authored_app_context_lookup=self._parent_state_mgr.effective_authored_app_context_lookup(),
            )
            self._set_selection(
                _ComponentSelection(identity_key, schema, child_context._state_mgr)
            )

        self._begin_owned_event_handler_pass()
        completion = _field_only_completion(self)
        invocation_owner = None if completion is None else completion.active
        try:
            effective_param_names = _pyr_param_names or param_names
            if dirty_state is None and effective_param_names:
                dirty_state = dirtyof_values(
                    build_function_arg_dirty_map(
                        effective_param_names,
                        _pyr_args_dirty or (),
                        _pyr_kwargs_dirty or {},
                    )
                )
            if dirty_state is None:
                args_for_rerun = tuple(
                    _bind_pending_event_plain_value(self, _unwrap(arg)[0])
                    for arg in args
                )
                kwargs_for_rerun = {
                    key: _bind_pending_event_plain_value(self, _unwrap(value)[0])
                    for key, value in kwargs.items()
                }
                call_args = args_for_rerun
                call_kwargs = kwargs_for_rerun
                call_author_args = ()
                call_author_kwargs = {}
                call_dirty_state = None
                call_pending_dirty_state = None
            else:
                author_args = tuple(
                    _bind_pending_event_plain_value(self, _unwrap(arg)[0])
                    for arg in args
                )
                author_kwargs = {
                    key: _bind_pending_event_plain_value(self, _unwrap(value)[0])
                    for key, value in kwargs.items()
                }
                call_args = ()
                call_kwargs = {}
                call_author_args = author_args
                call_author_kwargs = author_kwargs
                call_dirty_state = dirty_state
                call_pending_dirty_state = dirty_state
            call_runtime_func = _freeze_call_value(runtime_func)
            call_bound_receiver = _freeze_call_value(bound_receiver)
            call_args = tuple(_freeze_call_value(value) for value in call_args)
            call_author_args = tuple(
                _freeze_call_value(value) for value in call_author_args
            )
            call_dirty_state = _freeze_call_value(call_dirty_state)
            call_pending_dirty_state = _freeze_call_value(call_pending_dirty_state)
            call_packed_kwarg_param_names = tuple(
                _freeze_call_value(value) for value in packed_kwarg_param_names
            )
            call_param_names = tuple(_freeze_call_value(value) for value in param_names)
            if invocation_owner is not None:
                invocation_owner._require_open()
                invocation_owner._require_identity()
            self._call_runtime_func = call_runtime_func
            self._call_bound_receiver = call_bound_receiver
            self._call_args = call_args
            self._call_kwargs = call_kwargs
            self._call_author_args = call_author_args
            self._call_author_kwargs = call_author_kwargs
            self._call_dirty_state = call_dirty_state
            self._call_pending_dirty_state = call_pending_dirty_state
            self._call_uses_dirty_state_api = dirty_state is not None
            self._call_packed_kwargs = packed_kwargs
            self._call_packed_kwarg_param_names = call_packed_kwarg_param_names
            self._call_param_names = call_param_names
            child_context = self._child_context_state_mgr.owner
            self._child_context_state_mgr._authored_app_context_lookup = (
                self._parent_state_mgr.effective_authored_app_context_lookup()
            )
            self._child_context_state_mgr._mounted_callback = self._rerun_child
            child_context._run_boundary()
        except BaseException as error:
            if invocation_owner is not None:
                invocation_owner.fail(error)
            self.rollback_owned_event_handlers()
            raise
        self.ui_state = self._child_context_state_mgr.ui_state
        return None

    def _complete_legacy_selection(self, *, committed: bool) -> None:
        if committed:
            self.commit_owned_event_handlers()
        else:
            self.rollback_owned_event_handlers()

    def commit_owned_event_handlers(self) -> None:
        if not self._pass_owned_event_handler_order and not any(
            child.context_kind() == ContextKind.EVENT_HANDLER and child._seen_in_pass
            for child in self.children_state.values()
        ):
            return
        unseen_slots = [
            slot_id
            for slot_id, child in self.children_state.items()
            if child.context_kind() == ContextKind.EVENT_HANDLER and not child._seen_in_pass
        ]
        for slot_id in unseen_slots:
            child = self.children_state.get(slot_id)
            if child is not None:
                child.deactivate()

        self._pass_owned_event_handler_order = ()

    def rollback_owned_event_handlers(self) -> None:
        if _field_only_completion(self) is not None:
            return
        if not self._pass_owned_event_handler_order and not any(
            child.context_kind() == ContextKind.EVENT_HANDLER and child._seen_in_pass
            for child in self.children_state.values()
        ):
            return
        committed_ids = set(self._pass_owned_event_handler_order)
        for slot_id, child in list(self.children_state.items()):
            if child.context_kind() != ContextKind.EVENT_HANDLER:
                continue
            if slot_id not in committed_ids:
                child.deactivate()
                continue
            child._discard_selection()
            child._seen_in_pass = True
        self._pass_owned_event_handler_order = ()

    def deactivate(self) -> None:
        completion = _field_only_completion(self)
        if completion is not None:
            completion.require_retirement_allowed(self)
        if getattr(completion, "component_selection_enabled", False):
            self._dispose_child_context()
            self.children_state = {}
            children = dict(self._parent_state_mgr.children_state)
            if children.get(self._slot_id) is self:
                children.pop(self._slot_id)
                self._parent_state_mgr.children_state = children
            return
        with self.publish_write_scope():
            self._dispose_child_context()
            super().deactivate()

    def _begin_owned_event_handler_pass(self) -> None:
        completion = _field_only_completion(self)
        if completion is not None:
            completion.note_owned_event_handler_pass(self)
        # The component proof uses managed membership; only the unactivated
        # compatibility route needs an order snapshot for manual restoration.
        if not getattr(completion, "component_selection_enabled", False):
            self._pass_owned_event_handler_order = tuple(
                slot_id
                for slot_id, child in self.children_state.items()
                if child.context_kind() == ContextKind.EVENT_HANDLER
            )
        for child in self.children_state.values():
            if child.context_kind() == ContextKind.EVENT_HANDLER:
                child._seen_in_pass = False

    def _rerun_child(self) -> None:
        child_context = None if self._child_context_state_mgr is None else self._child_context_state_mgr.owner
        # Capture one invocation before preparation or user callbacks can reenter.
        runtime_func = self._call_runtime_func
        bound_receiver = self._call_bound_receiver
        args = self._call_args
        kwargs = self._call_kwargs
        author_args = self._call_author_args
        author_kwargs = self._call_author_kwargs
        previous_dirty_state = self._call_dirty_state
        pending_dirty_state = self._call_pending_dirty_state
        uses_dirty_state_api = self._call_uses_dirty_state_api
        uses_packed_kwargs = self._call_packed_kwargs
        packed_kwarg_param_names = self._call_packed_kwarg_param_names
        if child_context is None or runtime_func is None:
            raise RuntimeError("component child is not mounted")
        refresh_parent = not self._parent_state_mgr.is_scope_active()
        with self.publish_write_scope():
            if uses_dirty_state_api:
                dirty_state = pending_dirty_state
                if dirty_state is None:
                    dirty_state = _clean_dirty_state(previous_dirty_state)
                else:
                    self._call_pending_dirty_state = None
                if uses_packed_kwargs:
                    packed_kwargs = pack_function_args(
                        packed_kwarg_param_names,
                        author_args,
                        author_kwargs or {},
                    )
                    if bound_receiver is _BOUND_METHOD_SELF_MISSING:
                        runtime_func(child_context, dirty_state, **packed_kwargs)
                    else:
                        runtime_func(bound_receiver, child_context, dirty_state, **packed_kwargs)
                elif bound_receiver is _BOUND_METHOD_SELF_MISSING:
                    runtime_func(
                        child_context,
                        dirty_state,
                        *author_args,
                        **(author_kwargs or {}),
                    )
                else:
                    runtime_func(
                        bound_receiver,
                        child_context,
                        dirty_state,
                        *author_args,
                        **(author_kwargs or {}),
                    )
            elif uses_packed_kwargs:
                packed_kwargs = pack_function_args(
                    packed_kwarg_param_names,
                    args,
                    kwargs or {},
                )
                if bound_receiver is _BOUND_METHOD_SELF_MISSING:
                    runtime_func(child_context, **packed_kwargs)
                else:
                    runtime_func(bound_receiver, child_context, **packed_kwargs)
            elif bound_receiver is _BOUND_METHOD_SELF_MISSING:
                runtime_func(child_context, *args, **(kwargs or {}))
            else:
                runtime_func(
                    bound_receiver,
                    child_context,
                    *args,
                    **(kwargs or {}),
                )
            self.ui_state = child_context._state_mgr.ui_state
            if refresh_parent:
                self._parent_state_mgr.refresh_committed_ui_from_children()

    def _dispose_child_context(self) -> None:
        completion = _field_only_completion(self)
        if getattr(completion, "component_selection_enabled", False):
            completion.require_retirement_allowed(self)
            self._set_selection(_ComponentSelection())
            self._call_pending_dirty_state = None
            self.ui_state = ()
            return
        child_context = None if self._child_context_state_mgr is None else self._child_context_state_mgr.owner
        if child_context is None:
            return
        completion = _field_only_completion(self)
        if completion is not None:
            completion.require_retirement_allowed(self)
        child_context._remove_from_scheduler()
        with child_context._state_mgr.publish_write_scope():
            for child in list(child_context._state_mgr.children_state.values()):
                child.deactivate()
            child_context._state_mgr.children_state = {}
            child_context._state_mgr.clear_registered_slots()
        child_context._state_mgr._mounted_callback = None
        self._child_context_state_mgr = None
        self._call_pending_dirty_state = None
        self.ui_state = ()
