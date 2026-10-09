from __future__ import annotations

import os
from dataclasses import dataclass
from math import isfinite
from random import Random
from secrets import randbits
from textwrap import indent
from time import perf_counter
from typing import Callable

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtWidgets import QLayout, QMainWindow, QWidget

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.pyrolyze_native_pyside6 import NativePySide6Host, create_host, reconcile_window_content
from pyrolyze.runtime import RenderContext, dirtyof
from pyrolyze.runtime.context_lifecycle import RenderContext as LifecycleRenderContext
from pyrolyze.testing.generic_backend import generate_argument_fuzz_replay


def _select_fuzz_seed() -> int:
    configured = os.environ.get("PYROLYZE_FUZZ_SEED")
    return randbits(64) if configured is None else int(configured)


FUZZ_SEED = _select_fuzz_seed()
_seed_generator = Random(FUZZ_SEED)
PROGRAM_SEEDS = tuple(_seed_generator.getrandbits(64) for _ in range(2))
PLACEMENT_SEED = _seed_generator.getrandbits(64)
HISTORY_SEED = _seed_generator.getrandbits(64)


@pytest.fixture(autouse=True)
def report_fuzz_seed() -> None:
    # Pytest includes this captured output when any test fails. One master seed
    # reproduces the generated programs and every mutation sequence.
    print(
        f"Mutation budget: {_fuzz_seconds() * _fuzz_multiplier():g} seconds. "
        f"Replay without deadline: PYROLYZE_FUZZ_SEED={FUZZ_SEED} "
        f"PYROLYZE_FUZZ_MULTIPLIER={_fuzz_multiplier()} PYROLYZE_FUZZ_SECONDS=0"
    )


def _fuzz_multiplier() -> int:
    multiplier = int(os.environ.get("PYROLYZE_FUZZ_MULTIPLIER", "1"))
    if multiplier < 1:
        raise ValueError("PYROLYZE_FUZZ_MULTIPLIER must be positive")
    return multiplier


def _fuzz_seconds() -> float:
    seconds = float(os.environ.get("PYROLYZE_FUZZ_SECONDS", "2"))
    if not isfinite(seconds) or seconds < 0:
        raise ValueError("PYROLYZE_FUZZ_SECONDS must be finite and nonnegative")
    return seconds


@dataclass(frozen=True, slots=True)
class _FuzzDeadline:
    expires_at: float | None

    @classmethod
    def start(cls) -> _FuzzDeadline:
        seconds = _fuzz_seconds()
        # Divide the module-wide mutation budget among placement and history
        # cases. Program compilation and fresh baseline setup are separate.
        cases = 2 + 3 * len(PROGRAM_SEEDS)
        allowance = seconds * _fuzz_multiplier() / cases
        return cls(None if seconds == 0 else perf_counter() + allowance)

    def allows_next(self, completed_checks: int) -> bool:
        # Never let an exhausted budget turn a test into a vacuous success.
        return completed_checks == 0 or self.expires_at is None or perf_counter() < self.expires_at


@dataclass(frozen=True, slots=True)
class PlacementMismatch:
    seed: int
    step: int
    arguments: tuple[bool, ...]
    expected: tuple[str, ...]
    incremental: tuple[str, ...]
    fresh: tuple[str, ...]


def _load_panel(*, nested: bool) -> Callable[..., None]:
    controls = (
        'with Qt.CQBoxLayout(QBoxLayout.Direction.LeftToRight, objectName="controls"):\n'
        '                    Qt.CQLabel("Count", objectName="count")'
        if nested
        else 'Qt.CQLabel("Count", objectName="controls")'
    )
    namespace = load_transformed_namespace(
        f'''
from PySide6.QtWidgets import QBoxLayout
from pyrolyze.api import pyrolyze
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt

@pyrolyze
def panel(show_top, show_page, reverse, changed):
    with Qt.CQMainWindow():
        with Qt.CQWidget():
            with Qt.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
                if show_top:
                    Qt.CQLabel("Top changed" if changed else "Top", objectName="top")
                if reverse:
                    Qt.CQLabel("B", objectName="b")
                    Qt.CQLabel("A", objectName="a")
                else:
                    Qt.CQLabel("A", objectName="a")
                    Qt.CQLabel("B", objectName="b")
                if show_page:
                    Qt.CQLabel("Page", objectName="page")
                {controls}
                Qt.CQLabel("Bottom", objectName="bottom")
''',
        module_name=f"host_surface_fuzz_{nested}",
        filename="tests/fixtures/host_surface_fuzz.py",
    )
    return namespace["panel"]._pyrolyze_meta._func


def _physical_order(window: QMainWindow) -> tuple[str, ...]:
    layout = window.centralWidget().layout()
    assert layout is not None
    names: list[str] = []
    for index in range(layout.count()):
        item = layout.itemAt(index)
        child = item.widget() if item.widget() is not None else item.layout()
        assert child is not None
        names.append(child.objectName())
    return tuple(names)


def _replay_placement(*, nested: bool) -> tuple[PlacementMismatch, ...]:
    panel = _load_panel(nested=nested)
    replay = generate_argument_fuzz_replay(
        seed=PLACEMENT_SEED,
        step_count=32 * _fuzz_multiplier(),
        argument_space={
            "show_top": (False, True),
            "show_page": (False, True),
            "reverse": (False, True),
            "changed": (False, True),
        },
    )
    host = create_host()
    context = RenderContext()
    mismatches: list[PlacementMismatch] = []
    retained_controls: object | None = None
    started = perf_counter()
    deadline = _FuzzDeadline.start()
    completed_checks = 0
    try:
        for index, step in enumerate(replay.steps):
            if not deadline.allows_next(completed_checks):
                break
            args = tuple(step.arguments.values())
            context.mount(lambda: panel(context, dirtyof(), *args))
            reconcile_window_content(host, context.committed_ui())
            assert isinstance(host.root_widget, QMainWindow)
            incremental = _physical_order(host.root_widget)
            if nested:
                layout = host.root_widget.centralWidget().layout()
                controls = next(
                    layout.itemAt(position).layout()
                    for position in range(layout.count())
                    if layout.itemAt(position).layout() is not None
                )
                if retained_controls is not None:
                    assert controls is retained_controls
                retained_controls = controls
            fresh_host = create_host()
            fresh_context = RenderContext()
            try:
                fresh_context.mount(lambda: panel(fresh_context, dirtyof(), *args))
                reconcile_window_content(fresh_host, fresh_context.committed_ui())
                assert isinstance(fresh_host.root_widget, QMainWindow)
                fresh = _physical_order(fresh_host.root_widget)
            finally:
                fresh_context.close_app_contexts()
                fresh_host.close()
            expected = (
                *(("top",) if step.arguments["show_top"] else ()),
                *(("b", "a") if step.arguments["reverse"] else ("a", "b")),
                *(("page",) if step.arguments["show_page"] else ()),
                "controls",
                "bottom",
            )
            # Fresh and incremental can be identically wrong. The authored order
            # is an independent oracle, not inferred from either backend result.
            if incremental != expected or fresh != expected:
                mismatches.append(
                    PlacementMismatch(replay.seed, index, args, expected, incremental, fresh)
                )
            completed_checks += 1
    finally:
        context.close_app_contexts()
        host.close()
    print(f"fuzz_work_seconds={perf_counter() - started:.6f} placement_checks={completed_checks}")
    return tuple(mismatches)


def test_seeded_widget_only_placement_matches_authored_order() -> None:
    assert not _replay_placement(nested=False)


def test_seeded_mixed_surface_replay_matches_authored_order() -> None:
    assert not _replay_placement(nested=True)


@dataclass(frozen=True, slots=True)
class PhysicalTree:
    kind: str
    name: str
    text: str | None
    children: tuple[PhysicalTree, ...]


@dataclass(frozen=True, slots=True)
class HistoryStep:
    flags: tuple[bool, ...]
    fail_before_controls: bool = False
    fail_after_children: bool = False


class InjectedRenderFailure(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class HistoryMismatch:
    program_seed: int
    seed: int
    baseline_flags: tuple[bool, ...]
    mutations: tuple[HistoryStep, ...]
    baseline: PhysicalTree
    restored: PhysicalTree


def _physical_tree(node: QWidget | QLayout) -> PhysicalTree:
    if isinstance(node, QMainWindow):
        children = (_physical_tree(node.centralWidget()),)
    elif isinstance(node, QWidget):
        layout = node.layout()
        children = () if layout is None else (_physical_tree(layout),)
    else:
        children_list: list[PhysicalTree] = []
        for index in range(node.count()):
            item = node.itemAt(index)
            child = item.widget() if item.widget() is not None else item.layout()
            assert child is not None
            children_list.append(_physical_tree(child))
        children = tuple(children_list)
    text = getattr(node, "text", None)
    return PhysicalTree(type(node).__name__, node.objectName(), None if text is None else text(), children)


def _history_panel_source(*, nested: bool, program_seed: int) -> str:
    # Four groups with five independent flags each. Generate authored source,
    # never lowered runtime calls, so the real compiler owns all slot behavior.
    parameters = ", ".join(f"flag_{index}" for index in range(20))
    random = Random(program_seed)
    group_order = list(range(4))
    random.shuffle(group_order)
    groups: list[str] = []
    widget_types = ("CQLabel", "CQPushButton", "CQLineEdit")
    for group in group_order:
        offset = group * 5
        def widget(name: str, text: str) -> str:
            kind = random.choice(widget_types)
            return f'Qt.{kind}({text}, objectName="{name}_{group}")'

        row_children = "\n".join(
            widget(f"control_{child}", repr(f"Value {child}"))
            for child in range(random.randint(1, 3))
        )
        controls_widget = widget("controls", '"Count"')
        controls = (
            f'with Qt.CQBoxLayout(QBoxLayout.Direction.LeftToRight, objectName="controls_{group}"):\n'
            + indent(row_children, "    ")
            if nested
            else controls_widget
        )
        controls = (
            'if fail_before_controls:\n'
            '    raise InjectedRenderFailure("before controls")\n'
            + controls
        )
        a, b = widget("a", '"A"'), widget("b", '"B"')
        blocks = [
            f"if flag_{offset}:\n" + indent(widget("top", '"Top"'), "    "),
            f"if flag_{offset + 1}:\n" + indent(b + "\n" + a, "    ")
            + "\nelse:\n" + indent(a + "\n" + b, "    "),
            f"if flag_{offset + 2}:\n" + indent(widget("page", '"Page"'), "    "),
            controls,
            widget("bottom", f'"Changed" if flag_{offset + 3} else "Bottom"'),
            f"if flag_{offset + 4}:\n" + indent(widget("tail", '"Tail"'), "    "),
        ]
        random.shuffle(blocks)
        container = random.choice((
            f'Qt.CQGroupBox("Group {group}", objectName="group_{group}")',
            f'Qt.CQWidget(objectName="group_{group}")',
        ))
        direction = random.choice(("TopToBottom", "LeftToRight"))
        group_source = (
            f"with {container}:\n"
            f"    with Qt.CQBoxLayout(QBoxLayout.Direction.{direction}):\n"
            + indent("\n".join(blocks), "        ")
        )
        groups.append(group_source)
    body = indent("\n".join(groups), "                ")
    body += '\n                if fail_after_children:\n                    raise InjectedRenderFailure("after children")'
    return f'''
from PySide6.QtWidgets import QBoxLayout
from pyrolyze.api import pyrolyze
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt

@pyrolyze
def panel({parameters}, fail_before_controls=False, fail_after_children=False):
    with Qt.CQMainWindow():
        with Qt.CQWidget():
            with Qt.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
{body}
'''


def _load_history_panel(*, nested: bool, program_seed: int) -> Callable[..., None]:
    namespace = load_transformed_namespace(
        _history_panel_source(nested=nested, program_seed=program_seed),
        module_name=f"history_surface_fuzz_{nested}_{program_seed}",
        filename="tests/fixtures/history_surface_fuzz.py",
        globals_dict={"InjectedRenderFailure": InjectedRenderFailure},
    )
    return namespace["panel"]._pyrolyze_meta._func


def _replay_history(
    *, nested: bool, program_seed: int, inject_failures: bool = False
) -> tuple[HistoryMismatch, ...]:
    panel = _load_history_panel(nested=nested, program_seed=program_seed)
    seed = HISTORY_SEED
    rounds = 3 * _fuzz_multiplier()
    replay = generate_argument_fuzz_replay(
        seed=seed,
        step_count=5 + 5 * rounds * 8,
        argument_space={f"flag_{index}": (False, True) for index in range(20)},
    )
    flags = tuple(tuple(step.arguments.values()) for step in replay.steps)
    mismatches: list[HistoryMismatch] = []
    context_type = LifecycleRenderContext if inject_failures else RenderContext

    def render(
        host: NativePySide6Host, context: RenderContext, inputs: tuple[bool, ...]
    ) -> PhysicalTree:
        context.mount(lambda: panel(context, dirtyof(), *inputs))
        reconcile_window_content(host, context.committed_ui())
        assert isinstance(host.root_widget, QMainWindow)
        return _physical_tree(host.root_widget)

    baselines: list[PhysicalTree] = []
    for inputs in flags[:5]:
        host = create_host()
        context = context_type()
        try:
            baselines.append(render(host, context, inputs))
        finally:
            context.close_app_contexts()
            host.close()

    mutation_index = 5
    started = perf_counter()
    deadline = _FuzzDeadline.start()
    completed_checks = 0
    for inputs, baseline in zip(flags[:5], baselines, strict=True):
        if not deadline.allows_next(completed_checks):
            break
        host = create_host()
        context = context_type()
        history: list[HistoryStep] = []
        try:
            assert render(host, context, inputs) == baseline
            for _ in range(rounds):
                if not deadline.allows_next(completed_checks):
                    break
                for mutation in flags[mutation_index:mutation_index + 8]:
                    render(host, context, mutation)
                    history.append(HistoryStep(mutation))
                mutation_index += 8
                if inject_failures:
                    accepted_ui = context.committed_ui()
                    assert isinstance(host.root_widget, QMainWindow)
                    accepted_tree = _physical_tree(host.root_widget)
                    for fail_before_controls, fail_after_children in ((True, False), (False, True)):
                        # Flip every input to force genuine candidate changes,
                        # rather than exercising an otherwise-skipped body.
                        failed_inputs = tuple(not flag for flag in inputs)
                        history.append(HistoryStep(failed_inputs, fail_before_controls, fail_after_children))
                        with pytest.raises(InjectedRenderFailure):
                            context.mount(lambda: panel(
                                context, dirtyof(), *failed_inputs,
                                fail_before_controls=fail_before_controls,
                                fail_after_children=fail_after_children,
                            ))
                        assert context.committed_ui() == accepted_ui, (
                            f"program_seed={program_seed} seed={seed} history={history}"
                        )
                        reconcile_window_content(host, context.committed_ui())
                        assert _physical_tree(host.root_widget) == accepted_tree, (
                            f"program_seed={program_seed} seed={seed} history={history}"
                        )
                restored = render(host, context, inputs)
                if restored != baseline:
                    mismatches.append(
                        HistoryMismatch(program_seed, seed, inputs, tuple(history), baseline, restored)
                    )
                history.append(HistoryStep(inputs))
                completed_checks += 1
        finally:
            context.close_app_contexts()
            host.close()
    print(f"fuzz_work_seconds={perf_counter() - started:.6f} baseline_checks={completed_checks}")
    return tuple(mismatches)


@pytest.mark.parametrize("program_seed", PROGRAM_SEEDS)
def test_twenty_flag_widget_history_returns_to_fresh_baselines(program_seed: int) -> None:
    assert not _replay_history(nested=False, program_seed=program_seed)


@pytest.mark.parametrize("program_seed", PROGRAM_SEEDS)
def test_twenty_flag_mixed_history_returns_to_fresh_baselines(program_seed: int) -> None:
    assert not _replay_history(nested=True, program_seed=program_seed)


@pytest.mark.parametrize("program_seed", PROGRAM_SEEDS)
def test_twenty_flag_history_rolls_back_early_and_late_failures_and_retries(program_seed: int) -> None:
    assert not _replay_history(nested=True, program_seed=program_seed, inject_failures=True)


def test_program_generation_is_seeded_and_varies_authored_structure() -> None:
    first = _history_panel_source(nested=True, program_seed=71)
    assert first == _history_panel_source(nested=True, program_seed=71)
    assert first != _history_panel_source(nested=True, program_seed=103)


def test_master_seed_environment_override_is_repeatable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYROLYZE_FUZZ_SEED", "12345")
    assert _select_fuzz_seed() == _select_fuzz_seed() == 12345


def test_expired_fuzz_budget_still_requires_one_complete_check() -> None:
    deadline = _FuzzDeadline(perf_counter() - 1)
    assert deadline.allows_next(0)
    assert not deadline.allows_next(1)
    assert _FuzzDeadline(None).allows_next(100)
