# LazyNativeBackendLoadingPlan — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/LazyNativeBackendLoadingPlan.md` at `4f0812802d2abd951e46fb72995a66f9c94d45bb`; design for review, not implementation acceptance; recorded 2026-10-10.
**Baseline:** Pyrolyze `4f0812802d2abd951e46fb72995a66f9c94d45bb`. Authority and source evidence read using `git show` at that revision.
**Date:** 2026-10-10
**Axis:** Safety: degraded paths, failure recovery, publication, compatibility, and reachable stuck states. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks. I pre-commit to GO on a revision that resolves P2-1 as specified.

---

## 0. Evidence base

- Verified `git rev-parse HEAD` at start and end: both returned the exact baseline SHA.
- Start/end `git status --short` agreed: one modified fuzz test and three untracked documents. These remained out of scope; none was read.
- Read process authority `review-loop/SKILL.md`, including draft isolation, peer blindness, severity, and closure requirements.
- Read committed `AGENTS.md`, `dev-docs/README.md`, `dev-docs/LazyLoadingOptimizationRequirements.md`, `dev-docs/ApiDesignRules.md`, `dev-docs/SemanticUiLibraryDesignRules.md`, and `dev-docs/PackageStructureRules.md`.
- Read the complete controlling draft; specifically examined loading/publication at lines 143–169, compiler boundaries at 199–212, diagnostics/regeneration at 214–251, and implementation/acceptance sections.
- Inspected committed `src/pyrolyze/compiler/kernels/v3_14/rewrite.py:2461–2619`, `src/pyrolyze/import_hook.py:70–185`, and `pyrolyze_tools/generate_semantic_library.py:1187–1200`.
- Inspected committed `src/pyrolyze/backends/mountable_engine.py:1–190`, `:262–285`, `:326–336`; `src/pyrolyze/backends/pyside6/__init__.py:1–7`; `src/pyrolyze/unified/qt.py:1–160`; and `pyproject.toml:1–59`.
- Commands were inspection only: `git show`, `git rev-parse HEAD`, `git status --short`, `rg`, `nl`, `sed`, and `cat`. No tests, builds, writes, or git mutations occurred. Counterexamples below are text-permitted sequences, not executed implementation failures.

## 1. Findings

### [P2-1] Multi-file regeneration has no failure-safe publication or recovery contract

**Location:** `dev-docs/LazyNativeBackendLoadingPlan.md:234–242`, especially 238–240; acceptance coverage at 274 and the canonical generator/distribution coverage section.

**Violated invariant:** A validated candidate must not destroy the usability or recoverability of the previously complete generated catalog merely because publication fails partway through.

**State sequence:** Start with complete generation A. Generate and validate B in staging. Follow the prescribed replacement operation by replacing the facade/index with B, then begin replacing owned shards. A filesystem error or process interruption occurs before an indexed shard is replaced. The destination now contains B’s index and A’s shard. Alternatively, publish shards first and interrupt before replacing A’s index. Both replacement orders satisfy the text; neither guarantees a complete destination.

**Impact:** A fresh process encounters generation mismatches or missing definitions in a previously working catalog. The required stamp checks appropriately reject the mismatch, but do not restore availability. Restarting, as prescribed for artifact repair, cannot repair the on-disk set. The plan specifies neither retained generation A, rollback, resumable publication, nor detection and recovery before packaging. Successful reproducibility checks do not exercise this failure.

**Required correction:** Define the publication failure boundary explicitly. Require either whole-generation switching with retention of the previous complete generation, or a recoverable publication protocol that preserves the old set and restores/completes it before the destination is admitted for use or packaging. State interruption, replacement/deletion failure, and retry behavior. A non-transactional approach is acceptable only with explicit exclusive-use preconditions and a concrete recovery guarantee; staging validation alone is insufficient.

**Closure/regression test:** Add a future fault-injection acceptance gate covering every replacement and stale-file deletion boundary. After interruption or injected failure, verify that the documented recovery produces exactly complete A or complete B, never an admitted mixture; unrelated files remain untouched; retry succeeds; and a fresh-process one-widget lookup and package-inventory validation succeed. Draft closure requires this contract and gate in the revised text, not implementation now.

## 2. Invariant analysis

- **Known failures must not become unknown kinds:** Held in the proposal. Lines 173–177 require `.get` to propagate known-entry failures; lines 216–232 prohibit silent fallback and partial publication. The existing engine’s `.get` boundary can consume this without a mounting rewrite.
- **Compiler failures must remain attributable:** The existing collector suppresses import failures at `rewrite.py:2475–2478`, and hint resolution suppresses exceptions at 2612–2619. The draft explicitly identifies swallowed lazy-load failures as unacceptable and requires recognition/error parity before compiler changes. This is an implementation proof obligation, not permission to ship degraded recognition.
- **First-load identity and reentry:** The proposed reentrant lock, in-progress check, validation-before-publication, dependency-chain diagnostics, and identical concurrent results address same-backend resolution races. Shared modules are forbidden from importing widgets or their facade. Inspection did not establish a concrete allowed lock inversion; no deadlock finding is asserted.
- **Mixed artifacts fail before native construction:** Index/shard compatibility validation is required at first use. This prevents unchecked native construction but does not solve P2-1’s publication recovery.
- **Compatibility and scope:** Mapping representation and classmethod binding are explicit preimplementation decisions. Installed wheel/sdist verification is mandatory; frozen/zip support is not presumed. Tk, DPG, member compaction, and lifecycle changes remain deferred.
- **Disclosure:** The design introduces no credential collection or external reporting channel. Failure records must avoid retained tracebacks; generated artifacts prohibit absolute paths.

## 3. Risks and next action

Import-lock ordering, transient-failure cleanup, shared-dependency compatibility, descriptor binding, and compiler diagnostic preservation still require implementation evidence. This review grants none.

The single next action is to amend regeneration publication and its fault-injection acceptance gate to close P2-1, then obtain the focused Safety re-verdict.
