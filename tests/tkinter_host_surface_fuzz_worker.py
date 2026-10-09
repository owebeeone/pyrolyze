"""Isolated real-Tk history replay; seed covers source and mutation generation."""

from __future__ import annotations

import os
from math import isfinite
from random import Random
from secrets import randbits
from time import perf_counter
import tkinter

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.pyrolyze_native_tkinter import create_host, reconcile_window_content
from pyrolyze.runtime import dirtyof
from pyrolyze.runtime.context_lifecycle import RenderContext


class InjectedFailure(RuntimeError):
    pass


def snapshot(widget):
    options = widget.keys()
    text = str(widget.cget("text")) if "text" in options else ""
    # Creation order is not placement order. Ignore Tcl-generated path identities.
    children = widget.pack_slaves()
    return widget.winfo_class(), text, tuple(snapshot(child) for child in children)


def source(rng):
    lines = [
        "#@pyrolyze",
        "from pyrolyze.api import pyrolyze, mount",
        "from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary as Tk",
        "@pyrolyze",
        "def panel(" + ", ".join(f"f{i}: bool" for i in range(20)) + ", fail: int=0):",
        "    with Tk.CTtkFrame():",
        "        with mount(Tk.mounts.pack(side='top')):",
    ]
    groups = list(range(4))
    rng.shuffle(groups)
    for group in groups:
        lines.extend([
            "            with Tk.CTtkFrame():",
            f"                with mount(Tk.mounts.pack(side='{rng.choice(['left', 'top'])}')):",
        ])
        nodes = list(range(group * 5, group * 5 + 5))
        rng.shuffle(nodes)
        for index in nodes:
            kind = rng.choice(["CTtkLabel", "CTtkButton"])
            lines.extend([
                f"                    if f{index}:",
                f"                        Tk.{kind}(text='node-{index}')",
            ])
        if group == groups[1]:
            lines.extend(["            if fail == 1:", "                raise InjectedFailure('mid-tree')"])
    lines.extend(["        if fail == 2:", "            raise InjectedFailure('after-tree')"])
    return "\n".join(lines) + "\n"


def main():
    seed = int(os.environ["PYROLYZE_FUZZ_SEED"]) if "PYROLYZE_FUZZ_SEED" in os.environ else randbits(64)
    multiplier = int(os.environ.get("PYROLYZE_FUZZ_MULTIPLIER", "1"))
    seconds = float(os.environ.get("PYROLYZE_FUZZ_SECONDS", "2"))
    assert multiplier > 0 and isfinite(seconds) and seconds >= 0
    print(f"Replay: PYROLYZE_FUZZ_SEED={seed} PYROLYZE_FUZZ_MULTIPLIER={multiplier} PYROLYZE_FUZZ_SECONDS=0", flush=True)
    try:
        probe = create_host("Tk fuzz capability")
    except tkinter.TclError as exc:
        print(f"Tk root unavailable: {exc}")
        return 77
    probe.close()
    rng = Random(seed)
    work = 0.0
    checks = 0
    failures = 0
    for program in range(2):
        program_checks = 0
        generated = source(rng)
        namespace = load_transformed_namespace(
            generated, module_name=f"tests.tk_fuzz_{program}",
            filename="tests/fixtures/tk_history_fuzz.py",
            globals_dict={"InjectedFailure": InjectedFailure},
        )
        component = namespace["panel"]._pyrolyze_meta._func
        baselines = [tuple(bool(rng.getrandbits(1)) for _ in range(20)) for _ in range(5)]

        def render(context, host, flags, fail=0):
            context.mount(lambda: component(context, dirtyof(), *flags, fail=fail))
            reconcile_window_content(host, context.committed_ui())
            return snapshot(host.root_widget)

        recorded = []
        for flags in baselines:
            context, host = RenderContext(), create_host("Tk fresh baseline")
            try:
                recorded.append(render(context, host, flags))
            finally:
                context.close_app_contexts()
                host.close()
        start = perf_counter()
        deadline = start + seconds * multiplier / 2 if seconds else float("inf")
        history = []
        try:
            for flags, baseline in zip(baselines, recorded):
                context, host = RenderContext(), create_host("Tk retained replay")
                try:
                    assert render(context, host, flags) == baseline
                    for cycle in range(3 * multiplier):
                        if program_checks and perf_counter() >= deadline:
                            break
                        for _ in range(8):
                            mutation = tuple(bool(rng.getrandbits(1)) for _ in range(20))
                            history.append((mutation, 0))
                            render(context, host, mutation)
                        accepted = context.committed_ui()
                        physical = snapshot(host.root_widget)
                        for fault in (1, 2):
                            mutation = tuple(not value for value in flags)
                            history.append((mutation, fault))
                            try:
                                render(context, host, mutation, fault)
                            except InjectedFailure:
                                failures += 1
                            else:
                                raise AssertionError("injected failure did not execute")
                            assert context.committed_ui() == accepted
                            reconcile_window_content(host, context.committed_ui())
                            assert snapshot(host.root_widget) == physical
                        history.append((flags, 0))
                        assert render(context, host, flags) == baseline
                        checks += 1
                        program_checks += 1
                finally:
                    context.close_app_contexts()
                    host.close()
                if perf_counter() >= deadline:
                    break
        except BaseException:
            print(f"program={program}\nsource:\n{generated}\nhistory={history!r}", flush=True)
            raise
        work += perf_counter() - start
    print(f"fuzz_work_seconds={work:.3f} baseline_checks={checks} rollback_exceptions={failures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
