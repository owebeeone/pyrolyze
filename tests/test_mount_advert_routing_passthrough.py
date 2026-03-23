from __future__ import annotations

from pyrolyze.api import MountDirective, MountSelector, UIElement
from pyrolyze.backends.mountable_engine import MountableEngine

from .test_mountable_engine_generic import _explicit_mount_specs


class _ProbeRoutingEngine(MountableEngine):
    def __init__(self) -> None:
        super().__init__(_explicit_mount_specs())
        self.routed_inputs: list[tuple[str, tuple[object, ...] | None]] = []

    def _build_mount_advert_dag(self, parent_spec, mount_inputs):  # type: ignore[override]
        self.routed_inputs = [
            (mount_input.element.kind, mount_input.selectors)
            for mount_input in mount_inputs
        ]
        return list(mount_inputs)


def test_mount_advert_routing_layer_sees_natural_inputs_and_preserves_plain_mount_behavior() -> None:
    engine = _ProbeRoutingEngine()
    menu = MountSelector.named("menu")

    node = engine.mount(
        UIElement(
            kind="Host",
            props={"name": "host"},
            children=(
                MountDirective(
                    selectors=(menu,),
                    children=(
                        UIElement(kind="Choice", props={"name": "File"}),
                        UIElement(kind="Choice", props={"name": "Edit"}),
                    ),
                ),
                UIElement(kind="Choice", props={"name": "Body"}),
            ),
        ),
        slot_id=("root", "host", 1),
        call_site_id=101,
    )

    host = node.mountable
    assert [child.name for child in host.menu_children] == ["File", "Edit"]
    assert [child.name for child in host.widget_children] == ["Body"]
    assert engine.routed_inputs == [
        ("Choice", (menu,)),
        ("Choice", (menu,)),
        ("Choice", None),
    ]
