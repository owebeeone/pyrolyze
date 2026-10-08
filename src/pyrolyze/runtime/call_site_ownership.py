"""Adapt explicit call-site ownership to one lifecycle-owned collection.

Public contexts can outlive their selection without keeping a binding accepted.
Each private collection owns an explicit reference per entry. Replacement copies
retain reused contexts, while new contexts transfer their initial reference.
Completion releases discarded collections explicitly: tracebacks and snapshots
must not delay cleanup. Python finalization is only an idempotent safety net.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Hashable, Mapping

from yidl_lifecycle.bindings import BindingBase

if TYPE_CHECKING:
    from .call_site_context import CallSiteContext


def _raise_cleanup_errors(errors: list[BaseException]) -> None:
    if len(errors) == 1:
        raise errors[0]
    if errors:
        raise BaseExceptionGroup("call-site completion failed", errors)


@dataclass(eq=False, slots=True)
class _CallSiteCollection(BindingBase):
    contexts: dict[Hashable, CallSiteContext] = field(default_factory=dict)

    @classmethod
    def replacing(
        cls,
        contexts: Mapping[Hashable, CallSiteContext],
        previous: _CallSiteCollection,
        current: _CallSiteCollection,
    ) -> _CallSiteCollection:
        retained = {
            id(context)
            for collection in (previous, current)
            for context in collection.contexts.values()
        }
        entries = dict(contexts)
        acquired: list[CallSiteContext] = []
        try:
            for context in entries.values():
                if id(context) in retained:
                    context.inc_ref()
                    acquired.append(context)
                retained.add(id(context))
        except BaseException as error:
            errors = [error]
            for context in acquired:
                try:
                    context.dec_ref()
                except BaseException as cleanup:
                    errors.append(cleanup)
            _raise_cleanup_errors(errors)
        return cls(entries)

    def accepted(self) -> None:
        super(_CallSiteCollection, self).accepted()
        for context in {id(value): value for value in self.contexts.values()}.values():
            context.accepted()

    def release(self) -> None:
        if not self.is_closed:
            self._closed = True
            self._close()

    def _close(self) -> None:
        entries, self.contexts = self.contexts, {}
        errors: list[BaseException] = []
        for context in entries.values():
            try:
                context.dec_ref()
            except BaseException as error:
                errors.append(error)
        _raise_cleanup_errors(errors)
