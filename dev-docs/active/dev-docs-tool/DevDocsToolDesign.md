# Dev Docs Tool Design

## Purpose

Describe the first implementation design for the `dev-docs` management tool and
explicitly separate the near-term design from future ideas that should not be
built yet.

## Design Summary

The first version should be a small Python CLI using `argparse` with a
subcommand structure and a minimal per-project JSON metadata model.

The tool should treat:

- `project.json` as the structured source of truth for project metadata
- project `README.md` files as human narrative
- top-level `dev-docs/README.md` as generated output
- migration logs as operational history

This design intentionally chooses per-project metadata over one large central
registry file.

Serialization direction for the first implementation:

- Python `@dataclass` models define the schema
- JSON is the on-disk format
- `dataclasses_json` handles JSON read/write conversion
- validation still happens in tool logic after parsing

## Why Per-Project JSON

Per-project `project.json` has several advantages:

- metadata lives with the project it describes
- moving a project between `active/` and `archive/` is straightforward
- merge conflicts are smaller than with one central registry
- the tool can discover projects by filesystem traversal
- the model scales naturally as projects multiply

This is a better fit than:

- pure filesystem sentinels with no structured metadata
- a single global JSON file containing all projects

Pure filesystem conventions are attractive for status, but they are not enough
once the tool needs synopsis, canonical docs, replacement links, and migration
metadata.

## Directory Model

The first version should target this model:

```text
dev-docs/
  README.md
  active/
    <project-slug>/
      project.json
      README.md
      status/
        <status>.md
      ...
  archive/
    <project-slug>/
      project.json
      README.md
      status/
        <status>.md
      ...
  .proj-tool/
    migrations/
      ...
```

The `.proj-tool/` area is reserved for tool-owned operational artifacts such as
migration logs. It should not be treated as user-authored documentation.

## Metadata Model

### `project.json`

Initial schema:

```json
{
  "slug": "dev-docs-tool",
  "title": "Dev Docs Tool",
  "status": "in-progress",
  "synopsis": "Short project summary.",
  "canonical_docs": ["README.md", "DevDocsToolRequirements.md"],
  "tags": ["docs", "tooling"],
  "replaced_by": [],
  "supersedes": [],
  "updated": "2026-03-27"
}
```

Design notes:

- `canonical_docs` are project-relative paths
- `status` is duplicated in both `project.json` and `status/<status>.md`
- the duplication is acceptable because it improves browseability, and the tool
  can validate consistency

## Dataclass Schema

The first implementation should make the Python dataclasses explicit rather than
letting ad hoc dictionaries spread through the tool.

Recommended initial schema:

```python
@dataclass
class ProjectMetadata:
    slug: str
    title: str
    status: str
    synopsis: str
    canonical_docs: list[str]
    tags: list[str] = field(default_factory=list)
    replaced_by: list[str] = field(default_factory=list)
    supersedes: list[str] = field(default_factory=list)
    updated: str | None = None
```

```python
@dataclass
class MigrationProjectDecl:
    slug: str
    title: str
    status: str
    location: str
    synopsis: str
```

```python
@dataclass
class MigrationFileEntry:
    path: str
    project: str
    doc_kind: str
    target_path: str | None = None
```

```python
@dataclass
class MigrationManifest:
    generated_at: str
    root: str
    projects: list[MigrationProjectDecl] = field(default_factory=list)
    files: list[MigrationFileEntry] = field(default_factory=list)
```

```python
@dataclass
class MigrationLogEntry:
    source_path: str
    target_path: str
    project: str
    doc_kind: str
    project_created: bool = False
```

```python
@dataclass
class MigrationLog:
    applied_at: str
    root: str
    entries: list[MigrationLogEntry] = field(default_factory=list)
```

There should also be internal non-serialized dataclasses for discovered project
state, such as:

- filesystem location (`active` or `archive`)
- project directory path
- status marker path
- loaded `ProjectMetadata`

Those internal structures should not be written directly to JSON.

### Why Dataclasses First

Using dataclasses makes the schema:

- explicit in code
- easy to test
- easy to validate after deserialization
- stable across CLI commands

This is preferable to passing around untyped dictionaries, especially once the
tool starts handling migration manifests and logs in addition to `project.json`.

### Why JSON Plus `dataclasses_json`

JSON remains the preferred storage format because:

- the files are small and record-shaped
- manual edits are straightforward
- diffs are relatively compact
- merge resolution should be easier than with XML for this schema

`dataclasses_json` is acceptable here because it removes repetitive
serialization boilerplate without changing the underlying data model.

The tool should still:

- validate enum-like fields such as `status`, `location`, and `doc_kind`
- reject malformed or incomplete inputs clearly
- use deterministic JSON formatting when writing files

## Project-Internal Structure

The design should explicitly allow projects to contain meaningful internal
subdirectories rather than assuming that every migrated document lands in the
project root.

This matters because some projects naturally accumulate multiple plans, design
notes, analysis documents, or data artifacts. Flattening all of those into the
project root would recreate the same clutter Huggy is meant to reduce.

### Recommended Internal Convention

Huggy should support, but not require, project-relative directories such as:

```text
<project>/
  README.md
  project.json
  status/
    <status>.md
  plans/
  design/
  requirements/
  investigation/
  analysis/
  data/
  archive/
```

These should be treated as conventions, not mandatory fixed folders. The
important point is that nested project-relative targets are valid and normal.

### Migration Target Paths

Migration should use project-relative target paths rather than root-only target
filenames.

Preferred shape:

```json
{
  "path": "generic_backend_plan/01_Core_Model_And_Builders.md",
  "project": "generic-backend",
  "doc_kind": "plan",
  "target_path": "plans/01_Core_Model_And_Builders.md"
}
```

Why:

- allows grouped plan/design/data folders
- avoids collisions such as multiple source `README.md` files
- preserves meaningful structure from legacy topic directories
- keeps migration declarative without introducing an imperative action model

If `target_path` is omitted, Huggy may still default to placing the file in the
project root using the source basename.

If `target_path` is present, Huggy should:

- treat it as project-relative
- create any missing parent directories inside the project
- reject paths that escape the project root

### Canonical Docs And Subdirectories

`project.json.canonical_docs` should continue to support project-relative paths,
including nested ones such as:

- `README.md`
- `requirements/Requirements.md`
- `design/Design.md`
- `plans/Plan_01.md`

This is necessary so project metadata can accurately describe projects whose
important documents are intentionally grouped under subdirectories.

## Command Design

The first version should expose a single multi-command executable. The exact
name can be chosen later; the command shape should be stable from the start.

Recommended initial command set:

- `validate`
- `list`
- `show`
- `render-index`
- `scan-unstructured`
- `apply-migration`

## Proposed Package Layout

The first implementation should be a normal Python package with a shallow,
domain-oriented module structure.

Recommended `src/huggy` layout:

```text
src/huggy/
  __init__.py
  cli.py
  constants.py
  errors.py
  model.py
  io/
    __init__.py
    json_codec.py
    filesystem.py
  projects/
    __init__.py
    discover.py
    validate.py
    render_index.py
  migration/
    __init__.py
    scan.py
    apply.py
    log.py
```

### Module Responsibilities

#### `cli.py`

This module should contain:

- `argparse` setup
- subcommand registration
- dispatch into implementation modules

It should not accumulate business logic.

#### `model.py`

This module should define the dataclass-backed schema for:

- project metadata
- migration manifest
- migration log
- internal discovered-project state as needed

This module is the typed core of the tool's data model.

#### `constants.py`

This module should define:

- allowed statuses
- allowed document kinds
- reserved directory names
- any other small fixed enumerations

#### `errors.py`

This module should define custom exceptions for:

- validation failures
- malformed metadata
- migration application errors

#### `io/json_codec.py`

This module should own:

- `dataclasses_json` integration
- JSON load/save helpers
- deterministic formatting behavior

#### `io/filesystem.py`

This module should own:

- path helpers
- project-root path resolution
- safe file writes
- small reusable filesystem utilities

#### `projects/discover.py`

This module should:

- find projects under `active/` and `archive/`
- load `project.json`
- build internal discovered-project models

#### `projects/validate.py`

This module should:

- validate structured project directories
- validate metadata fields and status markers
- validate canonical docs and project-local references

#### `projects/render_index.py`

This module should:

- render the top-level `dev-docs/README.md`
- consume validated project metadata
- produce deterministic output

#### `migration/scan.py`

This module should:

- find unmanaged files
- emit editable migration manifests

#### `migration/apply.py`

This module should:

- read migration manifests
- create projects if needed
- move files into place
- update project metadata and stub files where required

#### `migration/log.py`

This module should:

- write migration logs
- read migration logs for future tooling

### Why This Layout

This structure is preferred over a generic `tools/` package because it keeps the
code organized by domain behavior:

- shared typed model
- project operations
- migration operations
- serialization and filesystem helpers

It also keeps the CLI thin and makes it easier for future tools to reuse the
same discovery, validation, and metadata-loading logic directly as Python code.

### `validate`

Responsibilities:

- discover all structured projects
- load and validate `project.json`
- validate the project directory contract
- report errors in a readable format

This command should be the shared validation base for other commands.

### `list`

Responsibilities:

- print a compact project summary
- support filtering by location and status
- support lightweight sorting

This command should operate only on validated project metadata.

### `show`

Responsibilities:

- display one project's metadata
- show canonical docs
- show its path and whether it lives in `active/` or `archive/`

### `render-index`

Responsibilities:

- render `dev-docs/README.md`
- group projects by `active/` and `archive/`
- surface status and synopsis prominently
- link to project folders and canonical docs

The file should be generated deterministically.

### `scan-unstructured`

Responsibilities:

- find files not already inside a structured project
- ignore tool-private paths
- emit a JSON classification manifest for manual editing

This command is intentionally conservative. It should not guess too much.

### `apply-migration`

Responsibilities:

- read the edited classification manifest
- create declared projects if absent
- move files into projects
- write a migration log

This command should avoid clever automatic renaming unless explicitly requested
in the manifest.

## Migration Manifest Design

The editable manifest should describe classification, not imperative actions.

Recommended shape:

```json
{
  "generated_at": "2026-03-27",
  "root": "pyrolyze/dev-docs",
  "projects": [
    {
      "slug": "uikit-backend",
      "title": "UIKit Backend",
      "status": "investigation",
      "location": "active",
      "synopsis": "Investigate UIKit support for PyRolyze."
    }
  ],
  "files": [
    {
      "path": "pyrolyze/dev-docs/UIKitPyrolizeFeasibility.md",
      "project": "uikit-backend",
      "doc_kind": "investigation"
    }
  ]
}
```

Why this shape:

- less duplication than action-based plans
- easier to edit
- easier to validate
- the tool can derive create-vs-attach behavior from the declared projects

The manifest should deserialize into the dataclass schema above rather than
being manipulated as raw dictionaries.

## Migration Log Design

The applied migration log should be distinct from the editable manifest.

Recommended location:

```text
dev-docs/.proj-tool/migrations/<timestamp>.json
```

Recommended contents:

- source path
- target path
- project slug
- doc kind
- timestamp
- whether the project was newly created

This log exists to support:

- auditability
- future reference repair
- later tooling that answers "where did this file go?"

The migration log should also use the dataclass schema above so that the tool
has one consistent typed model for both editable and generated JSON.

## Generated Root README Design

The top-level `dev-docs/README.md` should be generated from `project.json`
files.

It should contain:

- a short generated notice
- active project summary table
- archived project summary table
- links to project directories
- links to canonical docs

The generator should not attempt to summarize rich project README prose. The
index should be driven from structured metadata only.

## Validation Design

Validation should be centralized in one internal module so every command uses
the same project-loading and error-reporting rules.

At minimum, validation should cover:

- required metadata fields
- legal status values
- duplicate slugs
- missing canonical docs
- mismatch between `project.json.status` and `status/<status>.md`
- project files referenced outside the project directory

The first version should fail clearly rather than trying to repair mismatches.

## What We Are Not Doing Yet

The following ideas are intentionally deferred, even though they may be useful
later.

### 1. Interactive Editing

The first version should not become a metadata editor. It should read, validate,
render, and apply explicit migration manifests.

### 2. Automatic Link Rewriting

This is a real future need, but it is not a starter feature. The migration log
is enough to prepare for it.

### 3. Rich Graph Or Timeline Views

Relationships such as `replaced_by` and `supersedes` are worth keeping in the
metadata, but graph rendering and lifecycle timelines should wait.

### 4. Rich Search

The first version does not need semantic search or cross-project similarity
detection.

### 5. Full Legacy Migration

The tool should help migration, not silently reorganize the entire existing
`dev-docs` tree in one unsafe pass.

### 6. Eliminating Status Files

It would be possible to rely on `project.json` status only. The first design
keeps a readable `status/` marker because it is useful for humans browsing the
filesystem directly.

### 7. XML Serialization

XML was considered because explicit named closing tags can sometimes improve
boundary readability during manual conflict resolution.

It is intentionally not selected for the first version because:

- the metadata is small and shallow
- the data is record-oriented rather than document-oriented
- JSON should remain easier to diff and manually inspect overall
- the schema benefits more from typed dataclasses and validation than from XML
  markup

## Future Directions

These are candidates for later work once the basic structure and tool are real.

- `init-project` command
- `set-status` command
- `archive-project` and `restore-project`
- `find-moved` and `rewrite-links`
- stale project reports
- orphaned document reports
- root README templating with optional hand-written preamble
- graph output for project relationships
- optional TOML or YAML metadata if JSON becomes too limiting

## Recommended Next Step

After agreeing on this design, implement the first CLI with:

- a shared project discovery/validation layer
- `validate`
- `list`
- `show`
- `render-index`
- `scan-unstructured`
- `apply-migration`

That is enough to prove the model before broader reorganization begins.
