# Dev Docs Tool Requirements

## Purpose

Define the minimum useful requirements for a tool that manages the `dev-docs`
directory as a structured set of projects rather than a flat pile of unrelated
files.

This document defines what the tool must do first. It does not attempt to cover
every future automation idea.

## Problem Statement

`dev-docs` currently contains too many top-level files and too many unrelated
topics in one namespace.

This causes several problems:

- discovery is slow
- status is implicit or absent
- canonical documents are hard to identify
- abandoned and active work are mixed together
- there is no structured migration path from flat docs to project folders

The tool should make a project-based structure practical to adopt and maintain.

## Goals

- Support a per-project directory structure under `dev-docs`.
- Use small per-project metadata files as the authoritative structured source.
- Validate project structure and metadata.
- Generate a top-level index from project metadata.
- Detect legacy/unstructured files that are not yet part of the new layout.
- Emit a machine-editable migration manifest for those files.
- Apply that manifest to create projects and move files into place.
- Record what moves occurred so future link repair and audit work is possible.
- Establish the tool as a greenfield Python package with a normal PyPI-compatible
  project structure so other repo tooling can depend on it later.

## Non-Goals

- This first version does not need interactive editing.
- This first version does not need automatic broken-link rewriting.
- This first version does not need rich search or graph visualization.
- This first version does not need a full project lifecycle workflow.
- This first version does not need to migrate every existing `dev-docs` file
  automatically without review.
- This first version does not need to live under the existing `dev-setup`
  directory if that would make future reuse harder.

## Packaging Requirements

The tool should be treated as a greenfield Python project rather than a
one-off script.

Required packaging properties:

- a normal PyPI-compatible project layout
- its own `pyproject.toml`
- source under `src/`
- tests under `tests/`
- an installable CLI entry point
- minimal direct dependencies beyond what is justified by the schema and CLI

The intent is that future tools can import and reuse the same project-discovery,
validation, and metadata-loading logic instead of copying it.

The requirements do not force the exact package location yet, but they do rule
out designing it as a throwaway script coupled tightly to `dev-setup`.

## Required Structure

The tool must support this basic shape:

```text
dev-docs/
  active/
    <project-slug>/
      project.json
      README.md
      status/
        <one-status-file>.md
      ...
  archive/
    <project-slug>/
      project.json
      README.md
      status/
        <one-status-file>.md
      ...
```

The tool does not need to require that all existing docs are already in this
shape. It does need to support moving toward it.

## Project Metadata Requirements

Each project must support a `project.json` file with, at minimum:

- `slug`
- `title`
- `status`
- `synopsis`
- `canonical_docs`

The tool should also support these optional fields immediately because they are
high-value and easy to validate:

- `tags`
- `replaced_by`
- `supersedes`
- `updated`

The tool's Python implementation should also define explicit dataclass-backed
schema models for these JSON structures so that metadata shape is not carried as
untyped dictionaries throughout the codebase.

## Status Requirements

The tool must support a fixed status vocabulary for projects:

- `memo`
- `investigation`
- `in-progress`
- `completed`
- `abandoned`

The tool must validate that:

- `project.json.status` is one of the allowed values
- the `status/` directory exists
- the `status/` directory contains exactly one status file
- the status filename matches the project status

The first version does not need to manage status transitions automatically. It
does need to report mismatches.

## Command Requirements

The first version must support these commands:

### `validate`

Validate all structured projects under `dev-docs`.

It must check:

- required files exist
- required metadata fields exist
- status values are legal
- canonical docs exist
- project slugs are unique
- files referenced in metadata are local to the project

### `list`

List structured projects.

The first version should support:

- listing all projects
- filtering by active/archive location
- filtering by status
- basic sorting by title or slug

### `show`

Show the metadata and canonical docs for one project by slug.

### CLI Help Requirements

The Huggy CLI must provide clear top-level and subcommand help text.

Required properties:

- `huggy --help` must clearly describe that Huggy manages structured `dev-docs`
  projects, validates project metadata, generates indexes, and supports
  migration from unstructured layouts
- subcommand help text must be specific enough that a human or AI agent can
  determine the correct command to use without reading the source
- help output should describe the command's purpose, not just its arguments

### `render-index`

Generate the top-level `dev-docs/README.md` from structured project metadata.

The generated index should include, at minimum:

- active projects
- archived projects
- title
- slug
- status
- synopsis
- links to project folders and canonical docs

## Migration Requirements

The first version must support migration of currently unstructured files.

### `scan-unstructured`

This command must:

- identify files in `dev-docs` that are not already inside structured project
  folders
- ignore known tool-private directories
- emit a machine-editable JSON manifest

The manifest should contain:

- project declarations
- file classifications

The manifest should not try to encode imperative actions when classification is
sufficient.

### `apply-migration`

This command must:

- read the edited migration manifest
- create missing projects declared in the manifest
- move classified files into their target projects
- preserve filenames unless an explicit target name is supplied
- update or create `project.json` and stub `README.md` where needed

## Migration Logging Requirements

The tool must emit an applied migration log separate from the editable
migration manifest.

The migration log must record, at minimum:

- source path
- target path
- target project
- classified doc kind
- timestamp

This is required so that future tooling can detect moves and potentially repair
references.

## Extensibility Requirements

The CLI must be implemented as a multi-command tool from the beginning.

Required design constraints:

- subcommand-based structure
- commands can be added later without redesigning the CLI
- project metadata loading and validation logic is reusable across commands
- reusable logic can also be imported by future tools without shelling out to
  the CLI

The first version does not need plugin support or external configuration.

## Data Ownership Requirements

The authoritative structured source should be:

- `project.json` for project metadata
- project-local files for human narrative docs
- migration logs for applied move history

The generated root `dev-docs/README.md` should not be treated as the authority.
It should be renderable from project metadata.

## Repo Guidance Requirements

The `dev-docs` guidance for the main repository should eventually mention Huggy
explicitly once the structure is adopted.

At minimum, future repo guidance should direct contributors toward:

- using Huggy to validate structured `dev-docs` projects
- using Huggy to generate the root `dev-docs/README.md`
- using Huggy migration support when moving flat docs into project folders

## Testing And TDD Requirements

The tool must be built with normal project-local automated tests.

Required testing properties:

- a dedicated test suite under `tests/`
- focused tests for parsing, validation, rendering, and migration behavior
- command-level tests for the CLI entry point
- temporary-directory based tests rather than relying on the live repo tree

Required process:

- follow the repo's strict red/green/refactor workflow
- add or update tests first for each behavior change
- run the smallest relevant test target while iterating
- preserve the ability to run a broader regression target before finalizing

The first implementation should not skip test infrastructure on the assumption
that the tool is small. The structure-management and migration behavior is
precisely the sort of logic that benefits from early automated coverage.

## Future Requirements Explicitly Deferred

These are important but out of scope for the first version:

- automatic link rewriting
- duplicate-topic detection
- stale project reporting
- graph rendering of `supersedes` and `replaced_by`
- interactive project creation flows
- editing `project.json` in place from the CLI
- integration with a wider documentation site generator
- packaging/publishing concerns beyond a normal reusable Python project layout
