# Import Hook Fix

## Goal
Make `#@pyrolyze` imports reliable, transitive, and fast, while reducing the number of overlapping import-hook implementations.

The immediate target is not "invent a more powerful loader." It is:

- one canonical startup/import hook path
- one canonical transform loader implementation
- Python-native bytecode caching for transformed modules
- cache invalidation that respects PyRolyze compiler changes
- no hidden source semantics hacks

This is a roll-build candidate because the work is infrastructural, tightly scoped, and easy to stage with focused regression checks at each phase.


## Current Problems

### 1. Two import-hook implementations exist
There are currently two separate import-hook paths:

- `src/pyrolyze/import_hook.py`
- `src/pyrolyze/compiler/import_hook.py`

They overlap in responsibility but do not share the same implementation strategy.

This creates real risk:

- startup may use one hook while tests use another
- cache behavior differs by entrypoint
- fixes land in one path and not the other
- debugging import behavior becomes much harder than it should be


### 2. The startup path is still the simpler non-SourceLoader path
The startup `.pth` path currently routes through the compiler import hook entrypoint.

That path works, but it does not take advantage of Python's normal `__pycache__` bytecode model for transformed imports.

The result is:

- repeat imports are more expensive than they need to be
- import behavior is split between a "real" richer hook and a simpler startup hook
- there is more custom caching logic than should be necessary


### 3. Execution is still tied to AST execution helpers
The current compiler import hook lowers to AST and then executes through:

- `load_ast_kernel().exec_module_ast(...)`

That is valid for dynamic transformation helpers, but it is not the best shape for a normal import loader that wants Python-native caching.

For import-time compilation, the better shape is:

- transform source -> AST
- compile AST -> code object
- let the loader execute normal code objects


### 4. Cache invalidation has to respect compiler changes
Plain Python source timestamp caching is not enough.

If:

- the source file is unchanged
- but the PyRolyze lowering rules changed

then cached transformed bytecode must still be invalidated.

So the final design needs both:

- Python-native import caching
- PyRolyze-specific transform fingerprint invalidation


### 5. Import-hook installation ordering is still fragile
The hook has already needed special handling to remain at the front of `sys.meta_path`.

Any design change must preserve:

- idempotent install
- re-install moves the hook back to the front
- startup `.pth` and pytest/plugin setup converge on the same canonical hook


## What Is Not Broken
The core transform pipeline is not the problem.

These parts are already the right conceptual shape:

- `analyze_source(...)`
- `lower_plan_to_ast(...)`
- compile lowered AST into executable module code

The fix is about import-hook structure, caching, and duplication, not a rewrite of the compiler pipeline itself.


## Why The Trojan / Sentinel Model Is Not The Right Fix
The proposed "Trojan" idea is:

- intentionally trigger the loader through a sentinel import
- then strip that import back out before compilation

This can work as a local trick, but it is not a sound long-term import model.

### Why it is unattractive

#### 1. It hides real source semantics
If the source says `import sentinel_module`, but the loader silently erases it, then:

- source no longer matches runtime behavior
- readers and tools see one thing
- execution does another

That is a bad permanent contract.

#### 2. It solves an activation problem by mutating program meaning
The real problem to solve is:

- how PyRolyze knows which modules to transform
- how that transform participates in import and caching

The Trojan approach solves that by altering the user's source tree at import time.

That is backwards. Eligibility and activation should be handled by the loader/finder contract, not by deleting imports.

#### 3. It is brittle
Even if `foo` is replaced with some better sentinel:

- it is still special-case source surgery
- it still creates hidden behavior
- it still becomes another semantic rule authors have to remember

That is exactly the kind of trick that works "for now" and becomes technical debt very quickly.

#### 4. It does not address the main architectural issue
Even if sentinel stripping works, the deeper issues remain:

- two loader implementations
- split startup vs runtime behavior
- no single canonical caching path

So it is not actually a substitute for the needed refactor.


## Important Clarification
The sentinel/Trojan idea is not being rejected because it is impossible.

It is being rejected because:

- the current system already works semantically
- the missing value is correct caching and hook unification
- a sentinel-based source rewrite adds hidden semantics without solving the real structural problem

If later there is a separate, explicit transitive opt-in mode, it should be designed openly as a loader policy, not smuggled in as an import that gets deleted.


## Recommended Design

### 1. One canonical import-hook implementation
Make `src/pyrolyze/import_hook.py` the only real implementation.

`src/pyrolyze/compiler/import_hook.py` should become either:

- a thin compatibility wrapper over the canonical hook, or
- be removed after callers are migrated

The important rule is:

- startup, tests, and manual install must all go through the same implementation


### 2. Use `importlib.abc.SourceLoader`
The canonical loader should move from `importlib.abc.Loader` to `importlib.abc.SourceLoader`.

That gives:

- Python-managed `__pycache__`
- source-to-code caching in the standard import system
- less custom execution logic

The intended shape is:

- `get_filename(...)`
- `get_data(...)`
- `source_to_code(...)`

Inside `source_to_code(...)`:

- read source text
- check transform eligibility
- `analyze_source(...)`
- `lower_plan_to_ast(...)`
- compile the lowered AST to a code object

No Trojan stripping and no source-semantic hacks.


### 3. Do not use AST execution helpers in the loader
For import-time module execution, do not pass code objects back through AST-oriented kernel helpers.

Instead:

- use the kernel to parse/detect/lower
- compile the result to a normal code object
- let the standard loader execution path run that code object

This keeps the import loader aligned with Python's native machinery.


### 4. Keep transform-fingerprint invalidation
The caching design must still incorporate:

- Python bytecode compatibility
- file/source change detection
- transformer fingerprint change detection

This means the final caching story cannot rely on plain source timestamp alone.

The design should continue to use the current concept of:

- `kernel_loader.active_transformer_fingerprint()`

but fold it into the canonical loader path instead of maintaining split logic.


### 5. Reassess custom artifact caches
The current cache helpers in `src/pyrolyze/importer.py` should be reviewed after the SourceLoader transition.

Possible outcomes:

- keep only what is still necessary for transform metadata/debug artifacts
- reduce or remove caches that are only compensating for lack of Python-native import caching

The project should not keep two overlapping persistent caching models without a clear reason.


## Roll-Build Plan

### Start Tag
- `IMPORT_HOOK_START`


### Phase 1: Unify Hook Ownership
Tag:

- `IMPORT_HOOK_01`

Changes:

- make `pyrolyze.import_hook` the canonical implementation
- reduce `pyrolyze.compiler.import_hook` to a compatibility shim or forwarding layer
- ensure `.pth` startup still uses the canonical path
- ensure pytest/plugin setup also converges on the canonical path

Verification:

- marker-based imports still work
- install remains idempotent
- reinstall still moves the finder to the front of `sys.meta_path`
- existing import-hook tests still pass

Stop condition:

- if startup behavior and pytest behavior do not line up cleanly after consolidation


### Phase 2: Convert Canonical Loader To `SourceLoader`
Tag:

- `IMPORT_HOOK_02`

Changes:

- replace the canonical `Loader` with `SourceLoader`
- move transform/compile logic into `source_to_code(...)`
- remove AST-execution-based import path from the canonical loader

Verification:

- transformed module import still executes correctly
- package imports still preserve `__file__`, `__package__`, and package semantics
- transitive import tests still pass
- no semantic drift in author-visible behavior

Stop condition:

- if there is any change in import semantics for existing `#@pyrolyze` modules


### Phase 3: Add Fingerprint-Aware Cache Invalidation
Tag:

- `IMPORT_HOOK_03`

Changes:

- ensure transformed bytecode invalidates when:
  - source changes
  - Python bytecode magic changes
  - transformer fingerprint changes
- keep the logic in the canonical hook path

Verification:

- first import transforms
- second import reuses cached path
- changing source invalidates
- changing transformer fingerprint invalidates

Stop condition:

- if the only safe implementation would require a significantly more invasive cache design than planned


### Phase 4: Remove Obsolete Duplicate Cache/Hook Paths
Tag:

- `IMPORT_HOOK_04`

Changes:

- remove or minimize no-longer-needed duplicate hook logic
- remove or narrow caches that no longer serve a unique purpose
- update docs/comments/tests to reflect the one true path

Verification:

- full import-hook suite passes
- startup install path is still correct
- docs and tests point at the same canonical hook

Stop condition:

- if cleanup would remove debugging or artifact behavior that still has a legitimate separate use


## Test Plan

### Focused regression tests
- startup install uses canonical hook
- pytest/plugin install uses canonical hook
- finder stays at the front after reinstall
- `#@pyrolyze` marker detection still works
- package import path still works
- transitive import still works

### New caching tests
- second fresh import path uses cache without re-running transform
- source edit invalidates cache
- transformer fingerprint edit invalidates cache
- Python bytecode magic mismatch invalidates cache

### Negative tests
- non-marked modules are not transformed
- modules with loader/source read failures fall back cleanly
- no silent semantic rewriting of source imports


## Recommendation
Proceed with the roll-build.

This is the right scale of refactor for phased delivery because:

- the target behavior is clear
- the current duplication is a real maintainability problem
- Python already provides the right import-loader abstraction
- the biggest risk is implementation detail, not unresolved product semantics

The one thing to stay disciplined about is scope:

- fix the loader structure
- fix caching
- do not expand the eligibility model
- do not add sentinel/Trojan source rewriting as part of this work
