from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Literal, TextIO

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.pyrolyze_pyside6 import create_window as create_pyside_window
from pyrolyze.pyrolyze_pyside6 import reconcile_window_content as reconcile_pyside_content
from pyrolyze.pyrolyze_tkinter import create_window as create_tk_window
from pyrolyze.pyrolyze_tkinter import reconcile_window_content as reconcile_tk_content
from pyrolyze.runtime import (
    RenderContext,
    TraceChannel,
    TraceRecord,
    configure_trace,
    configure_trace_from_env,
    dirtyof,
)


BackendName = Literal["pyside6", "tkinter"]
SOURCE_PATH = Path(__file__).with_name("grid_app.py")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the PyRolyze dynamic grid example.")
    parser.add_argument(
        "--backend",
        choices=("pyside6", "tkinter"),
        default="pyside6",
        help="Select the native UI backend.",
    )
    parser.add_argument(
        "--trace",
        action="append",
        help="Enable runtime trace channels (comma-separated). Use 'all' for every channel.",
    )
    parser.add_argument(
        "--trace-stdout",
        action="store_true",
        help="Write trace records to stdout instead of the Python logging subsystem.",
    )
    return parser


def _load_grid_app() -> Any:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    namespace = load_transformed_namespace(
        source,
        module_name="examples.grid_app",
        filename=str(SOURCE_PATH),
    )
    return namespace["grid_app"]


def _post_flush(host: Any, backend: BackendName, callback: Any) -> None:
    if backend == "pyside6":
        from PySide6.QtCore import QTimer

        QTimer.singleShot(0, callback)
        return

    host.root.after(0, callback)


def resolve_trace_channels(trace_tokens: list[str] | None) -> tuple[TraceChannel, ...]:
    if not trace_tokens:
        return ()

    channels: list[TraceChannel] = []
    seen: set[TraceChannel] = set()
    for token in trace_tokens:
        for part in token.split(","):
            name = part.strip().lower()
            if not name:
                continue
            if name == "all":
                for channel in TraceChannel:
                    if channel not in seen:
                        channels.append(channel)
                        seen.add(channel)
                continue
            channel = TraceChannel(name)
            if channel in seen:
                continue
            channels.append(channel)
            seen.add(channel)
    return tuple(channels)


def format_trace_record(record: TraceRecord) -> str:
    if record.fields:
        fields = " ".join(f"{key}={value!r}" for key, value in sorted(record.fields.items()))
        return f"{record.channel.value}.{record.event} {fields}"
    return f"{record.channel.value}.{record.event}"


def build_stdout_trace_sink(stream: TextIO) -> Any:
    def _sink(record: TraceRecord) -> None:
        stream.write(
            f"pid={os.getpid()} ppid={os.getppid()} {format_trace_record(record)}\n"
        )
        stream.flush()

    return _sink


def build_app_host(backend: BackendName) -> tuple[Any, RenderContext]:
    component = _load_grid_app()
    if backend == "pyside6":
        host = create_pyside_window("PyRolyze Dynamic Grid")
        reconcile_content = reconcile_pyside_content
    else:
        host = create_tk_window("PyRolyze Dynamic Grid")
        reconcile_content = reconcile_tk_content

    ctx = RenderContext()

    def reconcile_host() -> None:
        reconcile_content(
            host,
            ctx.committed_ui(),
            on_after_event=run_flush_and_reconcile,
        )

    def run_flush_and_reconcile() -> None:
        ctx.run_pending_invalidations()
        reconcile_host()

    def render_root() -> None:
        component._pyrolyze_meta._func(ctx, dirtyof())
        reconcile_host()

    def post_flush(callback: Any) -> None:
        _post_flush(
            host,
            backend,
            lambda: (
                callback(),
                reconcile_host(),
            ),
        )

    ctx.set_flush_poster(post_flush)
    ctx.mount(render_root)
    return host, ctx


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.trace_stdout:
        stream_argv = argv if argv is not None else sys.argv[1:]
        sys.stdout.write(
            f"process.start pid={os.getpid()} ppid={os.getppid()} "
            f"backend={args.backend} argv={stream_argv!r}\n"
        )
        sys.stdout.flush()
    channels = resolve_trace_channels(args.trace)
    sink = build_stdout_trace_sink(sys.stdout) if args.trace_stdout else None
    if channels:
        configure_trace(enabled=channels, sink=sink)
    elif args.trace_stdout:
        configure_trace_from_env(sink=sink)
    host, ctx = build_app_host(args.backend)
    try:
        if args.backend == "pyside6":
            return host.exec()
        host.run()
        return 0
    finally:
        ctx.close_app_contexts()


if __name__ == "__main__":
    raise SystemExit(main())
