# py-rolyze reference docs

- **Spec (maintainers):** [Generated UI Library Reference Doc Spec](./Generated_UI_Library_Reference_Doc_Spec.md) — defines layout, content rules, and generator hooks so **user-facing** reference pages stay consistent.
- **Generated output (PySide6, users):** `generated/pyside6/entities.md` + `properties.md` — run from repo root:
  `uv run python py-rolyze/pyrolyze_tools/generate_semantic_library.py PySide6.QtWidgets --output-dir <backends/pyside6> --gen-docs`
  (add `--docs-out <dir>` to override the default `py-rolyze/docs/reference/generated/pyside6`). **No `README.md`** is emitted here; the parent `generated/README.md` is edited manually (e.g. Dear PyGui uses a different tool).

Repo-wide reference material may also live under the workspace root `docs/reference/`; see the spec for how to cross-link without duplicating generated files.
