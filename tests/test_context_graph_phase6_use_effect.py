from __future__ import annotations

from typing import Callable

import pytest

from pyrolyze.runtime.context import CompValue, ModuleRegistry, RenderContext, SlotId, UseEffectRequest


module_registry = ModuleRegistry()
_MODULE_ID = module_registry.module_id("tests.context_graph_phase6_use_effect")

_EFFECT_SLOT = SlotId(_MODULE_ID, 1, line_no=10)


def _register_effect(
    effect_fn: Callable[[], Callable[[], None] | None],
    deps: tuple[object, ...] | None,
) -> UseEffectRequest:
    return UseEffectRequest(effect_fn=effect_fn, deps=deps)


def test_effect_runs_after_successful_commit_and_skips_stable_deps() -> None:
    ctx = RenderContext()
    log: list[tuple[str, str]] = []

    def render(label: CompValue[str]) -> None:
        with ctx.pass_scope():
            log.append(("render", label.value))

            def effect() -> Callable[[], None]:
                log.append(("setup", label.value))

                def cleanup() -> None:
                    log.append(("cleanup", label.value))

                return cleanup

            ctx.call_plain(_EFFECT_SLOT, _register_effect, effect, (label.value,))
            log.append(("render-end", label.value))

    render(CompValue("alpha", dirty=True))
    render(CompValue("alpha", dirty=False))
    render(CompValue("beta", dirty=True))

    assert log == [
        ("render", "alpha"),
        ("render-end", "alpha"),
        ("setup", "alpha"),
        ("render", "alpha"),
        ("render-end", "alpha"),
        ("render", "beta"),
        ("render-end", "beta"),
        ("cleanup", "alpha"),
        ("setup", "beta"),
    ]


def test_effect_without_deps_runs_after_every_successful_commit() -> None:
    ctx = RenderContext()
    log: list[tuple[str, str]] = []

    def render(label: CompValue[str]) -> None:
        with ctx.pass_scope():
            def effect() -> Callable[[], None]:
                log.append(("setup", label.value))

                def cleanup() -> None:
                    log.append(("cleanup", label.value))

                return cleanup

            ctx.call_plain(_EFFECT_SLOT, _register_effect, effect, None)

    render(CompValue("alpha", dirty=True))
    render(CompValue("beta", dirty=True))

    assert log == [
        ("setup", "alpha"),
        ("cleanup", "alpha"),
        ("setup", "beta"),
    ]


def test_effect_cleanup_runs_when_the_effect_slot_is_deactivated() -> None:
    ctx = RenderContext()
    log: list[tuple[str, str]] = []

    def render(show: CompValue[bool], label: CompValue[str]) -> None:
        with ctx.pass_scope():
            if show.value:
                def effect() -> Callable[[], None]:
                    log.append(("setup", label.value))

                    def cleanup() -> None:
                        log.append(("cleanup", label.value))

                    return cleanup

                ctx.call_plain(_EFFECT_SLOT, _register_effect, effect, ())

    render(CompValue(True, dirty=True), CompValue("alpha", dirty=True))
    render(CompValue(False, dirty=True), CompValue("alpha", dirty=False))

    assert log == [
        ("setup", "alpha"),
        ("cleanup", "alpha"),
    ]


def test_failed_pass_preserves_previously_committed_effect() -> None:
    ctx = RenderContext()
    log: list[tuple[str, str]] = []

    def render(label: CompValue[str], fail: CompValue[bool]) -> None:
        with ctx.pass_scope():
            def effect() -> Callable[[], None]:
                log.append(("setup", label.value))

                def cleanup() -> None:
                    log.append(("cleanup", label.value))

                return cleanup

            ctx.call_plain(_EFFECT_SLOT, _register_effect, effect, (label.value,))

            if fail.value:
                raise RuntimeError("boom")

    render(CompValue("alpha", dirty=True), CompValue(False, dirty=True))

    with pytest.raises(RuntimeError, match="boom"):
        render(CompValue("beta", dirty=True), CompValue(True, dirty=True))

    render(CompValue("gamma", dirty=True), CompValue(False, dirty=True))

    assert log == [
        ("setup", "alpha"),
        ("cleanup", "alpha"),
        ("setup", "gamma"),
    ]
