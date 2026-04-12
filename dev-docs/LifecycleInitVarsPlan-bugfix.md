# Lifecycle InitVars — spec bugfix plan

This document tracks **review-driven fixes** for the initvars / retention / requestor
implementation relative to [LifecycleInitVarsPlan.md](LifecycleInitVarsPlan.md)
(especially the **semantic dispatch rule** in the preface) and
[LifecycleInitVarsDesign.md](LifecycleInitVarsDesign.md).

It does **not** replace the main plan; it is a **delta** to apply on top of current
`src/pyrolyze/lifecycle.py` without rolling back the overall feature shape.

[LifecycleInitVarsPlan.md](LifecycleInitVarsPlan.md) **Rollout status** and
**Acceptance criteria** are aligned with this doc: git tags are **historical
checkpoints**; “done to spec” for 3A–3C is **pending** this bugfix work.

## Problems (as reviewed)

1. **Kind identity encodes semantics**  
   Behavior is chosen via `issubclass(spec.kind, StaticKind)`, `HookDeclarationKind`,
   `CommitValidatorKind`, and `kind.name in frozenset(...)` instead of **kind-owned**
   semantic queries. That violates the plan’s rule: ask the semantic question on the
   abstraction that owns it.

2. **Wrong error surface on bad consumer signatures**  
   `_initvar_names_in_callable()` catches `TypeError` from
   `_extract_explicit_parameter_names()` and returns no refs. Combined with
   **dead-initvar analysis before** full runner compilation, invalid validator /
   hook / factory signatures can surface as **“unused lifecycle initvar”** instead
   of a **signature / injection** error.

3. **Silent initvar-dependency edges**  
   `_initvar_prereq_initvars_from_specs()` similarly swallows extraction failures,
   which can hide broken `InitVarSpec.default_factory` signatures.

4. **Checkpoint / test gaps** (for calling 3A–3C “done to spec”)  
   Targeted coverage is still thin for: strict failure reasons, `to_frozen()`
   retention behavior, and explicit tagging of validator vs hook vs factory paths
   if phases are audited by tag.

## Design principle (unchanged)

- **No** new `kind == LC_*` / `issubclass(kind, SomeConcreteKind)` **at call sites**
   that decide lifecycle meaning (retention, constructor defaults, scan participation).
- **Yes** to **small, explicit `LCKind` class methods or properties** (or
   `FieldSpec` + kind dispatch) that answer **one semantic question each**.

Concrete terminal kinds **implement** those hooks; generic internal bases may
provide defaults.

## Proposed `LCKind` semantic surface (names indicative)

Exact names are negotiable; semantics are not.

### A. Post-initialization initvar use (retention / `late_seeds`)

| Semantic | Purpose |
| --- | --- |
| `default_factory_may_run_after_initialization(spec) -> bool` | If `spec.default_factory` is present, may it run **after** `LifecycleContextState.__init__` completes (e.g. first read)? If **yes**, initvar names referenced there count toward **retained** storage. |

**Replaces:** `issubclass(spec.kind, StaticKind)` in the requestor scan for
`default_factory` → `late_seeds`.

**Note:** The user-suggested name **`needs_initvars_after_initialization`** is the
same idea scoped to “this field’s `default_factory` is a post-init runner.” Prefer
one name and document it; avoid overloading it for unrelated runners.

### B. Constructor-time default resolution (`__init__` loop)

| Semantic | Purpose |
| --- | --- |
| `eagerly_resolve_default_field_in_constructor(spec) -> bool` | Should `LifecycleContextState.__init__` call `resolve_default_field(name)` for this field after constructor kwargs are applied? |

**Replaces:** paired checks on `NonStoredHookKind` and `StaticKind` with **two
independent booleans** (or one tri-state if you prefer), e.g.:

- Hook **declaration** kinds: **False** (no stored default to resolve there).
- **Deferred** default kinds (today `static`): **False**.
- Typical stored kinds: **True**.

If two booleans collapse cleanly into one, document the combined meaning; do not
reintroduce `issubclass(..., StaticKind)` at the call site.

### C. Default constructor visibility (`FieldSpec.init` default)

| Semantic | Purpose |
| --- | --- |
| `default_field_init(spec) -> bool` | When `init` is omitted on the field descriptor, should merged behavior default to accepting this name as a constructor kw? |

**Replaces:** `_KIND_FIELD_INIT_FALSE` keyed by `kind.name`.

Terminal kinds such as `commit_validator`, `on_before_commit`, … override to
`False`; `commit_order_key` overrides to `True` (matches current product behavior).

### D. Initvar requestor scan participation (consumer callables)

Avoid branching on `HookDeclarationKind` / `CommitValidatorKind` at the scan site.

| Semantic | Purpose |
| --- | --- |
| `initvar_requestor_callables(spec) -> Iterable[tuple[str, Callable[..., Any]]]` | Named callables to inspect for explicit initvar parameter names (e.g. `("default", hook)`, `("commit_validator", validator)`). Empty if none. |

**Replaces:** separate `if issubclass(..., HookDeclarationKind)` /
`CommitValidatorKind` blocks.  
`working_default_factory` remains driven by **`spec.working_default_factory is not
MISSING`** (spec semantic), not by `TransientKind` identity.

Scan implementation **iterates** the returned `(label, fn)` pairs and applies the
same strict signature rules to each.

### E. `commit_order_key` — generic `default_factory` path only

[LifecycleInitVarsDesign.md](LifecycleInitVarsDesign.md) names **commit_order_key**
`default_factory` in the requestor-scan list so the **design** enumerates every
injection-eligible callable. That is **documentation completeness**, not a cue for
a **separate code branch**.

**Bugfix rule:** do **not** add `CommitOrderKeyKind` (or `commit_order_key`) special
cases in the requestor scan. Those fields are already included by the **generic**
rule: whenever `spec.default_factory is not MISSING`, scan that callable for
explicit initvar names (with strict signature validation). Same path as `const`,
`managed`, `commit_order_key`, etc.

**Liveness vs retention:** `commit_order_key`’s `default_factory` runs during
**eager** `resolve_default_field` in `LifecycleContextState.__init__` (not
post-init first read). So **`default_factory_may_run_after_initialization`** (or
the chosen hook name) should be **False** for `CommitOrderKeyKind`: referenced
initvars count toward **live** / `all_seeds`, but **not** toward **`late_seeds`**
/ retained storage under current semantics.

This section exists so no one reintroduces a one-off scanner branch “because the
design doc mentioned commit_order_key explicitly.”

## Requestor scan and decoration order

1. **Strict** parameter extraction (or compile) for **every** consumer callable
   returned from `initvar_requestor_callables`, plus `default_factory` /
   `working_default_factory` when present. **Do not** swallow `TypeError` into
   “no refs” for these paths.

2. **Initvar `default_factory` dependency graph** (`_initvar_prereq_initvars_from_specs`
   or successor): also **strict** — bad initvar factory signatures fail at
   decoration with the same style of error as other lifecycle callables.

3. **Dead-initvar** (`declared \ live`) runs only after consumer signatures are
   validated, so “unused initvar” never masks a signature bug.

Optional: factor a single internal helper, e.g.
`_explicit_parameter_names_or_raise(context: str, fn: Callable) -> tuple[str, ...]`,
used by scan, initvar factories, and table compilation for consistent messages.

## Tests to add or strengthen

Align with plan exit language; minimal set:

| Area | Intent |
| --- | --- |
| **Validator** | Bad signature (e.g. disallowed param) → **TypeError** mentioning signature/injection, **not** “unused initvar”. |
| **Hook** | Same. |
| **Factory / `working_default_factory`** | Same. |
| **Initvar chain** | Bad `InitVarSpec.default_factory` signature → decoration failure, not empty prereqs. |
| **`to_frozen()`** | Retained value uses `to_frozen()` when present; construction aborts if `to_frozen()` raises. |
| **Retention split** | Assert `__class_retained_initvars__` empty vs non-empty for eager-only vs late paths (already partially covered; keep explicit). |
| **`InitVarSpec.init` merge** | Module-level or tagged test for incompatible `init` across MRO (if not already flagged in review). |

## Files to touch

- `src/pyrolyze/lifecycle.py` — `LCKind` hooks, scan, `__init__` loop,
  `_default_init_for_field_kind` replacement, strict extraction / ordering in
  `managed_context`.
- `tests/test_api_lifecycle.py` — new failure-path and `to_frozen()` cases.
- Optionally a short cross-link from [LifecycleInitVarsPlan.md](LifecycleInitVarsPlan.md)
  **Rollout status** (“spec bugfix tracked in …-bugfix.md”) once work starts.

## Non-goals

- Reverting initvars, retention, `classvar`, or validator compilation **as a whole**.
- Introducing a parallel runner-policy framework **unless** the minimal `LCKind`
  hooks prove insufficient (YAGNI until then).
- Changing public `initvar` / `classvar` user API unless a bugfix strictly requires it.

## Completion criteria

- No remaining **initvar-related** decisions at call sites via
  `issubclass(spec.kind, <concrete terminal kind>)` or `kind.name in frozenset(...)`
  for the behaviors listed above.
- Invalid consumer or initvar-dependency signatures **always** fail with an
  appropriate **signature / parameter** error before dead-initvar analysis.
- Tests above green; lifecycle suite remains green; full-suite unrelated failures
  unchanged unless separately fixed.
