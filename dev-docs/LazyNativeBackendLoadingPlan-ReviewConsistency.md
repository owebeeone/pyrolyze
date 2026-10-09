# LazyNativeBackendLoadingPlan — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/LazyNativeBackendLoadingPlan.md` at `4f0812802d2abd951e46fb72995a66f9c94d45bb`; design for review, not implementation or performance acceptance.
**Baseline:** Pyrolyze `4f0812802d2abd951e46fb72995a66f9c94d45bb`. Object, controlling documents and source inspected through committed bytes using `git show HEAD:<path>`.
**Date:** 2026-10-10
**Axis:** Consistency with the controlling graph, existing interfaces and proposed acceptance evidence. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero findings. This verdict accepts the draft’s consistency only; its declared pre-implementation proof gates remain mandatory.

---

## 0. Evidence base

Only permitted inspection commands were used: `git rev-parse HEAD`, `git status --short`, `git show`, `cat`, `rg`, `nl` and `sed`. No tests, builds, writes or Git mutations occurred.

HEAD matched the exact baseline at both start and end. Status remained unchanged: the modified fuzz test and three untracked documents identified in the brief were excluded. No current-round peer report was read.

Read evidence:

- Process authority: `review-loop/SKILL.md`, including draft isolation, peer blindness, severity, deferrals and verdict rules.
- Object: `dev-docs/LazyNativeBackendLoadingPlan.md:1–375`, covering boundaries, triggers, caching, compiler recognition, diagnostics, generation, acceptance and measurements.
- Controlling documents: `AGENTS.md:1–95`; `dev-docs/README.md:1–195`; `dev-docs/ApiDesignRules.md:1–83`; `dev-docs/SemanticUiLibraryDesignRules.md:1–82`; `dev-docs/PackageStructureRules.md:1–169`; `dev-docs/LazyLoadingOptimizationRequirements.md:1–430`.
- Compiler: `src/pyrolyze/compiler/kernels/v3_14/rewrite.py:2461–2619`, imported-symbol collection and runtime type-hint resolution.
- Generated surface: targeted regions of `src/pyrolyze/backends/pyside6/generated_library.py`, including manifest construction, private helper at line 32226 and `CQLabel` signature at lines 39978–39998.
- Generator: `pyrolyze_tools/generate_semantic_library.py:715–790`, plus definitions at lines 835–843, 1187–1200 and 2131–2145.
- Registration/runtime: `src/pyrolyze/api.py:304–318`; `src/pyrolyze/backends/model.py:1–215`; targeted engine regions at `src/pyrolyze/backends/mountable_engine.py:89–124,262–336`; `src/pyrolyze/backends/pyside6/engine.py:1–220`; `src/pyrolyze/pyrolyze_native_pyside6.py:1–95`.
- Unified exports: `src/pyrolyze/unified/__init__.py:1–61`, `factory.py:1–48`, `qt.py:1–172`; related contract excerpts from `dev-docs/UnifiedMountBasedNativeApi.md:89–172`.
- Evidence harnesses: `tests/test_generated_backend_libraries.py:1–220`; targeted fixture/test definitions in `tests/test_generate_semantic_library_tool.py`; `tests/versioned_test_harness.py:1–110`; `tests/data/gold_src/phase7_ui_interface_kwds_native_wrapper.py:1–44`; `pyproject.toml:1–59`.
- Import-hook execution and cache paths: targeted regions of `src/pyrolyze/import_hook.py:19–29,85–145`.

## 2. Invariant analysis

**Deferred requirements remain obligations.** Requirements R1.3 and R2 are not satisfied by widget-level sharding alone. The draft explicitly retains them at lines 8–12, 253–262 and 277. Its Qt checkpoint therefore does not falsely supersede the requirements’ broader representation acceptance criteria. No superseded-clause list is claimed or needed for this supplement.

**Explicit author semantics remain controlling.** The draft’s signature, annotation, default and coercion preservation rules at lines 96–112 agree with the API and semantic-library rules. The `CQLabel("Ready", enabled=True)` example matches the committed positional `text` parameter. Internal shard classes are expressly not a second public authoring surface.

**The compiler eagerness obstacle is correctly identified.** The committed collector enumerates manifest entries and resolves each callable at `rewrite.py:2563–2601`. Consequently, a backend-only lazy resolver cannot establish compilation coldness. The draft acknowledges this and requires an approved recognition boundary, including aliases, containers, handlers and dynamic references, before implementation. This is a substantive gate, not an unsupported claim that the existing compiler already works lazily.

**Descriptor identity is not assumed proved.** Rebinding transformed classmethods could affect ownership, metadata and private-name lookup. Lines 102–112 and slice 0 require a focused binding proof and stop if the existing contract cannot be preserved. The unified adapter currently attaches native callable objects at `unified/qt.py:160–164`; selective forwarding to the same cached callable preserves the stated identity target.

**The mapping boundary matches committed consumers.** Host construction passes `WIDGET_SPECS` unchanged; engine construction stores a `Mapping`; `_spec_for` uses `.get(kind)`. The draft’s known-entry failure propagation preserves unsupported-kind handling without disguising broken artifacts as index misses. Existing concrete `frozendict` assertions are explicitly identified as requiring an approved representation decision.

**Acceptance separates coldness from deliberate realization.** Full catalog validation is explicitly permitted in isolated parity coverage. Fresh-process checks separately cover import, host creation, compilation and first use. Timings distinguish disk-cache warmth from loaded definitions, and toolkit imports from GUI resource creation. These requirements are mutually satisfiable at draft level.

**No conflicting runtime expansion was found.** Ordinary resolved specs retain the committed model and mount interfaces. The plan neither changes lifecycle ownership nor replaces mount selectors or unified operations. Packaging additions address files absent from current package configuration rather than assuming editable-checkout success proves distribution support.

## 3. Risks and next action

Static inspection cannot establish transformed descriptor compatibility, selective compiler recognition, installed-package parity or performance gains. None is represented as established by this draft.

The single next action is slice 0: close and record the compiler recognition, descriptor-binding and mapping-representation decisions before implementation proceeds.
