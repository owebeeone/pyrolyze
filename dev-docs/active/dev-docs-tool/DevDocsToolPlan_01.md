# Dev Docs Tool Plan 01

## Purpose

Define the first implementation plan for the `dev-docs` management tool.

This plan follows the requirements and design already defined for the project
and focuses on the smallest rollout that provides immediate value without
locking the tool into unnecessary complexity.

## Plan Summary

The first implementation should prove three things:

- per-project metadata is sufficient to model structured `dev-docs` projects
- a small CLI can validate and render the new structure reliably
- the same tool can help migrate the existing flat `dev-docs` layout into that
  structure

The implementation should now be assumed to live in the standalone `huggy`
package rather than under `dev-setup/`.

The first rollout should therefore prioritize validation, discovery, index
generation, and migration support over interactive editing or link rewriting.

## Phase 1: Metadata And Discovery Core

### Goal

Build the shared project-loading and validation layer that every subcommand will
depend on.

### Deliverables

- dataclass-backed schema in the Huggy package
- shared JSON serialization helpers
- shared filesystem/path utilities
- project discovery under `dev-docs/active` and `dev-docs/archive`
- `project.json` loader
- validation of required metadata fields
- validation of status consistency with `status/<status>.md`
- validation of canonical document paths
- stable in-memory project model for reuse by CLI commands

### Exit Criteria

- the loader can discover structured projects reliably
- invalid projects produce deterministic, readable errors
- valid projects load into a stable internal representation
- the shared typed model is usable by multiple future commands and tools

## Phase 2: Core Read-Only Commands

### Goal

Add the minimal commands needed to inspect and trust the new structure.

### Deliverables

- thin CLI dispatch layer in Huggy
- `validate`
- `list`
- `show`

### Exit Criteria

- `validate` reports structural and metadata issues clearly
- `list` can summarize projects with basic filtering and sorting
- `show` can render one project's metadata and canonical docs

## Phase 3: Root Index Generation

### Goal

Generate the top-level `dev-docs/README.md` from project metadata so the root
index stops being a hand-maintained file.

### Deliverables

- `render-index`
- deterministic README rendering
- grouping by `active/` and `archive/`
- inclusion of title, slug, status, synopsis, and canonical doc links
- clear `huggy --help` and subcommand help text that explains the tool's role in
  managing structured `dev-docs`

### Exit Criteria

- repeated runs with unchanged metadata produce identical output
- generated output is readable enough to become the normal entry point for
  `dev-docs`
- `huggy --help` is descriptive enough that a human or AI agent can identify the
  intended command surface quickly

## Phase 4: Legacy Migration Support

### Goal

Make the tool useful against the current repo by helping classify and move
unstructured `dev-docs` files.

### Deliverables

- `scan-unstructured`
- editable migration manifest JSON
- `apply-migration`
- migration log written under `.proj-tool/migrations/`
- support for project-relative `target_path` values so migration can preserve or
  introduce useful internal subdirectories such as `plans/`, `design/`,
  `analysis/`, and `data/`

### Exit Criteria

- the tool can detect unmanaged top-level docs
- the manifest can declare both new projects and file classifications
- `apply-migration` can create projects and move files safely
- applied moves are logged for later audit and link-fix work
- migration can place files into nested project-relative paths rather than only
  flattening them into project roots

## Phase 5: Repo Guidance Integration

### Goal

Make the structured `dev-docs` workflow discoverable from repo guidance, not
just from the Huggy package itself.

### Deliverables

- update the relevant `dev-docs` or repository guidance to mention Huggy
- note that Huggy is the intended tool for validation, index generation, and
  migration once the structure is active

### Exit Criteria

- a contributor reading repo guidance can discover Huggy without already knowing
  it exists
- the guidance aligns with the implemented command surface

## Phase 6: Initial Project Migration

### Goal

Use the tool on a small number of real `dev-docs` topics to prove that the
structure is practical.

### Candidate Early Projects

- `dev-docs-tool`
- `uikit-backend`
- `lazy-loading`

### Exit Criteria

- at least a few existing flat docs have been migrated into structured projects
- the generated root index remains readable
- the migration model shows no immediate structural gaps

## Implementation Order

Recommended order:

1. Huggy package skeleton and test harness
2. internal dataclass model, JSON codec, and filesystem helpers
3. project discovery and validation core
4. `validate`
5. `list`
6. `show`
7. `render-index`
8. `scan-unstructured`
9. `apply-migration`
10. add `target_path` support for nested project-relative migration targets
11. first real migrations

This order keeps the tool useful early and ensures migration work happens only
after the structure is inspectable and validated.

## Testing Strategy

The implementation should use focused tests first.

Initial test groups:

- package import and CLI smoke tests
- dataclass and JSON round-trip tests
- project discovery and loading
- metadata validation failures
- status-file consistency checks
- `list` and `show` output behavior
- root README generation
- unstructured file detection
- migration manifest ingestion
- file move and log behavior
- project-relative nested target path behavior

The first tests should use temporary directory fixtures rather than the real
repo tree.

The package layout should also be exercised directly in tests so reusable module
boundaries stay real rather than collapsing back into one large CLI module.

### Golden Migration Harness

Migration behavior should also use fixture-based golden tests.

Recommended structure:

```text
tests/data/migrations/
  case_001_basic/
    src_data/
    manifest.json
    golden/
  case_002_existing_project/
    src_data/
    manifest.json
    golden/
```

Recommended method:

1. copy `src_data/` into a temporary directory
2. run the migration tool against that temporary tree
3. compare the resulting filesystem state against `golden/`

The golden comparison should verify:

- final directory structure
- final file placement
- generated `project.json` content
- generated or updated project `README.md` content where relevant
- migration-log content after normalizing or freezing time-dependent fields
- nested project-relative placements such as `plans/...` or `analysis/...` where
  a migration case requires preserved substructure

This harness should be used for realistic migration scenarios because it keeps
the tests deterministic while still exercising end-to-end filesystem behavior.

### AI-Assisted Structure Discovery

The migration plan should explicitly support an AI review step between raw scan
and applied migration.

Target workflow:

1. Huggy scans an unstructured `dev-docs` tree
2. Huggy emits a rich scan report
3. an AI or human reviews that report and decides whether existing source
   directories should be preserved or flattened
4. the reviewed result becomes the migration manifest
5. Huggy applies the migration manifest and writes a migration log

To support that workflow, the implementation needs these steps:

1. enrich the scan model so it captures more than a flat file list
2. add cluster discovery rules so existing topic directories become visible as
   candidate project groups
3. separate raw scan reports from applyable migration manifests
4. add suggested structure fields such as suggested project slug, suggested doc
   kind, suggested target path, and whether a cluster likely wants preserved
   structure
5. add AI-friendly scan output that gives enough context for review, including
   cluster shape and lightweight file metadata
6. update the migration manifest schema to use project-relative `target_path`
7. update migration application logic to honor nested target paths
8. add golden tests for scan-report output on realistic unstructured trees
9. add end-to-end documentation for the scan → review → apply workflow

The important design point is that Huggy should not try to fully infer final
structure on its own. It should produce a rich enough report that an AI or
human can make a good preserve-vs-flatten decision before migration is applied.

### Concrete Huggy Additions For This Workflow

The AI-assisted workflow needs explicit new Huggy command behavior and explicit
new data structures. The plan should treat these as first-class implementation
work, not as a vague future enhancement.

#### New Or Revised Commands

The plan should include these concrete command changes:

1. revise `scan-unstructured`
   - emit a rich scan report rather than a minimal flat migration manifest
   - include file-level and cluster-level observations plus Huggy suggestions

2. add `render-scan-summary`
   - optional but strongly recommended
   - produce a concise human/AI-readable summary of the scan report
   - useful when raw JSON is too noisy for review

3. revise `apply-migration`
   - consume migration manifests that use project-relative `target_path`
   - preserve nested project structure where specified

4. optionally add `validate-migration`
   - validate a reviewed migration manifest before apply
   - check that all referenced projects, target paths, and doc kinds are legal

The minimum viable command surface for AI-assisted review is:

- `scan-unstructured`
- `apply-migration`

The minimum recommended surface is:

- `scan-unstructured`
- `validate-migration`
- `apply-migration`

#### New Dataclass Structures

The plan should include these concrete schema additions.

1. `ScanReport`
   - top-level scan output
   - contains scan timestamp, root, discovered clusters, and file observations

2. `ScanCluster`
   - represents a discovered loose-file group or source directory cluster
   - includes:
     - source path
     - cluster kind
     - file count
     - extensions present
     - has readme
     - suggested project slug
     - suggested preserve-structure flag
     - optional notes

3. `ScanFileEntry`
   - represents one observed file in the scan report
   - includes:
     - source path
     - source cluster
     - extension
     - basename
     - optional first heading / first non-empty line for text files
     - suggested doc kind
     - suggested target path
     - optional confidence / notes

4. revised `MigrationFileEntry`
   - replace `target_name` with `target_path`
   - treat `target_path` as project-relative

5. optional `MigrationValidationReport`
   - structured errors and warnings for pre-apply validation

These structures are necessary so the AI step can review something richer than
just a list of paths with blank fields.

#### Planned Implementation Sequence For AI-Assisted Workflow

To keep this actionable, the plan should break the work into a concrete order:

1. add `ScanReport`, `ScanCluster`, and `ScanFileEntry` dataclasses
2. update `scan-unstructured` to emit the richer scan report
3. update tests to cover scan-report output with realistic golden fixtures
4. revise migration manifest schema to use `target_path`
5. update `apply-migration` to honor nested target paths
6. add `validate-migration`
7. document the scan → review → validate → apply workflow

## Out Of Scope For This Plan

These ideas should remain deferred until the first tool is working:

- interactive metadata editing
- automatic link rewriting
- graph visualizations
- stale-project reporting
- duplicate-topic clustering
- automatic renaming to canonical doc names during migration unless explicitly
  configured

## Risks

### Risk: Over-structuring Too Early

If the tool requires too much metadata or too many invariants immediately,
adoption will stall.

Mitigation:

- keep `project.json` minimal
- keep the first command set small

### Risk: Package Skeleton Outruns Useful Behavior

Because Huggy is now a reusable standalone package, there is a risk of spending
too much time on package structure before the tool actually validates and
renders real `dev-docs` projects.

Mitigation:

- keep the package layout shallow
- land useful end-to-end commands early
- avoid building extension points before real command logic exists

### Risk: Drift Between `project.json` And Status Files

The design intentionally duplicates status information.

Mitigation:

- treat mismatch as a validation error
- do not add status-editing commands in the first version

### Risk: Migration Creates Broken References

Moving docs will eventually break links if not tracked.

Mitigation:

- record an explicit migration log from the first migration-support release
- defer automatic rewriting until enough history exists to do it safely

## Recommended Next Step

Start implementation in Huggy with the internal dataclass model, JSON codec,
filesystem helpers, and `validate` command, then add the read-only commands
before tackling migration behavior.
