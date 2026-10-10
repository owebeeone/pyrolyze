"""Compiled dirty checks must not allocate generic placeholder slots."""

from typing import Any

import pytest

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.context_state_lcm.context_base import ContextBaseStateMgr


@pytest.mark.parametrize("dirty", [False, True])
def test_compiled_component_admission_does_not_depend_on_dirty_short_circuit(
    monkeypatch: pytest.MonkeyPatch, dirty: bool
) -> None:
    namespace = load_transformed_namespace(
        "from pyrolyze.api import pyrolyze\n"
        "@pyrolyze\n"
        "def child(value):\n"
        "    pass\n"
        "@pyrolyze\n"
        "def panel(value):\n"
        "    child(value)\n",
        module_name="slot_admission_repro",
    )
    requests: list[type[Any]] = []
    original = ContextBaseStateMgr.ensure_resolved_slot

    def trace(self: Any, slot_id: Any, slot_type: type[Any], **kwargs: Any) -> Any:
        requests.append(slot_type)
        return original(self, slot_id, slot_type, **kwargs)

    monkeypatch.setattr(ContextBaseStateMgr, "ensure_resolved_slot", trace)
    root = runtime.RenderContext()

    def render() -> None:
        with root.pass_scope():
            root.component_call(
                runtime.SlotId(runtime.ModuleId("admission-repro"), 1),
                namespace["panel"],
                1,
                dirty_state=runtime.dirtyof(value=dirty),
            )

    render()
    assert requests == [
        runtime.ComponentCallSlotContext,
        runtime.ComponentCallSlotContext,
    ]


@pytest.mark.parametrize("dirty", [False, True])
@pytest.mark.parametrize(
    "prefix, body, value, concrete_type",
    [
        (
            "from pyrolyze.api import UIElement, call_native\n"
            "@pyrolyze\n"
            "def frame(value):\n"
            "    call_native(UIElement)(kind='frame', props={'value':value})\n",
            "with frame(value):\n        pass",
            1,
            runtime.ContainerSlotContext,
        ),
        (
            "from pyrolyze.api import mount, MountSelector\n",
            "with mount(MountSelector.named(value)):\n        pass",
            "menu",
            runtime.DirectiveSlotContext,
        ),
        (
            "from pyrolyze.api import app_context_override\n"
            "from pyrolyze.runtime.app_context import AppContextKey\n"
            "KEY=AppContextKey('theme', lambda host: 'default')\n",
            "with app_context_override[KEY](value):\n        pass",
            "dark",
            runtime.AppContextOverrideSlotContext,
        ),
        (
            "from pyrolyze.api import keyed\n",
            "for item in keyed(value, key=lambda item:item):\n        pass",
            [1],
            runtime.KeyedLoopSlotContext,
        ),
    ],
    ids=["compiled-container", "mount", "override", "keyed-loop"],
)
def test_other_compiled_paths_do_not_allocate_generic_placeholders(
    monkeypatch: pytest.MonkeyPatch,
    dirty: bool,
    prefix: str,
    body: str,
    value: Any,
    concrete_type: type[Any],
) -> None:
    namespace = load_transformed_namespace(
        "from pyrolyze.api import pyrolyze\n"
        + prefix
        + "@pyrolyze\ndef panel(value):\n    "
        + body
        + "\n",
        module_name="other_slot_admission_repro",
    )
    requests: list[type[Any]] = []
    original = ContextBaseStateMgr.ensure_resolved_slot

    def trace(self: Any, slot_id: Any, slot_type: type[Any], **kwargs: Any) -> Any:
        requests.append(slot_type)
        return original(self, slot_id, slot_type, **kwargs)

    monkeypatch.setattr(ContextBaseStateMgr, "ensure_resolved_slot", trace)
    root = runtime.RenderContext()

    def render() -> None:
        with root.pass_scope():
            root.component_call(
                runtime.SlotId(runtime.ModuleId("other-admission-repro"), 1),
                namespace["panel"],
                value,
                dirty_state=runtime.dirtyof(value=dirty),
            )

    render()
    assert requests[:2] == [runtime.ComponentCallSlotContext, concrete_type]
    assert runtime.SlotContext not in requests
