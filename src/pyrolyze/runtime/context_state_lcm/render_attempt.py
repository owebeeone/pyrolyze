from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass, field
from types import TracebackType
from typing import NoReturn

from .lifecycle_adapter import LifecycleTransaction, TransactionManager


class RenderAttemptAborted(RuntimeError):
    """A locally reported failure prevented outer render publication."""


class RenderAttemptIncomplete(RuntimeError):
    """Transaction ownership was lost; neither undo nor reuse is certified."""


def _contains_exception(primary: BaseException, error: BaseException) -> bool:
    if primary is error:
        return True
    return isinstance(primary, BaseExceptionGroup) and any(
        _contains_exception(child, error) for child in primary.exceptions
    )


def _raise_with_cleanup(
    primary: BaseException, errors: list[BaseException]
) -> NoReturn:
    additional = [error for error in errors if not _contains_exception(primary, error)]
    if additional:
        raise BaseExceptionGroup(
            "render attempt cleanup failed", [primary, *additional]
        )
    raise primary


@dataclass(eq=False, slots=True)
class _RenderAttempt:
    """Own one explicit key; local scopes never complete its transaction.

    SC2's private field-only gate uses this helper; production routes do not.
    Root owners retain failed, uncertified completions instead of retrying.
    """

    manager: TransactionManager
    tx_key: Hashable
    transaction: LifecycleTransaction
    first_failure: BaseException | None = field(default=None, init=False)
    finished: bool = field(default=False, init=False)
    publication_uncertain: bool = field(default=False, init=False)
    _finishing: bool = field(default=False, init=False, repr=False)
    _entered: bool = field(default=False, init=False, repr=False)
    _reuse_ready: bool = field(default=False, init=False, repr=False)
    _integrity_lost: bool = field(default=False, init=False, repr=False)
    _identity_failure: RuntimeError | None = field(default=None, init=False, repr=False)
    _ownership_failure: RuntimeError | None = field(
        default=None, init=False, repr=False
    )
    _scopes: list[_LocalRenderScope] = field(
        default_factory=list, init=False, repr=False
    )
    _cleanup_errors: list[BaseException] = field(
        default_factory=list, init=False, repr=False
    )

    @classmethod
    def start(cls, manager: TransactionManager, tx_key: Hashable) -> _RenderAttempt:
        if manager.active_transaction_for(tx_key) is not None:
            raise RuntimeError("render transaction key is already active")
        transaction = manager.begin(tx_key)
        assert isinstance(transaction, LifecycleTransaction)
        return cls(manager, tx_key, transaction)

    @property
    def reuse_ready(self) -> bool:
        return self.finished and self._reuse_ready and not self._cleanup_errors

    def next_attempt(self) -> _RenderAttempt:
        if not self.reuse_ready:
            raise RuntimeError("render completion is not ready for reuse")
        return type(self).start(self.manager, self.tx_key)

    def fail(self, cause: BaseException) -> None:
        if self.first_failure is None:
            self.first_failure = cause

    def _require_open(self) -> None:
        if self.finished:
            raise RuntimeError("render attempt is already finished")
        if self._finishing:
            raise RuntimeError("render attempt is finishing")

    def _require_identity(self) -> None:
        if self.manager.active_transaction_for(self.tx_key) is not self.transaction:
            self._integrity_lost = True
            self.publication_uncertain = True
            if self._identity_failure is None:
                self._identity_failure = RuntimeError(
                    "owned render transaction is missing or replaced"
                )
            error = self._identity_failure
            self.fail(error)
            raise error

    def _check_ownership(self) -> None:
        if self._ownership_failure is not None:
            return
        try:
            self._require_identity()
            self.manager.require_sole_transaction_owner(self.transaction)
        except RuntimeError as error:
            self._ownership_failure = error
            self._integrity_lost = True
            self.fail(error)
            if self.first_failure is not error and error not in self._cleanup_errors:
                self._cleanup_errors.append(error)

    def is_scope_active(self, context: object) -> bool:
        return any(scope.context is context for scope in self._scopes)

    def scope(
        self,
        context: object,
        *,
        manager: TransactionManager,
        on_enter: Callable[[], None],
        on_exit: Callable[[], None],
        on_abort: Callable[[], None],
    ) -> _LocalRenderScope:
        return _LocalRenderScope(self, context, manager, on_enter, on_exit, on_abort)

    def begin_scope(
        self,
        context: object,
        *,
        manager: TransactionManager,
        on_enter: Callable[[], None],
        on_exit: Callable[[], None],
        on_abort: Callable[[], None],
    ) -> _LocalRenderScope:
        scope = self.scope(
            context,
            manager=manager,
            on_enter=on_enter,
            on_exit=on_exit,
            on_abort=on_abort,
        )
        scope._enter(allow_reentry=False)
        return scope

    def _admit(self, scope: _LocalRenderScope, *, allow_reentry: bool) -> bool:
        self._require_open()
        self._require_identity()
        if scope.manager is not self.manager:
            error = RuntimeError(
                "local render scope uses a different transaction manager"
            )
            self.fail(error)
            raise error
        if self.is_scope_active(scope.context):
            if allow_reentry:
                return False
            error = RuntimeError("local render scope is already active")
            self.fail(error)
            raise error
        self._scopes.append(scope)
        return True

    def _release(self, scope: _LocalRenderScope) -> None:
        self._scopes.remove(scope)

    def _discard_owned(self) -> None:
        # Identity, not the per-key integer token, fences external replacements.
        self._check_ownership()
        if self.manager.active_transaction_for(self.tx_key) is self.transaction:
            try:
                self.manager.rollback(self.tx_key)
            except BaseException as error:
                self._cleanup_errors.append(error)

    def _finish_failed(self, propagating: BaseException | None) -> None:
        self._discard_owned()
        self._reuse_ready = not self._integrity_lost and not self._cleanup_errors
        if propagating is not None:
            if self._cleanup_errors:
                _raise_with_cleanup(propagating, self._cleanup_errors)
            return
        if self._integrity_lost:
            aborted: RuntimeError = RenderAttemptIncomplete(
                "render transaction ownership was lost; completion is incomplete"
            )
        else:
            aborted = RenderAttemptAborted("render attempt aborted before publication")
        aborted.__cause__ = self.first_failure
        _raise_with_cleanup(aborted, self._cleanup_errors)

    def finish(self, propagating: BaseException | None = None) -> None:
        self._require_open()
        if any(scope._completing for scope in self._scopes):
            error = RuntimeError("local render scope is completing")
            self.fail(error)
            raise error
        if propagating is not None:
            self.fail(propagating)
        self._finishing = True
        try:
            if self._scopes and self.first_failure is None:
                self.fail(RuntimeError("render attempt has unexited local scopes"))
            for scope in reversed(tuple(self._scopes)):
                try:
                    assert self.first_failure is not None
                    scope.abort(self.first_failure)
                except BaseException:
                    # abort records its cleanup error; keep unwinding siblings.
                    pass
            self._check_ownership()
            if self.first_failure is not None:
                self._finish_failed(propagating)
                return
            try:
                self.manager.validate(self.tx_key)
            except BaseException as error:
                self.fail(error)
                self._discard_owned()
                self._reuse_ready = (
                    not self._integrity_lost and not self._cleanup_errors
                )
                _raise_with_cleanup(error, self._cleanup_errors)
            self._check_ownership()
            if self.first_failure is not None:
                self._finish_failed(None)
                return
            try:
                result = self.manager.commit_only(self.tx_key)
            except BaseException as error:
                # The pinned TM cannot distinguish prepare, apply, or after
                # failures here. Never invent an undo or certify a retry.
                self.fail(error)
                self.publication_uncertain = True
                raise
            if result is None:
                error = RuntimeError(
                    "render transaction acquired an external nested begin"
                )
                self.fail(error)
                self._integrity_lost = True
                self._discard_owned()
                _raise_with_cleanup(error, self._cleanup_errors)
            if (
                result != self.transaction.tx_id
                or self.manager.active_transaction_for(self.tx_key) is not None
                or self.first_failure is not None
            ):
                self.publication_uncertain = True
                self._integrity_lost = True
                error = RuntimeError(
                    "render completion changed ownership during publication"
                )
                cause = self.first_failure
                self.fail(error)
                raise error from cause
            self._reuse_ready = True
        finally:
            self.finished = True
            self._finishing = False

    def __enter__(self) -> _RenderAttempt:
        self._require_open()
        if self._entered:
            error = RuntimeError("render owner has already been entered")
            self.fail(error)
            raise error
        self._entered = True
        try:
            self._require_identity()
        except RuntimeError:
            self.finish()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        self.finish(exc)
        return False


@dataclass(eq=False, slots=True)
class _LocalRenderScope:
    owner: _RenderAttempt
    context: object
    manager: TransactionManager
    on_enter: Callable[[], None]
    on_exit: Callable[[], None]
    on_abort: Callable[[], None]
    _entered: bool = field(default=False, init=False, repr=False)
    _active: bool = field(default=False, init=False, repr=False)
    _completing: bool = field(default=False, init=False, repr=False)

    def _enter(self, *, allow_reentry: bool) -> None:
        if self._entered:
            raise RuntimeError("local render handle has already been entered")
        self._entered = True
        self._active = self.owner._admit(self, allow_reentry=allow_reentry)
        if self._active:
            try:
                self.on_enter()
            except BaseException as error:
                self.abort(error)
                raise

    def _require_active(self) -> None:
        if self._completing:
            error = RuntimeError("local render scope is already completing")
            self.owner.fail(error)
            raise error
        if not self._active:
            raise RuntimeError("local render scope is not active")

    def _release(self) -> None:
        self._active = False
        try:
            self.owner._release(self)
        except BaseException as error:
            self.owner.fail(error)
            self.owner._cleanup_errors.append(error)
            raise

    def finish(self) -> None:
        self._require_active()
        self._completing = True
        try:
            self.owner._require_open()
            self.owner._require_identity()
            self.on_exit()
        except BaseException as error:
            self.owner.fail(error)
            self._abort(error)
            raise
        else:
            self._release()
        finally:
            self._completing = False

    def abort(self, cause: BaseException) -> None:
        self._require_active()
        self._completing = True
        try:
            self._abort(cause)
        finally:
            self._completing = False

    def _abort(self, cause: BaseException) -> None:
        self.owner.fail(cause)
        errors: list[BaseException] = []
        try:
            self.on_abort()
        except BaseException as error:
            self.owner._cleanup_errors.append(error)
            errors.append(error)
        finally:
            try:
                self._release()
            except BaseException as error:
                errors.append(error)
        if errors:
            _raise_with_cleanup(cause, errors)

    def __enter__(self) -> _LocalRenderScope:
        self._enter(allow_reentry=True)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if self._active:
            if exc is None:
                self.finish()
            else:
                self.abort(exc)
        return False
