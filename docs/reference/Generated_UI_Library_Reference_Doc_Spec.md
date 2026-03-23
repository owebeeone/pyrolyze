# Spec: Generated UI Library Reference Documentation

## Purpose

Define **machine-generated, human-readable reference Markdown** for each **generated UI library** (e.g. `PySide6UiLibrary` emitters such as `CQPushButton`, `CQMainWindow`). The docs are a **compressed API reference** for **PyRolyze authors**: what you pass at the call site, how each field maps onto the native toolkit’s **setters**, **properties**, or **constructor**, and how **`mount(...)`** selectors map onto parent **attach APIs** (e.g. `setMenuBar`, `setCentralWidget`).

**Primary audience:** **users** who already read Qt/Tk/Dear PyGui docs and need a **straight mapping** from “native API name” → “PyRolyze field / mount hook.” This is not a tutorial; high-level authoring patterns may still live in repo-level docs (e.g. `docs/user/PyRolyze_Authoring_Guide.md`), but **this generated reference is user-facing**, not an internal contributor-only note.

**Update model (read this):** PyRolyze applies **one-way deltas** into the toolkit. The runtime reconciler issues updates; there is **no meaningful read-back** of widget state through PyRolyze for driving logic—the tables document **what PyRolyze will call or set**, not a bidirectional binding. Do not assume “if I change the widget elsewhere, PyRolyze reflects it”; treat the doc as the **outbound** contract only.

**Tone:** follow `docs/Python Library Documentation Tone Guide - Short.md` → **`reference`**: matter-of-fact, scannable tables, minimal prose.

---

## Scope

| In scope | Out of scope |
|----------|----------------|
| Emitters (`CQ*` / library-specific public component functions) derived from `UiWidgetSpec` | Tutorial walkthroughs, design rationale |
| Constructor kwargs, updatable props, methods, events | Hand-written per-widget narrative |
| `MountPointSpec` → Qt/Tk/DPG attach behavior | Runtime reconciler algorithms |
| Cross-links and stable anchor IDs | Pretty screenshots or diagrams (unless added later) |
| Native API → PyRolyze field/mount mapping | How to build custom widgets or extend the generator |
| Curated **unmapped** native property/type lists (e.g. `hidden`) | Full toolkit API dumps without curation |

Backends in scope: **at minimum PySide6**; same schema should generalize to **Tkinter** and **Dear PyGui** when their generated libraries exist.

---

## Where files live (`py-rolyze/docs`)

All generated reference output for the **py-rolyze package** lives under:

```text
py-rolyze/docs/reference/generated/
├── README.md                          # What these two files are + how to regenerate + tone link
└── <backend-id>/                      # e.g. pyside6, tkinter, dearpygui
    ├── entities.md                    # All emitters (CQ*): one section per entity, links → properties.md
    └── properties.md                  # All mapped fields + mount params + unmapped native names
```

**Naming rules**

- `<backend-id>`: lowercase, matches the generated module or engine family (e.g. `pyside6` for `PySide6UiLibrary`).
- **Only two content files per backend** (`entities.md`, `properties.md`) to keep the reference small; no per-emitter files.
- **Stable anchors:** kebab-case slugs — entity headings `#entity-<emitter-slug>` (e.g. `#entity-cqpushbutton`), property glossary `#prop-<slug>` (e.g. `#prop-object-name`), mount rows may use `#mount-<emitter-slug>-<mount-name>` on the **entities** page or a dedicated subsection in **properties** (pick one convention and keep it stable); see below.

**Repo root `docs/`**

- Add a **short pointer** only (optional but recommended): e.g. `docs/reference/README.md` or a line in `docs/README.md` linking to `py-rolyze/docs/reference/generated/README.md`.
- Avoid duplicating generated content at repo root unless CI copies artifacts for publishing; single source of truth stays under `py-rolyze/docs/reference/generated/`.

---

## Document set and cross-linking

### 1. `README.md` (top-level under `generated/`)

- One paragraph: what this reference is **for authors** (native API ↔ PyRolyze kwargs/mounts) and the **one-way delta** expectation.
- Links to `<backend-id>/entities.md` and `<backend-id>/properties.md`.
- Command(s) to regenerate (see **Generator integration**) — mainly for maintainers; users consume the committed Markdown.
- Link to `docs/Python Library Documentation Tone Guide - Short.md` (reference tone).

### 2. `<backend-id>/properties.md` — all **mapped** names + **unmapped** native surface

**A. Mapped properties and parameters (author-facing)**

- **Single flat sorted list** at the top (TOC): every distinct identifier used anywhere in the library:
  - `constructor_params` keys  
  - `props` keys  
  - `methods` keys  
  - `events` keys  
  - `mount_points` param names (`MountParamSpec.name`)  
- Each TOC entry links to anchor **`#prop-<slug>`** on this file.
- Under each anchor, a **short block**:
  - **Native mapping:** setter / property / constructor / signal (as in spec tables).
  - **Used by entities:** bullet list of links to `entities.md#entity-<emitter-slug>`.

Optional: one combined table for scanability (Field | Mode | Setter/accessor | Entities) if it stays generated and sorted deterministically—TOC + anchors remain mandatory.

**B. Unmapped native properties (and similar)**

- Section **`## Unmapped native properties`** (or toolkit-specific title, e.g. “Qt properties not exposed”).
- **Sorted flat list** of native names authors might look for in toolkit docs that **do not** appear as PyRolyze kwargs/events/methods for **any** emitter in this backend—e.g. `hidden` if only `visible` is mapped, or stylesheet-only knobs with no generated field.
- Each line: **native name** — one short note (**why** / **use instead** / **not applicable**) when the generator or maintainer can supply it; otherwise `—`.
- **Source of truth for the list:** generator config (curated denylist / allowlist diff), optional introspection minus mapped set in a later revision—document which approach the pipeline uses in `README.md`.

**C. Unmapped native widget / item kinds (optional but recommended)**

- Same file or end of `entities.md`: if maintained, a short **`## Unmapped native types`** listing toolkit classes that exist natively but have **no** corresponding `CQ*` (or equivalent) emitter—helps users stop searching for a missing wrapper.

### 3. `<backend-id>/entities.md` — all emitters in one file

**Top: entity index**

- **Sorted table:** Emitter (link `#entity-<slug>`) | Kind | Mounted type | Child policy (optional).

**Per entity: `## <EmitterName>`** with stable anchor `#entity-<emitter-slug>`**

1. Subline: `kind: …` → `mounted_type_name: …`

2. **`### Props and constructor fields → application`**  
   Compressed table; **Field** column values are **links** to `properties.md#prop-<slug>` where a glossary entry exists.

   | Field | Mode | Setter / accessor | Notes |
   |-------|------|---------------------|--------|

   Same row rules as before (`UiPropSpec` / `UiParamSpec`, `PropMode`, `setter_kind` + `setter_name`, events as extra column or type column).

3. **`### Methods`** (if any) — table; link method **names** to `properties.md` anchors if listed there.

4. **`### Mount points`** — table (`apply_method_name`, `append_method_name`, …); mount **param** names link to `properties.md#prop-…`.

5. **`### Default child attachment`** — `default_attach_mount_point_names` order + `default_child_mount_point_name`.

6. No separate “See also” required; cross-links are inline.

**Unmapped entities**

- Section **`## Unmapped native types`** here **or** only in `properties.md`—**pick one file** per backend to avoid duplication. Prefer **properties.md** if the list is property-centric; **entities.md** if it is purely “no emitter for this `QClass`”.

---

## Anchor and slug conventions

- Entity: `entities.md#entity-<emitter-slug>` (e.g. `#entity-cqpushbutton`).
- Mapped field / event / mount-param: `properties.md#prop-<slug>` (e.g. `#prop-object-name`, `#prop-on-clicked`).
- Mount rows: link mount **parameter glossary** from `properties.md`; the entity table does not require separate mount anchors if the glossary is sufficient.

Generators must emit **stable** slugs (lowercase, non-alphanumeric → `-`).

---

## Generator integration (for maintainers: how to modify generator scripts)

### Source of truth

Prefer generating from the **same structured data** used to build the library, not by parsing the emitted `.py` file:

- Ideal: **intermediate artifact** (e.g. JSON or pickled `frozendict[str, UiWidgetSpec]`) produced by the existing codegen pipeline **before** Python emission.
- Acceptable fallback: import the generated module in a **dev-only** script and read `PySide6UiLibrary.WIDGET_SPECS` (and `UI_INTERFACE.entries`) after ensuring import side effects are safe for CI.

### Deliverables

1. **CLI (PySide6):** `uv run python py-rolyze/pyrolyze_tools/generate_semantic_library.py PySide6.QtWidgets --output-dir <backends/pyside6> --gen-docs` writes `entities.md` and `properties.md` under `py-rolyze/docs/reference/generated/pyside6` (override with `--docs-out`). The shared `generated/README.md` is **not** produced by this step—maintain it manually when combining with Dear PyGui or other backends.
2. **Deterministic output**: sorted keys, stable row order, fixed column set; run in CI or pre-commit optional hook.
3. **Version stamp**: footer line `Generated from py-rolyze <version or git sha> at <iso8601>` on each file or only on `README.md` (pick one; document in README).

### CI / PR expectations

- If generated docs are **committed**: PRs that change specs must include regenerated Markdown.
- Alternatively: generate in CI and publish as artifact; then `README.md` must state that.

### Non-goals for v1

- i18n  
- HTML site theming  
- Embedding full Qt documentation URLs for every setter (optional link template in a later revision)

---

## Acceptance criteria

- [ ] `entities.md` lists every public emitter in the index and has a **complete** section per emitter (props → native application, mounts, default attach).
- [ ] `properties.md` includes a TOC + anchored entries for **every** mapped identifier, each listing **which entities** use it (links to `entities.md`).
- [ ] `properties.md` includes **`## Unmapped native properties`** with a maintained list (e.g. `hidden` when not mapped) and brief notes.
- [ ] Either `properties.md` or `entities.md` includes **`## Unmapped native types`** (no emitter) without duplicating the same list in both files.
- [ ] Regeneration is documented in `py-rolyze/docs/reference/generated/README.md` (PySide6 `--gen-docs` command).
- [ ] Docs layout matches `generated/README.md` + `<backend-id>/{entities,properties}.md` only (no per-emitter files).

---

## Open questions

1. **Dear PyGui / Tkinter**: same folder layout with `<backend-id>`, or separate packages under `py-rolyze/docs/reference/generated/`?
2. **Public vs internal emitters**: should the **entity index** in `entities.md` omit non-`public` entries if the generator distinguishes them?
3. **Link to installed Qt docs**: optional base URL env var for Qt version?

---

## Related types (implementation hints)

Author-facing model types live in `pyrolyze.backends.model`: `UiWidgetSpec`, `UiPropSpec`, `UiMethodSpec`, `UiEventSpec`, `MountPointSpec`, `MountParamSpec`, `PropMode`, `AccessorKind`, `MountReplayKind`, `ChildPolicy`.

Generated consumer: `pyrolyze.backends.pyside6.generated_library.PySide6UiLibrary` (`WIDGET_SPECS`, `mounts` selectors).
