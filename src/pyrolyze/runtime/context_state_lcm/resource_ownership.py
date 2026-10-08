"""Bridge lifecycle ownership to explicitly counted external resources.

Only private lifecycle fields retain these wrappers. Value snapshots and external
callbacks may retain the resource, but never the wrapper: otherwise incidental
Python references would postpone unsubscribe or effect cleanup. Constructing a
wrapper transfers a resource's initial reference; each additional application
owner must retain one explicitly.

Failed candidates release explicitly because tracebacks can retain private
evaluation locals. Release and later Python finalization share one idempotent
path, so neither can double-release the resource. This is ownership adaptation,
not another transaction manager or field-publication mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass

from yidl_lifecycle.bindings import BindingBase
from yidl_lifecycle.bindings_refcount import BindingBase as RefCountedBindingBase


@dataclass(eq=False, slots=True)
class _ResourceOwner(BindingBase):
    resource: RefCountedBindingBase | None

    @classmethod
    def retain(cls, resource: RefCountedBindingBase) -> _ResourceOwner:
        resource.inc_ref()
        return cls(resource)

    def release(self) -> None:
        if not self.is_closed:
            self._closed = True
            self._close()

    def _close(self) -> None:
        resource, self.resource = self.resource, None
        if resource is not None:
            resource.dec_ref()
