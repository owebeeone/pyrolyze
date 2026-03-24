# Unified native API — implementation plans

This directory holds **per-backend implementation notes** for the unified
mount-based library and adapters (`dev-docs/UnifiedMountBasedNativeApi.md`,
`dev-docs/WidgetReconcilePlan.md`).

## Index

| Document | Scope |
| --- | --- |
| [README.md](README.md) | This index; cross-cutting work that is not owned by a single backend file. |
| [PySide6.md](PySide6.md) | Qt / PySide6 adapter and codegen touchpoints. |
| [Tkinter.md](Tkinter.md) | Tk / ttk (and tix where relevant) adapter touchpoints. |
| [DearPyGui.md](DearPyGui.md) | Dear PyGui adapter, dump, and generated `add_*` surface. |

## Cross-cutting (all backends)

Track these in **every** backend file where they apply; do not duplicate long
design prose—link back to the parent docs.

- **Canonical mount keys** — `dev-docs/MountKeys.md` + `pyrolyze.unified.mount_keys`;
  reference layouts still expand in `tests/unified/` / `examples/`.
- **Unified package** — `pyrolyze.unified` (`src/pyrolyze/unified/`): base +
  `QtUnifiedNativeLibrary` / `TkUnifiedNativeLibrary` / `DpgUnifiedNativeLibrary`,
  `get_unified_native_library()`, env `PYROLYZE_UNIFIED_BACKEND` (default `qt`).
- **App context policy keys** — theme / density / typography; readers only on
  create/update paths (not mount resolution).
- **Window proxy** — shell lifetime; `dev-docs/ReactiveRootWindowProxy.md`.
- **Mechanical extracts** — `dev-docs/widget-reconcile/`; re-run
  `scripts/extract_widget_catalogs.py` and `scripts/build_unified_coverage.py` when
  codegen or dump changes.
- **Tests** — mirror `src/pyrolyze/<unified>/...` under `tests/...`; use public
  PyRolyze forms in E2E tests (`pyrolyze/AGENTS.md`).
- **PyRolyze under pytest** — **pytest11** import hook (`pyrolyze.compiler.import_hook`)
  for on-disk modules with `#@pyrolyze`; optional `pyrolyze-import-hook-pth install`
  for plain `python` in a venv. **Dynamic** snippets still use
  `load_transformed_namespace` (`UnifiedMountBasedNativeApi.md`).

## Related documents

- `dev-docs/UnifiedMountBasedNativeApi.md`
- `dev-docs/WidgetReconcilePlan.md`
- `dev-docs/widget-reconcile/RoleMatrix.md`
- `dev-docs/widget-reconcile/AdditionalAnalysis.md` — mounts, `WIDGET_SPECS` samples, advert rules, DPG split
- `dev-docs/ReactiveRootWindowProxy.md`
