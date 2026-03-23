#!/usr/bin/env python3
"""DearPyGui UI library generator (discovery, shaping, fixture spec listing)."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyrolyze.backends.dearpygui.author_shape import shape_canonical_mountable
from pyrolyze.backends.dearpygui.discovery import (
    dearpygui_default_dump_path,
    iter_canonical_mountables,
    load_dearpygui_dump,
)
from pyrolyze.backends.dearpygui.specs import FIXTURE_WIDGET_SPECS

try:
    from pyrolyze_tools.dearpygui_emit_library import write_generated_library
except ModuleNotFoundError:  # pragma: no cover - script run with cwd = pyrolyze_tools/
    from dearpygui_emit_library import write_generated_library


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DearPyGui discovery and author-surface shaping for Pyrolyze code generation.",
    )
    parser.add_argument(
        "--dump-path",
        type=Path,
        default=None,
        help=f"Override path to dearpygui_api_dump.py (default: {dearpygui_default_dump_path()})",
    )
    parser.add_argument(
        "--print-summary",
        action="store_true",
        help="Print SUMMARY-derived counts after load.",
    )
    parser.add_argument(
        "--list-shaped",
        type=int,
        default=0,
        metavar="N",
        help="Print first N shaped mountables (kind + prop/event counts).",
    )
    parser.add_argument(
        "--list-fixture-spec-kinds",
        action="store_true",
        help="Print UiWidgetSpec kind keys from backends/dearpygui/specs.py (phase 3–5 harness).",
    )
    parser.add_argument(
        "--emit",
        action="store_true",
        help="Regenerate src/pyrolyze/backends/dearpygui/generated_library.py from the API dump.",
    )
    parser.add_argument(
        "--emit-to",
        type=Path,
        default=None,
        metavar="PATH",
        help="With --emit, write generated library to PATH instead of the default package path.",
    )
    args = parser.parse_args(argv)

    loaded = load_dearpygui_dump(dump_path=args.dump_path)
    if args.print_summary:
        print(f"DearPyGui {loaded.dearpygui_version} ({loaded.function_count} functions)")
        for name, count in sorted(loaded.classification_counts.items()):
            print(f"  {name}: {count}")

    canonical = iter_canonical_mountables(loaded)
    if args.list_shaped > 0:
        for item in canonical[: args.list_shaped]:
            shaped = shape_canonical_mountable(item)
            print(
                f"{shaped.public_kind_name} ({shaped.factory_name}): "
                f"{len(shaped.props)} props, {len(shaped.events)} events, "
                f"mounts={shaped.mount_point_names or '—'}",
            )

    if args.list_fixture_spec_kinds:
        for name in sorted(FIXTURE_WIDGET_SPECS.keys()):
            print(name)

    if args.emit:
        out = write_generated_library(output_path=args.emit_to)
        print(f"Wrote {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
