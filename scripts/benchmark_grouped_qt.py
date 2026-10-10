"""Compare accepted eager source with grouped Qt in fresh processes."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile

from pyrolyze_tools.generate_grouped_native_library import write_grouped_library
from pyrolyze_tools.generate_semantic_library import apply_learnings, discover_widget_classes, load_learnings
from pyrolyze_tools.preserve_native_catalog import catalog_public_names
from pyrolyze_tools.preserve_native_catalog import catalog_source_from_groups


PROBE = '''
import importlib,json,resource,sys,time,tracemalloc
import pyrolyze
import PySide6.QtWidgets
if sys.argv[5] == 'preloaded':
    from pyrolyze.compiler import load_transformed_namespace
    load_transformed_namespace('from pyrolyze.api import pyrolyze\\n@pyrolyze\\ndef empty() -> None:\\n    pass\\n',
                              module_name='compiler_preload')
sys.path.insert(0, sys.argv[1])
instrument = sys.argv[4] == 'memory'
if instrument: tracemalloc.start()
started = time.perf_counter()
library = importlib.import_module(sys.argv[2]).PySide6UiLibrary
for name in json.loads(sys.argv[3]): getattr(library, name)
elapsed = time.perf_counter() - started
specs = library.WIDGET_SPECS
print(json.dumps({'seconds': elapsed,
                  'python_bytes': tracemalloc.get_traced_memory()[0] if instrument else None,
                  'rss_peak': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  'loaded_groups': sum('.family_' in name for name in sys.modules),
                  'constructed_kinds': len(specs._specs) if hasattr(specs, '_specs') else len(specs)}))
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    accepted_input = parser.add_mutually_exclusive_group(required=True)
    accepted_input.add_argument("--accepted-source", type=Path)
    accepted_input.add_argument("--accepted-catalog", type=Path)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--preload-compiler", action="store_true")
    args = parser.parse_args()
    accepted = (args.accepted_source.read_text() if args.accepted_source
                else catalog_source_from_groups(args.accepted_catalog))
    names = catalog_public_names(accepted)
    widgets = [widget for widget in apply_learnings(discover_widget_classes("PySide6"), load_learnings("PySide6"))
               if widget.public_name in names]
    families = {widget.public_name: "layouts" if widget.class_name.endswith("Layout") else widget.module_name
                for widget in widgets}
    workloads = {"import": (), "label": ("CQLabel",),
                 "demo": ("CQMainWindow", "CQVBoxLayout", "CQLabel", "CQPushButton", "CQLineEdit", "CQComboBox")}
    with tempfile.TemporaryDirectory(prefix="qt-group-bench-") as temporary:
        root = Path(temporary)
        eager = root / "eager"
        eager.mkdir()
        (eager / "__init__.py").write_text("")
        (eager / "facade.py").write_text(accepted)
        packages = {"eager": eager}
        for cap in (1, 4, 8, 16):
            package = root / f"grouped_{cap}"
            write_grouped_library("PySide6", widgets, families=families, maximum_kinds=cap,
                                  output_dir=package, accepted_source=accepted)
            packages[package.name] = package
        for name, package in packages.items():
            for workload, members in workloads.items():
                command = [sys.executable, "-c", PROBE, str(root), f"{name}.facade", json.dumps(members)]
                def run(mode: str) -> dict[str, object]:
                    result = subprocess.run([*command, mode, "preloaded" if args.preload_compiler else "normal"], env=os.environ.copy(),
                                            text=True, capture_output=True)
                    if result.returncode:
                        raise RuntimeError(result.stderr)
                    return json.loads(result.stdout.splitlines()[-1])
                cold = run("timing")
                warm = [run("timing") for _ in range(args.repeats)]
                memory = run("memory")
                print(json.dumps({"package": name, "workload": workload,
                                  "files": len(tuple(package.glob("*.py"))),
                                  "first_seconds": cold["seconds"],
                                  "warm_median_seconds": statistics.median(row["seconds"] for row in warm),
                                  **{key: memory[key] for key in ("python_bytes", "rss_peak", "loaded_groups", "constructed_kinds")}}), flush=True)


if __name__ == "__main__":
    main()
