from __future__ import annotations

from typing import Callable

import pytest

from pyrolyze.runtime.context import DirtyStateContext, ModuleRegistry, RenderContext, SlotId, UseEffectRequest, dirtyof


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

    def render(label: str, __pyr_dirty_state: DirtyStateContext) -> None:
        _ = __pyr_dirty_state
        with ctx.pass_scope():
            log.append(("render", label))

            def effect() -> Callable[[], None]:
                log.append(("setup", label))

                def cleanup() -> None:
                    log.append(("cleanup", label))

                return cleanup

            ctx.call_plain(_EFFECT_SLOT, _register_effect, effect, (label,))
            log.append(("render-end", label))

    render("alpha", dirtyof(label=True))
    render("alpha", dirtyof(label=False))
    render("beta", dirtyof(label=True))

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

    def render(label: str, __pyr_dirty_state: DirtyStateContext) -> None:
        _ = __pyr_dirty_state
        with ctx.pass_scope():
            def effect() -> Callable[[], None]:
                log.append(("setup", label))

                def cleanup() -> None:
                    log.append(("cleanup", label))

                return cleanup

            ctx.call_plain(_EFFECT_SLOT, _register_effect, effect, None)

    render("alpha", dirtyof(label=True))
    render("beta", dirtyof(label=True))

    assert log == [
        ("setup", "alpha"),
        ("cleanup", "alpha"),
        ("setup", "beta"),
    ]


def test_effect_cleanup_runs_when_the_effect_slot_is_deactivated() -> None:
    ctx = RenderContext()
    log: list[tuple[str, str]] = []

    def render(show: bool, label: str, __pyr_dirty_state: DirtyStateContext) -> None:
        _ = __pyr_dirty_state
        with ctx.pass_scope():
            if show:
                def effect() -> Callable[[], None]:
                    log.append(("setup", label))

                    def cleanup() -> None:
                        log.append(("cleanup", label))

                    return cleanup

                ctx.call_plain(_EFFECT_SLOT, _register_effect, effect, ())

    render(True, "alpha", dirtyof(show=True, label=True))
    render(False, "alpha", dirtyof(show=True, label=False))

    assert log == [
        ("setup", "alpha"),
        ("cleanup", "alpha"),
    ]


def test_failed_pass_preserves_previously_committed_effect() -> None:
    ctx = RenderContext()
    log: list[tuple[str, str]] = []

    def render(label: str, fail: bool, __pyr_dirty_state: DirtyStateContext) -> None:
        _ = __pyr_dirty_state
        with ctx.pass_scope():
            def effect() -> Callable[[], None]:
                log.append(("setup", label))

                def cleanup() -> None:
                    log.append(("cleanup", label))

                return cleanup

            ctx.call_plain(_EFFECT_SLOT, _register_effect, effect, (label,))

            if fail:
                raise RuntimeError("boom")

    render("alpha", False, dirtyof(label=True, fail=True))

    with pytest.raises(RuntimeError, match="boom"):
        render("beta", True, dirtyof(label=True, fail=True))

    render("gamma", False, dirtyof(label=True, fail=False))

    assert log == [
        ("setup", "alpha"),
        ("cleanup", "alpha"),
        ("setup", "gamma"),
    ]
