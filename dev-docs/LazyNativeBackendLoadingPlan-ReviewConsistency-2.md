# LazyNativeBackendLoadingPlan — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/LazyNativeBackendLoadingPlan.md` at `d0502025e65072d5892d05c39862396520cf6241`; design for review, not implementation or performance acceptance.
**Baseline:** Pyrolyze `d0502025e65072d5892d05c39862396520cf6241`. Object, authority documents and source read from committed bytes using `git show`. Review interval: `4f0812802d2abd951e46fb72995a66f9c94d45bb..d0502025e65072d5892d05c39862396520cf6241`.
**Date:** 2026-10-10
**Axis:** Consistency with controlling contracts, existing interfaces and proposed acceptance evidence. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero findings. This accepts draft consistency only; compatibility, implementation and performance remain subject to the declared proof gates.

---

## Prior-Finding Closure

| Prior Consistency result | Verification | Disposition |
| --- | --- | --- |
| GO, no findings at `4f0812802d2abd951e46fb72995a66f9c94d45bb` | Read `dev-docs/LazyNativeBackendLoadingPlan-ReviewConsistency.md`; independently rechecked affected interfaces and controlling requirements. | No inherited finding requires closure. |

Read `dev-docs/LazyNativeBackendLoadingPlan-RemPlan-1.md`. Its cross-axis remediation is legitimate prior-round context; this report does not independently close the other axis’s finding.

## Changed-Range Analysis

- **Lines 55–68 and 98–109:** The replaceable facade and signature stub move under `_generated/`; stable Python and explicit stub re-exports remain at the existing import path. This separates generation ownership from handwritten compatibility shims without requiring a second author-facing class.
- **Lines 243–285:** Directory promotion replaces per-file publication. The text explicitly recognizes the two-rename absence window, excludes consumers during maintenance, retains the old generation, requires recovery before admission, and handles first generation and cleanup failure separately.
- **Lines 370–381:** Acceptance now exercises directory renames, marker transitions, failed generator exit, first generation and backup cleanup. The writer proof remains a slice-1 prerequisite to real catalog migration.
- The interval contains both `8558536b4e2aefede6ee82dbe0816c12c49fa5ae` and `d0502025e65072d5892d05c39862396520cf6241`; both document patches were inspected. No source implementation is accepted by these changes.

## 0. Evidence Base

Only inspection commands were used: `git rev-parse HEAD`, `git status --short`, `git show`, `rg`, `nl`, `sed` and `cat`. No tests, builds, writes or Git mutations occurred.

HEAD matched the exact tuple at start and end. The committed object remained pinned. End status additionally showed two untracked round-2 prompt files; neither was read. The modified fuzz test and other untracked documents were excluded. No current-round peer report or prompt was read.

Evidence inspected:

- Process authority: `review-loop/SKILL.md`, including replacement reviewers, blindness, draft acceptance and severity rules.
- Object: `dev-docs/LazyNativeBackendLoadingPlan.md:1–433`; prior Consistency report and remediation plan in full.
- Controlling graph: `AGENTS.md:1–95`, `dev-docs/README.md:1–195`, `LazyLoadingOptimizationRequirements.md:1–430`, `ApiDesignRules.md:1–83`, `SemanticUiLibraryDesignRules.md:1–82`, and `PackageStructureRules.md:1–169`.
- Compiler recognition: `src/pyrolyze/compiler/kernels/v3_14/rewrite.py:2451–2619`; import-hook marker, execution and fingerprint paths at `src/pyrolyze/import_hook.py:19–29,85–145`.
- Registration/specs: `src/pyrolyze/api.py:295–318`, `src/pyrolyze/backends/model.py:1–215`; engine mapping storage and resolution at `src/pyrolyze/backends/mountable_engine.py:89–124,262–280,308–336`.
- Public integration: `src/pyrolyze/backends/pyside6/__init__.py:1–7`, `src/pyrolyze/pyrolyze_native_pyside6.py:1–91`, and unified `__init__.py:1–61`, `factory.py:1–48`, `qt.py:1–172`; supplementary contract `dev-docs/UnifiedMountBasedNativeApi.md:89–175`.
- Generator and generated signatures: targeted generator definitions at lines 715–780, 1187–1247 and 2131–2196; generated library helper/signature regions at lines 32218–32260 and 39976–40035.
- Existing evidence harnesses: `tests/test_generated_backend_libraries.py:1–205`, fake-widget and writer tests at `tests/test_generate_semantic_library_tool.py:44–134,353–397`, packed-call golden source at `tests/data/gold_src/phase7_ui_interface_kwds_native_wrapper.py:1–44`, and `pyproject.toml:1–59`.

## 2. Invariant Analysis

**Relocation does not require an author API change.** The compiler examines the imported class object and its `UI_INTERFACE`, not whether the class was defined in the imported module (`rewrite.py:2483–2488,2563–2601`). A direct re-export therefore preserves this recognition boundary. The draft requires one facade identity, not a subclass or replacement wrapper (`LazyNativeBackendLoadingPlan.md:98–120`). Its explicit stub re-export can expose signatures from the generated facade stub without executing shards. This is coherent, not proof of an implemented static-tool result.

**Descriptor compatibility is explicitly gated.** Keeping the shard class name preserves private-name mangling; binding its descriptor to the public facade targets the existing `cls.__element` call shape. Runtime hints depend on the callable’s defining module (`rewrite.py:2606–2619`), so preserving annotation globals matters. The draft expressly requires binding, hints, component metadata and packed-call proof before adoption at lines 111–121 and 320; it does not assume relocation alone proves them.

**Compiler coldness is not falsely attributed to backend loading.** The existing collector resolves every manifest member. Lines 208–221 acknowledge that obstacle and require an approved bounded reference-selection change, including dynamic-reference compatibility. The one-widget compilation acceptance is conditional on that decision, not contradictory to committed compiler behavior.

**Runtime and unified contracts remain intact.** Host construction passes the mapping unchanged; the engine stores it and resolves through `.get`. Unknown keys and known broken definitions remain distinguishable. Unified forwarding must retain native callable identity and a unified-owned manifest, matching the current attachment contract at `unified/qt.py:160–164`. Concrete `frozendict` compatibility is a recorded decision, not silently weakened coverage.

**Publication and evidence requirements agree.** No atomic swap is claimed. Pending or absent catalogs are inadmissible; successful promotion and recovery have distinct complete-inventory outcomes. Interruption testing precedes migration, while installed-package checks follow integration. Deliberate catalog introspection and fresh-process coldness tests are separate, so their load assertions are satisfiable.

**No controlling clause is silently superseded.** The document is a supplement, not an amendment claiming deleted obligations. Member-level laziness and representation compaction remain outstanding (`LazyLoadingOptimizationRequirements.md:131–145,170–250,392–395`; plan lines 8–12,300–309,324). Explicit signatures, coercions, registration separation and backend ownership agree with the standing rules. Lifecycle behavior and unified operations are not redefined.

## 3. Risks and Next Action

Static inspection cannot establish transformed descriptor behavior, installed-tool stub discovery, selective recognition completeness, package exclusion of maintenance artifacts, or measured gains. Those remain implementation proof obligations, not established results.

The single next action is slice 0: record the compiler-recognition, descriptor-binding and mapping-representation decisions before implementation proceeds.
