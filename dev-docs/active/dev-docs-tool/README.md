# Dev Docs Tool

## Synopsis

This project defines the structure and management tool for `dev-docs`.

The immediate goal is to move from a largely flat document directory toward a
project-based structure with explicit metadata, generated indexes, and
migration support for existing documents.

## Status

Current status: `in-progress`

## Canonical Docs

- `DevDocsToolRequirements.md`
- `DevDocsToolDesign.md`

## Current Scope

- define a minimal per-project metadata model
- define the first command set for a multi-command CLI
- define how root index generation works
- define how unstructured legacy files are scanned, classified, and migrated

## Notable Future Work

- implement the CLI itself
- generate and maintain the top-level `dev-docs/README.md`
- migrate older flat `dev-docs` files into project folders
- add link-fixup and migration-history support

## Open Questions

- how much project metadata should live in `project.json` versus project
  `README.md`
- whether migration logs should be committed or tool-private
- whether future tooling should rewrite links automatically or only report them
