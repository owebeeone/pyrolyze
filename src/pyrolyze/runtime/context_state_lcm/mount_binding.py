"""A mount advertisement is candidate graph data, not an external resource.

The existing host publication method resolves provenance without mutating the
public surface. Lifecycle owns this immutable selection and its UI anchor;
discard/removal needs neither a lifetime wrapper nor imperative withdrawal.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pyrolyze.api import PyrolyzeMountAdvertisement, PyrolyzeMountAdvertisementRequest
from pyrolyze.runtime.slot_call_semantics import SlotCallBinding

if TYPE_CHECKING:
    from .mount_render import _MountRenderCompletion


@dataclass(frozen=True, slots=True)
class _MountAdvertisementBinding(SlotCallBinding):
    request: PyrolyzeMountAdvertisementRequest
    advertisement: PyrolyzeMountAdvertisement

    @classmethod
    def bind(
        cls,
        completion: _MountRenderCompletion,
        host: Any,
        request: PyrolyzeMountAdvertisementRequest,
    ) -> _MountAdvertisementBinding:
        completion.require_resource_owner()
        advertisement = host.publish_slot_call_mount_advertisement(request)
        completion.require_resource_owner()
        return cls(request, advertisement)

    def exposed_value(self) -> PyrolyzeMountAdvertisementRequest:
        return self.request

    def retained_advertisement(self) -> PyrolyzeMountAdvertisement:
        return self.advertisement
