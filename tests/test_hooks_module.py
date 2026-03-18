from __future__ import annotations

from typing import Callable

from pyrolyze.api import use_effect as api_use_effect
from pyrolyze.api import use_state as api_use_state
from pyrolyze.hooks import use_effect, use_grip, use_mount, use_state, use_unmount
from pyrolyze.runtime import (
    ExternalStoreRef,
    ModuleRegistry,
    RenderContext,
    SlotId,
    UseEffectRequest,
)


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.hooks_module")

_STATE_SLOT = SlotId(_MODULE_ID, 1, line_no=10)
_EFFECT_SLOT = SlotId(_MODULE_ID, 2, line_no=11)
_GRIP_SLOT = SlotId(_MODULE_ID, 3, line_no=12)


def test_api_reexports_primary_hooks() -> None:
    assert api_use_state is use_state
    assert api_use_effect is use_effect


def test_use_state_provides_plain_tuple_and_stable_setter() -> None:
    ctx = RenderContext()
    observed: list[tuple[tuple[bool, bool], tuple[int, Callable[[int], None]]]] = []

    def render() -> Callable[[int], None]:
        with ctx.pass_scope():
            dirty_state, pair = ctx.call_plain(
                _STATE_SLOT,
                use_state,
                0,
                result_shape=("tuple", 2),
            )
            observed.append((dirty_state, pair))
            return pair[1]

    setter = render()
    same_setter = render()
    setter(7)
    after_update = render()

    assert observed[0][0] == (True, True)
    assert observed[0][1][0] == 0
    assert observed[1][0] == (False, False)
    assert observed[1][1][0] == 0
    assert same_setter is setter
    assert observed[2][0] == (True, True)
    assert observed[2][1][0] == 7
    assert after_update is setter


def test_use_effect_helpers_return_runtime_requests() -> None:
    setup_log: list[str] = []

    def effect() -> Callable[[], None]:
        setup_log.append("setup")

        def cleanup() -> None:
            setup_log.append("cleanup")

        return cleanup

    effect_request = use_effect(effect, deps=[1, "a"], __pyrolyze_ctx=None)
    mount_request = use_mount(lambda: setup_log.append("mount"), __pyrolyze_ctx=None)
    unmount_request = use_unmount(lambda: setup_log.append("unmount"), __pyrolyze_ctx=None)

    assert isinstance(effect_request, UseEffectRequest)
    assert effect_request.deps == (1, "a")
    assert effect_request.effect_fn() is not None
    assert setup_log == ["setup"]

    assert isinstance(mount_request, UseEffectRequest)
    assert mount_request.deps == ()
    cleanup = mount_request.effect_fn()
    assert cleanup is None
    assert setup_log == ["setup", "mount"]

    assert isinstance(unmount_request, UseEffectRequest)
    assert unmount_request.deps == ()
    cleanup = unmount_request.effect_fn()
    assert callable(cleanup)
    cleanup()
    assert setup_log == ["setup", "mount", "unmount"]


def test_use_grip_coerces_external_store_refs_and_ref_providers() -> None:
    notifications: list[str] = []

    def subscribe(listener: Callable[[], None]) -> Callable[[], None]:
        notifications.append("subscribe")
        listener()

        def unsubscribe() -> None:
            notifications.append("unsubscribe")

        return unsubscribe

    def get() -> str:
        return "warm"

    direct = ExternalStoreRef(identity="weather", subscribe=subscribe, get=get)

    class GripHandle:
        def ref(self) -> ExternalStoreRef[str]:
            return direct

    assert use_grip(direct) is direct
    assert use_grip(GripHandle()) is direct
