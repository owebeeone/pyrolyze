# Code janitor report — py-rolyze

**Scope:** Read-only review of the `py-rolyze` package (sources, tools, tests, examples). No code was changed for this document.

**Collected signal date:** 2026-03-23 (local workspace snapshot).

---

## Executive summary

The tree already separates **compiler**, **runtime**, **backends**, and **codegen tools**, but several areas carry **disproportionate weight**: a very large runtime module (`context.py`), large per-backend shim modules, an enormous **checked-in generated** DearPyGui library, and a very large **hand-maintained** PySide6 learnings table. The **test suite is broad** (~370 tests across 59 files) with clear **families of parallel tests** (context-graph phases, AST rewrite phases, per-backend wrappers and grid examples) where **count could be reduced or runtime improved** through parametrization and shared fixtures without necessarily losing coverage.

---

## Scale (quick numbers)

| Area | Approximate size |
|------|------------------|
| Tests collected (`pytest --collect-only`) | **370** |
| Top-level `tests/test_*.py` files | **59** |
| `src/pyrolyze/**/*.py` files | **68** |
| `examples/*.py` files | **16** |

Largest **non-generated** Python modules under `src/pyrolyze/` (by line count, approximate):

| Module | ~Lines | Note |
|--------|--------|------|
| `runtime/context.py` | ~2.4k | Core graph / render / scheduling |
| `compiler/kernels/v3_14/rewrite.py` | ~2.2k | AST lowering |
| `backends/pyside6/learnings.py` | ~7.2k | **Manual** learnings blob |
| `backends/dearpygui/generated_library.py` | ~23k | **Generated**, checked in |
| `pyrolyze_tkinter.py` / `pyrolyze_pyside6.py` | ~1.2k / ~1.3k | Parallel adapter patterns |
| `backends/mountable_engine.py` | ~1.0k | Shared mount logic |
| `testing/hydo.py` | ~1.0k | Test helpers |

Largest **tooling** script:

| Script | ~Lines |
|--------|--------|
| `pyrolyze_tools/generate_semantic_library.py` | ~2.4k |

Largest **example**:

| File | ~Lines |
|------|--------|
| `examples/studio_app.py` | ~3.3k |

---

## Where “bloat” is real vs acceptable

### Acceptable / intentional bulk

- **`backends/dearpygui/generated_library.py`:** Documented as generated and checked in; size is a consequence of API surface, not sloppy code.
- **Golden / versioned compiler tests:** `tests/versioned_test_harness.py` and `test_ast_goldens.py` support multiple Python/kernel combinations; some duplication is the price of **reproducible** compiler output.

### Worth targeting for cleaner structure

1. **`runtime/context.py` (~2.4k lines)**  
   Single module mixes many concerns (dirty state, slots, external stores, scheduling, commit paths, tracing hooks, etc.). Even if behavior stays identical, **splitting by subdomains** (e.g. graph identity, invalidation, commit, scheduler façade) would improve navigation, test targeting, and reviewability.

2. **`compiler/kernels/v3_14/rewrite.py` (~2.2k lines)**  
   Same story as context: one huge rewrite pipeline. **Phase-local modules** or a small “rewrite step” registry would reduce merge conflict pain and make “which pass broke this?” faster to answer.

3. **`backends/pyside6/learnings.py` (~7.2k lines, manual)**  
   This is the largest **hand-edited** concentration of data in `src`. Long-term maintainability may improve if large chunks move to **machine-readable inputs** (TOML/JSON) merged at build time, or are **split by widget family** with thin aggregator imports—without changing the public `LEARNINGS` object shape.

4. **`pyrolyze_tools/generate_semantic_library.py` (~2.4k lines)**  
   Natural candidate to break into packages: discovery, Qt introspection, learnings merge, codegen, CLI.

5. **`examples/studio_app.py` (~3.3k lines)**  
   Likely a kitchen-sink demo. For contributor clarity, **multiple modules** (e.g. panels, models, DPG wiring) or moving non-essential experiments out of the default example path would shrink the “face” of the repo.

---

## Parallelism and duplication (backends)

`pyrolyze_tkinter.py` and `pyrolyze_pyside6.py` share the same structural skeleton: module registry, owner slot, node mapper protocol, layout state, reconciliation via `mount_reconciler` / `ui_nodes`. That is **healthy reuse of runtime**, but the **per-kind mappers and layout metrics** will drift unless periodically reconciled.

**Janitor-style follow-ups (conceptual):**

- Extract **shared adapter utilities** (e.g. ordered child lists, metrics dict shape, trace emission patterns) if they are copy-pasted between backends.
- Consider a **single internal test matrix** for “create / update prop / reorder children / detach” that runs against each `UiBackendAdapter` implementation (would cut triplicated narrative tests—see test section).

---

## Test suite: consolidation and optimization opportunities

### Per-file test counts (distribution)

Roughly **8% of tests** live in one file: `test_generate_semantic_library_tool.py` (**31** tests, ~892 lines). Most other files are **smaller clusters**; several files collect only **1–2** tests (high **process/fixture overhead** relative to assertions).

### High-value merge / parametrize candidates

1. **Context graph phases (`test_context_graph_phase*.py`, `test_context_graph_no_comp_value_api.py`)**  
   ~10 files with overlapping themes (phase1…phase8, scheduler, native UI, invalidation kernel). If phases are **stable product boundaries**, keeping separate files is fine. If the goal is **leaner CI**, consider:
   - One module per **major milestone** (e.g. “through phase 4”, “component call + effects”, “native + scheduler”) with **parametrized** scenarios, or
   - Shared **fixtures** for building minimal graphs so each test file stops re-stating similar bootstrapping.

2. **AST rewrite tests (`test_ast_phase*.py`, mount directive, kernel selection, compiler facade)**  
   Similar phase-oriented split. **Parametrizing** “input snippet → expected IR / marker” across phases (where safe) could **reduce test count** while keeping one assertion per dimension.

3. **Grid example tests**  
   Four related entry points:
   - `test_examples_grid_app.py` — PyRolyze UI tree / `RenderContext` (generic)
   - `test_examples_grid_app_tkinter.py`, `test_examples_grid_app_dearpygui_native.py`, `test_examples_grid_app_pyside6_native.py` — native hosts  
   **Opportunity:** one **parametrized** “grid scenario” spec (compile, mount, one interaction) with a **backend fixture** (abstract: “build host + pump events”). That reduces four files’ worth of duplicated “find button / pump / assert label” patterns.

4. **Wrapper tests (`test_tkinter_wrapper.py`, `test_pyside6_wrapper.py`)**  
   Parallel structure (~9 vs ~12 tests). A **shared parametrized suite** over a small `BackendUnderTest` protocol would shrink total tests and enforce parity.

5. **DearPyGui cluster**  
   `test_dearpygui_adapter_phases_3_5.py`, `test_dearpygui_discovery_and_learnings.py`, `test_dearpygui_live_host.py`, `test_dearpygui_generated_library.py`, examples mount/trees—some could share **DPG lifecycle fixtures** (create context once per session) to speed runs, even if test **count** stays similar.

6. **Mount / engine tests**  
   `test_mountable_engine_generic.py`, `test_hydo_mountable_engine.py`, `test_generated_hydo_mountable_engine.py`, `test_mount_point_runtime.py` overlap at the “mount spec → engine behavior” level. Auditing for **redundant scenarios** (same assertion, different fake) could drop tests without losing coverage.

### Tests that are “cheap wins” for speed, not necessarily fewer tests

- **`test_ast_goldens.py` (17 tests):** Already table-driven via `gold_cases.toml`; ensure golden regeneration is **cached** in local dev and CI where possible.
- **Version matrix:** `[tool.pyrolyze.test-matrix]` lists four Python versions; full matrix multiplies wall time. **Document** which subset is “PR gate” vs “nightly” if not already.

### Repo hygiene note

Under `tests/` there may be local artifacts such as **`.uv-venvs`** (tooling caches). If those are not meant to be committed, ensure they are **ignored** so greps and file watchers stay fast and clones stay small.

---

## Packaging and dependencies

- **PySide6** is a **core** dependency in `pyproject.toml`, even though some tests and workflows are Tk- or DearPyGui-only. That is convenient for one wheel but forces install weight for minimal consumers. A future split into **optional extras** (e.g. `pyside6`, `tk` is stdlib, `dpg`) could reduce perceived bloat—at the cost of more conditional imports and CI matrices.

---

## Suggested prioritization (no code — action order)

1. **Split or document** `runtime/context.py` and `rewrite.py` boundaries (biggest readability win).
2. **Deduplicate grid + wrapper tests** via shared fixtures/parametrization (good test-count / CI-time ROI).
3. **Tame `pyside6/learnings.py`** growth (data format or file split).
4. **Modularize** `generate_semantic_library.py` and trim `studio_app.py` surface for new contributors.

---

## How to refresh this report

```bash
cd py-rolyze
uv run --with pytest pytest --collect-only -q | tail -3
find tests -maxdepth 1 -name 'test_*.py' | wc -l
find src -name '*.py' -exec wc -l {} + | sort -n | tail -20
```

Re-run after refactors to validate that test count and largest-file lists moved in the intended direction.
