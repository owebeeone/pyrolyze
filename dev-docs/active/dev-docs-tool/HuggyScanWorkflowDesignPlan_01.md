# Huggy Scan Workflow Design And Plan 01

## Purpose

Define the precise next design and implementation plan for Huggy's
AI-assisted scan, review, and migration workflow.

This document starts from the **current implemented Huggy state**, not from a
blank-slate idealized design.

Current Huggy already has:

- package scaffold
- typed metadata and migration dataclasses
- `validate`
- `list`
- `scan-unstructured`
- `apply-migration`
- migration logs
- migration golden tests

What it does **not** yet have is a sufficiently rich scan report for an AI or
human to make good preserve-vs-flatten structure decisions.

This document defines that missing piece in enough detail to drive
implementation directly.

## Current State

### What `scan-unstructured` Does Today

Today, `scan-unstructured` emits a minimal object shaped roughly like:

```json
{
  "generated_at": "",
  "root": "<dev-docs-root>",
  "projects": [],
  "files": [
    {
      "path": "ApiDesignRules.md",
      "project": "",
      "doc_kind": "",
      "target_name": null
    }
  ]
}
```

This is enough to manually fill in a migration manifest, but it is not a rich
scan report.

### Why The Current Output Is Not Rich Enough

The current output does not tell an AI or human:

- which files appear to belong together as one source cluster
- whether a source directory already looks like a proto-project
- whether a group contains mixed content types
- whether a source cluster already has a `README.md`
- whether files look like plans, requirements, design docs, analysis docs, or
  data artifacts
- whether the source shape suggests preserving structure or flattening it
- where files should land inside the target project

So while the current scan output is technically editable, it pushes too much
interpretive work onto the reviewer with too little structure.

## Desired Workflow

The intended workflow should be:

1. Huggy scans an unstructured `dev-docs` tree.
2. Huggy emits a **rich scan report**.
3. An AI or human reviews that report.
4. The reviewer produces or edits a **migration manifest**.
5. Huggy validates the migration manifest.
6. Huggy applies the migration manifest.
7. Huggy writes a migration log.

The key design principle is:

- **scan report is observational and suggestive**
- **migration manifest is prescriptive**

Those are distinct artifacts and should stay distinct.

## Precise Artifact Definitions

## 1. Rich Scan Report

The rich scan report is the output of `huggy scan-unstructured`.

It is **not** a migration manifest.

It should contain:

- top-level scan metadata
- discovered source clusters
- per-file observations
- Huggy suggestions
- no applied actions

### Top-Level Shape

```json
{
  "generated_at": "2026-03-27T12:00:00Z",
  "root": "pyrolyze/dev-docs",
  "summary": {
    "cluster_count": 12,
    "file_count": 62,
    "top_level_file_count": 37,
    "directory_cluster_count": 5
  },
  "clusters": [...],
  "files": [...]
}
```

### Required Semantics

- `generated_at`
  - scan timestamp in UTC ISO format
- `root`
  - scanned `dev-docs` root
- `summary`
  - lightweight counts so a reviewer can understand report scale quickly
- `clusters`
  - candidate source groupings
- `files`
  - per-file observations with suggested target structure

## 2. Migration Manifest

The migration manifest remains the input to `apply-migration`.

It should describe:

- declared target projects
- target placement for each file

It should not be overloaded with low-level scan observations once the rich scan
report exists.

## 3. Migration Log

The migration log remains the output history artifact written by
`apply-migration`.

It should continue to record:

- source path
- target path
- project
- doc kind
- timestamp
- whether the project was created

## Rich Scan Report: Detailed Schema

## `ScanReport`

Required fields:

- `generated_at: str`
- `root: str`
- `summary: ScanSummary`
- `clusters: list[ScanCluster]`
- `files: list[ScanFileEntry]`

## `ScanSummary`

Required fields:

- `cluster_count: int`
- `file_count: int`
- `top_level_file_count: int`
- `directory_cluster_count: int`

Purpose:

- quick review of report scale
- useful in both machine and human review

## `ScanCluster`

A cluster is Huggy's discovered grouping of source files before migration.

Cluster types:

- `single-file`
- `directory`

Required fields:

- `id: str`
  - stable scan-local identifier such as `cluster:generic_backend_plan`
- `source_path: str`
  - `""` is not allowed
  - top-level file cluster source is the file path
  - directory cluster source is the directory path
- `cluster_type: str`
  - one of `single-file`, `directory`
- `file_count: int`
- `extensions: list[str]`
- `has_readme: bool`
- `contains_mixed_extensions: bool`
- `top_level: bool`
- `suggested_project_slug: str | null`
- `suggested_project_title: str | null`
- `suggested_location: str | null`
  - `active`, `archive`, or `null`
- `suggested_preserve_structure: bool`
- `reasons: list[str]`

### Meaning Of `suggested_preserve_structure`

This field answers:

- should the reviewer start from the assumption that this source cluster wants
  internal project-relative structure preserved?

Examples:

- numbered plan directory: likely `true`
- mixed markdown/json directory: likely `true`
- single top-level markdown file: likely `false`

This is a suggestion, not an action.

### Meaning Of `reasons`

This field explains Huggy's reasoning in plain, structured phrases.

Examples:

- `["directory cluster", "contains numbered plan files"]`
- `["contains README.md", "mixed .md and .json content"]`
- `["single top-level markdown file"]`
- `["source directory named obsolete"]`

This is important for AI review. The AI should not have to rediscover why
Huggy suggested preserving structure.

## `ScanFileEntry`

Each file observation should be precise and reviewable.

Required fields:

- `path: str`
- `cluster_id: str`
- `basename: str`
- `extension: str`
- `relative_parent: str`
  - parent path relative to the scanned root
- `is_text: bool`
- `first_heading: str | null`
- `first_nonempty_line: str | null`
- `size_bytes: int`
- `suggested_project_slug: str | null`
- `suggested_doc_kind: str | null`
- `suggested_target_path: str | null`
- `suggested_canonical: bool`
- `reasons: list[str]`

### Meaning Of `suggested_target_path`

This is Huggy's proposed project-relative destination path.

Examples:

- `README.md`
- `plans/01_Core_Model_And_Builders.md`
- `analysis/RoleMatrix.md`
- `data/surface_analysis.json`

This is the core field that lets an AI propose whether structure should be
preserved or normalized.

### Meaning Of `suggested_canonical`

This tells the reviewer whether Huggy thinks the file likely belongs in
`project.json.canonical_docs`.

Examples:

- project root `README.md`: likely `true`
- `requirements/Requirements.md`: likely `true`
- `data/surface_analysis.json`: likely `false`

## Cluster Discovery Rules

Huggy should not guess project structure from file content alone.
It should discover **clusters** using filesystem shape first.

### Rule 1: Top-Level Loose Files

Any file directly under `dev-docs/` and not inside a reserved structured area is
initially a `single-file` cluster.

### Rule 2: Existing Topic Directories

Any directory directly under `dev-docs/` that is not reserved should be treated
as a `directory` cluster.

Examples from the current repo:

- `generic_backend_plan/`
- `mount_advert_plan/`
- `unified_plan/`
- `widget-reconcile/`
- `obsolete/`

### Rule 3: Reserved Structured Areas

These are not unstructured clusters:

- `active/`
- `archive/`
- `.proj-tool/`

### Rule 4: Nested Files Stay Attached To Their Discovered Cluster

If a cluster is a directory, files under it remain members of that cluster in
the scan report.

The scan report should not flatten them.

## Suggestion Rules

Huggy should make suggestions conservatively.

### Project Suggestion Rules

Examples:

- source directory named `obsolete` -> likely `archive`
- source directory with numbered plan files -> likely one active project
- top-level `*Requirements*` + related `*Design*` docs may still need human/AI
  grouping, so suggested project may be weaker

### Doc Kind Suggestion Rules

Examples:

- `README.md` -> `readme`
- filename contains `Requirements` -> `requirements`
- filename contains `Design`, `Proposal`, `Model` -> `design`
- filename contains `Plan` or starts with ordered prefix `01_`, `02_` -> `plan`
- filename contains `Analysis`, `Report`, `RoleMatrix` -> `analysis`
- `.json` non-metadata artifact -> `data`

### Target Path Suggestion Rules

Examples:

- `README.md` -> `README.md`
- ordered plan docs -> `plans/<basename>`
- requirements docs -> `requirements/<basename>`
- design/proposal/model docs -> `design/<basename>`
- analysis/report docs -> `analysis/<basename>`
- data artifacts -> `data/<basename>`

### Preserve vs Flatten Suggestion Rules

Huggy should set `suggested_preserve_structure = true` when:

- the source is a directory cluster
- files are already grouped meaningfully
- there is mixed content type that benefits from separation
- there are multiple plans or ordered plan documents
- there is likely README collision risk

Huggy should set it to `false` when:

- the cluster is a single loose file
- there is no evidence of meaningful internal structure

## Migration Manifest: Revised Detailed Schema

The migration manifest should remain the applyable artifact.

It should contain:

- declared projects
- classified files

But file entries should now use `target_path`, not `target_name`.

## `MigrationProjectDecl`

Required fields:

- `slug`
- `title`
- `status`
- `location`
- `synopsis`

Optional future fields:

- `canonical_docs`
- `tags`

## `MigrationFileEntry`

Required fields:

- `path`
- `project`
- `doc_kind`

Optional fields:

- `target_path`
- `canonical`
- `notes`

### `target_path` Rules

- interpreted as project-relative path
- may be omitted, in which case basename-in-root default is allowed
- must not escape the project root
- may contain nested directories such as:
  - `plans/...`
  - `design/...`
  - `analysis/...`
  - `data/...`

## Required Huggy Command Changes

## 1. `scan-unstructured`

Current behavior:

- emits a minimal migration-like object

Required new behavior:

- emit `ScanReport`
- include `summary`
- include `clusters`
- include rich file observations
- include Huggy suggestions

This command should remain non-destructive.

### Output Modes

Required:

- JSON to stdout or to a specified file

Optional later:

- Markdown summary rendering

## 2. `apply-migration`

Current behavior:

- consumes the current minimal migration manifest
- can move files and create projects

Required new behavior:

- consume revised manifest with `target_path`
- create nested directories as needed
- preserve project-relative structure where specified
- validate that `target_path` stays inside the project

## 3. `validate-migration`

This should be added.

Purpose:

- validate a reviewed migration manifest before apply

Checks:

- all referenced projects exist in the manifest or target tree
- all statuses and locations are valid
- all target paths are valid and project-relative
- no duplicate file destinations
- no escaping target paths

## 4. `render-scan-summary`

Optional but recommended.

Purpose:

- render a concise human/AI-friendly summary of a rich scan report

This is especially useful when the JSON report is too large to inspect directly.

## Detailed Implementation Plan

## Phase A: Rich Scan Dataclasses

Add new dataclasses:

- `ScanSummary`
- `ScanCluster`
- `ScanFileEntry`
- `ScanReport`

Exit criteria:

- types exist
- round-trip JSON tests exist

## Phase B: Cluster Discovery Engine

Implement:

- directory cluster detection
- loose-file cluster detection
- reserved-directory exclusion

Exit criteria:

- scan can identify clusters in realistic fixture trees

## Phase C: Suggestion Engine

Implement:

- doc kind suggestions
- target path suggestions
- project slug/title suggestions
- preserve/flatten suggestions
- human-readable reason generation

Exit criteria:

- scan report includes deterministic suggestions and reasons

## Phase D: `scan-unstructured` Rewrite

Replace the current minimal output with `ScanReport`.

Exit criteria:

- command emits rich report
- existing migration path is not silently broken without documentation

## Phase E: Migration Manifest Revision

Revise manifest support to use:

- `target_path`
- optional canonical flag

Exit criteria:

- manifest schema is updated in code and docs
- old `target_name` path is removed or intentionally compatibility-wrapped

## Phase F: `apply-migration` Nested Path Support

Implement:

- nested `target_path`
- parent directory creation
- path safety checks

Exit criteria:

- nested target path goldens pass

## Phase G: `validate-migration`

Add the new command and validation report structure.

Exit criteria:

- invalid manifests fail before mutation
- duplicate target path scenarios are detected

## Phase H: Rich Scan Goldens

Add scan-report golden fixtures for:

- top-level loose file collections
- directory clusters with numbered plans
- mixed markdown/json clusters
- archive-like clusters
- non-markdown files

Exit criteria:

- golden tests verify the structure and suggestions in the rich scan report

## Phase I: Workflow Documentation

Document the full workflow:

1. scan
2. AI/human review
3. validate migration
4. apply migration
5. inspect log

Exit criteria:

- repo guidance can point contributors to this workflow directly

## Testing Requirements

The current migration goldens are a strong starting point, but this new work
needs additional test categories.

## Test Revision Plan

The new workflow should not merely add tests. It must also revise the current
Huggy test structure so the existing tests still make sense after
`scan-unstructured` stops emitting the current minimal migration-like object.

The current test baseline includes:

- package smoke tests
- CLI tests
- dataclass round-trip tests
- migration unit/integration tests
- migration golden tests

The scan/report redesign affects those tests directly.

### 1. Revise Existing `scan-unstructured` Expectations

Current scan tests effectively assume:

- no cluster model
- no rich scan metadata
- output shape close to a migration manifest

These tests must be rewritten to assert the new `ScanReport` shape instead.

Required changes:

- stop asserting only `root`, `projects`, and `files`
- add assertions for:
  - `summary`
  - `clusters`
  - file-level suggestion fields
  - preserve/flatten suggestions
  - human-readable `reasons`

### 2. Keep Existing Migration Goldens, But Reclassify Their Role

The current migration goldens remain valuable, but after the redesign they
should be understood as testing:

- reviewed/applyable migration manifests
- migration application correctness
- migration logging correctness

They do **not** test rich scan-report quality.

Plan action:

- retain current migration goldens
- continue extending them for nested `target_path` behavior
- do not overload them to prove scan-report semantics

### 3. Add A New Golden Test Layer For Rich Scan Reports

A separate golden layer should be added for scan reports.

Recommended fixture layout:

```text
tests/data/scan_reports/
  case_001_loose_files/
    src_data/
    golden_report.json
  case_002_directory_cluster/
    src_data/
    golden_report.json
  case_003_mixed_content/
    src_data/
    golden_report.json
```

These tests should:

1. copy `src_data` into a temporary directory
2. run `scan-unstructured`
3. normalize volatile fields if needed
4. compare the emitted report against `golden_report.json`

These tests are necessary because scan quality is now a first-class concern.

### 4. Add A New Review-Step Test Layer

The workflow now has an important conceptual boundary:

- scan report
- reviewed migration manifest

Tests should make that boundary explicit.

Recommended additions:

- fixture cases where a rich scan report exists
- an expected reviewed migration manifest for the same source tree
- tests that verify the manifest is valid for apply

This does not require automating the AI step. It requires the test harness to
treat reviewed manifests as a distinct artifact type.

### 5. Add `validate-migration` Tests

Once `validate-migration` exists, add tests for:

- invalid project references
- invalid `target_path`
- duplicate target destinations
- illegal escaping paths
- invalid status/location/doc-kind values

These tests should exist before `validate-migration` is considered complete.

### 6. Revise CLI Tests

Current CLI tests only cover:

- `--help`
- `version`
- basic `validate`

The redesign requires new CLI tests for:

- `scan-unstructured` rich report output
- `validate-migration`
- `apply-migration` with nested target paths
- subcommand help for the richer workflow

If `render-scan-summary` is added, it also needs dedicated CLI tests.

### 7. Revise Dataclass Tests

Current dataclass tests are minimal.

The redesign should add explicit round-trip and validation-oriented tests for:

- `ScanSummary`
- `ScanCluster`
- `ScanFileEntry`
- `ScanReport`
- revised `MigrationFileEntry` with `target_path`

### 8. Add Path-Safety Tests

Because nested target paths are becoming first-class, tests must explicitly
cover:

- valid nested project-relative paths
- path normalization
- rejection of escaping paths such as `../outside.md`
- behavior when parent directories need to be created

### 9. Preserve Current Working Coverage While Refactoring

As the scan/report model changes, the implementation should not delete the
current migration tests and only add replacements later.

Required process:

- introduce new scan-report tests first
- then change implementation
- then revise affected old tests
- keep migration goldens green throughout

This preserves the red/green/refactor discipline and avoids losing protection
for already-working migration behavior.

### Unit Tests

- dataclass round-trip tests for new scan-report structures
- suggestion-rule tests
- target-path validation tests

### Golden Scan Tests

Fixture trees that verify:

- cluster detection
- file observation enrichment
- suggested project slugs
- suggested target paths
- preserve/flatten signals
- reason strings

### Golden Migration Tests

Extend current goldens so some reviewed manifests use nested target paths such
as:

- `plans/...`
- `analysis/...`
- `data/...`

## Explicit Non-Goals

This design does **not** require:

- fully automatic final structure inference
- AI making unreviewed destructive changes
- Huggy choosing perfect project taxonomy without human or AI review

Huggy's role is:

- structured observation
- conservative suggestion
- safe application

not autonomous document architecture.

## Recommended Next Step

Implement **Phase A through Phase D** first:

- new rich scan-report dataclasses
- cluster discovery
- suggestion engine
- rewritten `scan-unstructured`

That is the smallest slice that unlocks the AI-assisted workflow in a precise,
reviewable way.
