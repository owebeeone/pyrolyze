"""Offline grouped Qt generation; promotion requires exclusive maintenance."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from collections.abc import Sequence

from pyrolyze_tools.generate_grouped_native_library import write_grouped_library
from pyrolyze_tools.generate_semantic_library import apply_learnings, discover_widget_classes, load_learnings
from pyrolyze_tools.generated_library_publication import GenerationPublication


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maximum-kinds", type=int, required=True)
    parser.add_argument("--staging-dir", type=Path, required=True)
    parser.add_argument("--promote-to", type=Path)
    accepted = parser.add_mutually_exclusive_group()
    accepted.add_argument("--accepted-source", type=Path)
    accepted.add_argument("--accepted-catalog", type=Path)
    args = parser.parse_args(argv)
    if args.promote_to is not None:
        worker = [sys.executable, "-m", "pyrolyze_tools.generate_grouped_qt_library",
                  "--maximum-kinds", str(args.maximum_kinds), "--staging-dir", str(args.staging_dir)]
        if args.accepted_source is not None:
            worker.extend(["--accepted-source", str(args.accepted_source)])
        else:
            catalog = args.accepted_catalog or args.promote_to
            if catalog.exists():
                worker.extend(["--accepted-catalog", str(catalog)])
        subprocess.run(worker, check=True)
        GenerationPublication(args.promote_to).promote(args.staging_dir)
        return 0
    widgets = apply_learnings(discover_widget_classes("PySide6"), load_learnings("PySide6"))
    accepted_source = args.accepted_source.read_text() if args.accepted_source else None
    catalog = args.accepted_catalog or args.promote_to
    if accepted_source is None and catalog is not None and catalog.exists():
        from pyrolyze_tools.preserve_native_catalog import catalog_source_from_groups

        accepted_source = catalog_source_from_groups(catalog)
    if accepted_source is not None:
        from pyrolyze_tools.preserve_native_catalog import catalog_public_names

        names = catalog_public_names(accepted_source)
        widgets = [widget for widget in widgets if widget.public_name in names]
        if {widget.public_name for widget in widgets} != names:
            raise ValueError("discovery cannot represent the accepted catalog")
    families = {
        widget.public_name: "layouts" if widget.class_name.endswith("Layout") else widget.module_name
        for widget in widgets
    }
    write_grouped_library("PySide6", widgets, families=families,
                          maximum_kinds=args.maximum_kinds, output_dir=args.staging_dir,
                          accepted_source=accepted_source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
