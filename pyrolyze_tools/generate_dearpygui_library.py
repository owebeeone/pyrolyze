#!/usr/bin/env python3
"""DearPyGui UI library generator entrypoint (phases 1–2: discovery + learnings shaping)."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyrolyze.backends.dearpygui.author_shape import shape_canonical_mountable
from pyrolyze.backends.dearpygui.discovery import (
    dearpygui_default_dump_path,
    iter_canonical_mountables,
    load_dearpygui_dump,
)


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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
