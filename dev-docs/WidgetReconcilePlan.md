# Widget Reconcile Plan

## Purpose

This document is the **execution plan** for reconciling Dear PyGui, PySide6, and
Tkinter widget surfaces into a **small unified API** with identical names per
operation across adapters. It complements
`dev-docs/UnifiedMountBasedNativeApi.md` (architecture and cutover policy) by
defining **how** we analyze thousands of native types without manual review of
every widget, and **acceptance criteria** for each phase.

## Deliverables (summary)

These are the **concrete artifacts** the reconcile track produces. Phase
acceptance checklists in each section below remain authoritative; this table is
the rollup.

| Deliverable | Owner / home | When |
| --- | --- | --- |
| **Extract tooling + schema** | `scripts/extract_widget_catalogs.py` + `dev-docs/widget-reconcile/README.md` | Phase 0 |
| **Per-backend extract files** (JSON/CSV) | `dev-docs/widget-reconcile/widget_catalog_extract.json` | Phase 0 → ongoing |
| **Role triage matrix** | `dev-docs/widget-reconcile/RoleMatrix.md` | Phase 1 (expand over time) |
| **Role glossary** | `RoleMatrix.md` § Role glossary | Phase 1 (expand over time) |
| **Canonical mount key spec** | Doc section or sibling file; keys + semantics + `default` policy | Phase 2 |
| **Three reference layouts** | `examples/` and/or tests (DPG, Qt, Tk) using `advertise_mount` + `mount` only | Phase 2 |
| **Unified package + three adapter classes** | Abstract base + Qt/Tk/DPG subclasses (same pattern as `*UiLibrary`); env/CLI backend selection | Phase 3+ |
| **Mirrored test tree** | `tests/...` subtrees aligned with unified source layout (per `UnifiedMountBasedNativeApi.md`) | Phase 3+ |
| **`.venv` / pytest + PyRolyze hook** | Documented (and optionally required) way to auto-enable import transformation for `pytest` | Phase 3+ (dev UX) |
| **Wave checklists** | Enumerated unified symbols per wave; checked off as implemented | Phase 3+ |
| **App context policy keys + docs** | Toolkit-agnostic module + brief semantics | Phase 4 |
| **Context integration tests** | Per backend (or documented skip) | Phase 4 |
| **Removal of `backends/common/`** | Delete package; fix imports; no shims | Phase 5 |
| **Contributor doc updates** | Pointers to unified API + reconcile plan | Phase 5 |

Related but **not** solely owned by this plan: reactive **root / window proxy**
model for toolkit window lifetime (`dev-docs/ReactiveRootWindowProxy.md`).


## Principles

1. **Do not analyze widget-by-widget equally.** The full native catalogs stay in
   generated code and dumps; the unified surface stays intentionally small.
2. **Mechanical extraction first.** Lists of kinds, props, and mount families come
   from codegen outputs, `UiInterface` metadata, and (for Dear PyGui) the
   normalized API dump (`backends/dearpygui/discovery.py`), not from ad hoc
   reading of megabyte `generated_library.py` files.
3. **Semantic roles, not raw names.** Collapse native kinds into a finite set of
   roles (e.g. text entry, toggle, ordered container). Each role gets one row
   in a triage matrix.
4. **Triage every role:** **portable**, **best-effort**, or **toolkit-only**.
   Only portable and best-effort roles earn unified names in the first waves.
5. **Priority by author journeys:** shell and mounts, then high-frequency
   controls, then containers that interact with mounts and context, then
   long-tail items when a concrete example demands them.

## Cross-References

Phases **1–5** here align with **A–E** in `UnifiedMountBasedNativeApi.md`; **Phase
0** is preparatory (extract tooling only).

- Architecture, app context, and deletion of `backends/common/`:
  `dev-docs/UnifiedMountBasedNativeApi.md`
- Hierarchical app context behavior:
  `dev-docs/HierarchicalContextManagementPlan.md`,
  `dev-docs/HierarchicalContextManagement.md`
- Shared vocabulary for props and accessors: `src/pyrolyze/backends/model.py`
- Per-backend implementation checklists: `dev-docs/unified_plan/`


## Phase 0 — Tooling and outputs

### Goal

Make inventory **repeatable**: scripts or documented commands that emit
structured lists per backend (JSON or CSV checked in under `dev-docs/` or a
dedicated `dev-docs/widget-reconcile/` folder—exact path chosen when Phase 0
runs).

### Work

- Dear PyGui: leverage `DpgLoadedDump` / canonical mountable records; document
  how to regenerate the dump if the pipeline already supports it.
- PySide6 / Tkinter: define a minimal extractor over generated artifacts (e.g.
  walk `UiInterface` / kind tables / engine registries—whatever is most stable
  in-tree) so output shape matches DPG where possible:
  `{backend, native_id, role_guess_optional, accessor_summary, mount_family}`.
- Optionally: single “merge” script that produces one combined file for diffing
  across regenerations.

### Acceptance criteria

- [x] Checked-in **README or header** in the chosen artifact directory stating
      how to regenerate each backend’s extract (command or module entrypoint).
- [x] At least one **automated extract** committed (PySide6 + Tkinter + Dear PyGui
      `add_*` slice; dump slice when `scratch/dpg/` present).
- [x] **Documented output schema** (field names and meaning) so Phase 1 tables
      do not fork ad hoc columns per author.


## Phase 1 — Inventory and role matrix

### Goal

Produce a **single triage artifact** (spreadsheet or markdown table in
`dev-docs/`) that maps **semantic roles** to the three backends and to
**portable / best-effort / toolkit-only**.

### Work

- From Phase 0 extracts, cluster native entries into **roles**; assign each
  native kind to exactly one role for reconciliation purposes (split roles if
  two behaviors cannot share one unified API).
- For each role, record: representative native ids per backend, primary
  accessor pattern (`AccessorKind`-style), mount involvement if any, and triage
  label.
- Produce the **unified name proposal** column: one Python identifier per role
  that will appear identically on all three adapter classes (or `—` if
  toolkit-only).
- Order roles by **journey priority** (see Principles): shell/mounts → common
  controls → layout containers → long tail.

### Acceptance criteria

- [x] **Role catalog** committed: every row is a role, not an exhaustive per-widget
      list without clustering (`RoleMatrix.md` — initial high-value roles).
- [x] **Three columns** (DPG / Qt / Tk) per role with representative mapping or
      explicit “none / N/A”.
- [x] **Triage column** complete: every role labeled portable, best-effort, or
      toolkit-only; no empty cells.
- [x] **Unified name column** for every portable and best-effort role; toolkit-only
      rows either omitted from unified surface or explicitly listed as excluded
      with rationale.
- [x] Short **glossary** of role names (one line each) appended or linked so
      Phase 2+ authors share vocabulary.

Follow-up: add rows for remaining generated kinds (e.g. Qt Designer interfaces)
only when a unified or explicitly **toolkit-only** decision is needed.


## Phase 2 — Mount contract

### Goal

Freeze **canonical mount keys** and prove each toolkit can host a reference
shell using only `advertise_mount` + `mount` for those keys.

### Work

- Align with `UnifiedMountBasedNativeApi.md`: small versioned key set,
  documented semantics, per-toolkit recommended `target=` patterns.
- Add or extend **one reference layout per toolkit** in `examples/` and/or
  focused tests (may start from PySide6 grid patterns).

### Acceptance criteria

- [ ] **Mount key document** committed (can be a section inside this file or a
      sibling under `dev-docs/`) listing every canonical key, meaning, and
      whether `default=True` applies.
- [ ] **Three runnable references** (DPG, Qt, Tk) or **three test-backed layouts**
      that compile and exercise each key at least once; CI runs the tests that
      apply on available backends (skip policy documented if headless limits
      apply).
- [ ] No reference relies on `backends/common/` for shell composition (may still
      exist elsewhere in repo until Phase 5).


## Phase 3 — Adapter skeleton and first unified operations

### Goal

Introduce the **shared namespace**, **unified abstract base**, and **three
concrete adapter classes** with **identical public method names** for the first
wave of roles (subset of Phase 1 portable + best-effort), plus a **factory**
reading env/CLI for backend selection.

### Work

- Pick package layout (per `UnifiedMountBasedNativeApi.md` open questions);
  implement named stubs or real implementations for wave 1 only.
- Enforce naming: same `__all__` or export list shape across adapters where
  practical; document any intentional asymmetry in signatures in the role matrix
      appendix.
- Tests: per-backend smoke tests that import the adapter and invoke each wave-1
      symbol (generic backend framework acceptable per `AGENTS.md`).
- Lay out tests under **`tests/` subtrees that mirror** the unified package (see
      `UnifiedMountBasedNativeApi.md` § Tests, layout, and `.venv` import hook).
- Prefer **author-facing PyRolyze** in E2E-style tests (`@pyrolyze`, mounts,
      adverts); follow TDD in `pyrolyze/AGENTS.md`.
- Plan or land **automatic PyRolyze import hook** activation for `pytest` when
      using the project `.venv` (document mechanism in `dev-docs/`).

### Acceptance criteria

- [ ] **Three adapter classes** (subclasses of the unified base) exist with
      **matching method names** for wave 1; **factory** resolves backend from
      env/CLI (or documented default).
- [ ] **Test suite** passes for wave 1 on each backend slice the project already
      supports in CI.
- [ ] New unified tests live under **mirrored** `tests/...` paths (not a flat dump
      of unrelated names unless justified).
- [ ] **`dev-docs/`** describes PyRolyze-under-pytest: **current** =
      `load_transformed_namespace` strategy (`UnifiedMountBasedNativeApi.md`);
      **future** = `.venv` hook + checked-in config once implemented; CI/local
      workflow matches whatever is implemented.
- [ ] **Wave 1 list** explicitly enumerated in this doc or a linked checklist
      (checkboxes may live in the triage artifact).


## Phase 4 — App context integration

### Goal

Wire **presentation policy** (theme / density / typography or minimal subset)
through `AppContextKey` + adapters so subtree overrides affect native widgets
reactively, without mount resolution reading context.

### Work

- Declare keys in a single toolkit-agnostic module (per unified API design).
- Implement read paths in adapters on create/update paths only.
- One end-to-end scenario per toolkit demonstrating override + visible effect
      (or test observable equivalent).

### Acceptance criteria

- [ ] **Keys defined** and documented next to intended semantics (token shape or
      enum).
- [ ] **At least one test per backend** (or documented skip) proving a reader
      invalidates or reapplies policy when override changes; consistent with
      hierarchical context rules (mount resolution unchanged).
- [ ] **Doc note** that mount selectors do not consult app context.


## Phase 5 — Cutover: delete `backends/common/`

### Goal

Remove the old shared UI library in one pass; repo uses unified library +
adapters only for portable patterns.

### Work

- Migrate examples, tests, and internal imports off `CoreUiLibrary` /
      `backends/common/`.
- Move any remaining shared non-UI types into agreed locations (`model.py`,
      unified package).
- Delete `src/pyrolyze/backends/common/`.

### Acceptance criteria

- [ ] **No imports** of `pyrolyze.backends.common` (or equivalent path) remain in
      the pyrolyze tree; `grep` or CI check optional but recommended.
- [ ] **Full test suite** green for supported Python versions.
- [ ] **Contributor docs** updated to point at unified + adapters (paths listed in
      changelog-style note in this section when done).


## Phase completion summary

| Phase | Primary artifact | Done when |
| --- | --- | --- |
| 0 | Extract scripts + schema | Regeneration documented; first extract landed |
| 1 | Role triage table | All roles triaged; unified names for portable/best-effort |
| 2 | Mount key doc + 3 references | Keys frozen; each toolkit proves layout |
| 3 | Adapters wave 1 + tests | Matching names; tests green |
| 4 | Context keys + per-backend tests | Policy applied on widget paths only |
| 5 | Removal of `common/` | Tree clean; docs updated |

## Maintenance

When generated backends or DPG dumps are regenerated, re-run Phase 0 extracts
and **diff** against the previous artifact. New native kinds should either map
to an existing role or trigger an explicit new row in the Phase 1 matrix before
they appear in the unified API.
