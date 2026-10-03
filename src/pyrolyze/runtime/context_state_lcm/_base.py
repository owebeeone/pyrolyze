from __future__ import annotations

from typing import Any, Self

from pyrolyze.runtime.slot_kinds import ContextKind
from .lifecycle_adapter import (
    TransactionManager,
    const,
    field,
    initvar,
    local_store,
    managed_context,
)

USE_OWNER = object()
USE_FACTORY = object()


def unavailable() -> None:
    raise NotImplementedError("context_bare_refactor state manager scaffold")


def _default_context_kind(self: StateMgrBase) -> ContextKind:
    return getattr(self.owner, "_context_kind", ContextKind.SLOT)


def _resolve_render_context_state_mgr_initvar(
    cls: type[StateMgrBase],
    render_context_state_mgr: Any,
    render_context: Any,
) -> Any:
    del cls
    if render_context_state_mgr is not None:
        return render_context_state_mgr
    return getattr(render_context, "_state_mgr", None)


def _copy_parent_state_mgr(cls: type[StateMgrBase], parent_state_mgr: Any) -> Any:
    del cls
    return parent_state_mgr


def _copy_slot_id(cls: type[StateMgrBase], slot_id: Any) -> Any:
    del cls
    return slot_id


def _copy_invoke_dirty(cls: type[StateMgrBase], invoke_dirty: bool) -> bool:
    del cls
    return invoke_dirty


def _copy_seen_in_pass(cls: type[StateMgrBase], seen_in_pass: bool) -> bool:
    del cls
    return seen_in_pass


@managed_context
class StateMgrBase:
    # Roots use neutral slot inputs; descendants share this one construction schema.
    owner: Any = const()
    render_context_state_mgr: Any = initvar(default=None)
    render_context: Any = initvar(default=None)
    parent_state_mgr: Any = initvar(default=None)
    slot_id: Any = initvar(default=None)
    invoke_dirty: bool = initvar(default=True)
    seen_in_pass: bool = initvar(default=False)
    _render_context_state_mgr: Any = field(
        init=False,
        default_factory=_resolve_render_context_state_mgr_initvar,
    )
    _context_kind: ContextKind = const(default_factory=_default_context_kind, allow_self_factory=True)
    _parent_state_mgr: Any = field(init=False, default_factory=_copy_parent_state_mgr)
    _slot_id: Any = field(init=False, default_factory=_copy_slot_id)
    _invoke_dirty: bool = field(init=False, default_factory=_copy_invoke_dirty)
    _seen_in_pass: bool = field(init=False, default_factory=_copy_seen_in_pass)
    _site_metadata: tuple[Any, ...] = local_store(default_factory=tuple)

    @classmethod
    def create(cls, owner: Any, **kwargs: Any) -> Self:
        """Construct through the runtime's boundary-resolution entry point."""
        render_state = _resolve_render_context_state_mgr_initvar(
            cls,
            kwargs.get("render_context_state_mgr"),
            kwargs.get("render_context"),
        )
        manager = getattr(render_state, "_transaction_manager", None)
        if manager is not None:
            from .field_only_render import _field_only_completion

            completion = _field_only_completion(render_state)
            if completion is not None:
                completion.require_slot_type(type(owner))
            kwargs["transaction_manager"] = manager
        return cls(owner=owner, **kwargs)

    @property
    def _transaction_manager(self) -> TransactionManager:
        return self._y_get_transaction_manager()

    def _owner_facade(self) -> Any:
        return object.__getattribute__(self, "owner")

    def _resolve_owner_arg(self, value: Any) -> Any:
        return self._owner_facade() if value is USE_OWNER else value

    def children_by_slot_id(self) -> dict[Any, Any]:
        return {}

    def iter_children(self) -> tuple[Any, ...]:
        return tuple()

    def committed_ui(self) -> tuple[Any, ...]:
        return ()

    def own_committed_ui(self) -> tuple[Any, ...]:
        return ()

    def own_committed_ui_entries(self) -> tuple[Any, ...]:
        return ()

    def parent_context(self) -> Any | None:
        return None
