# Grouped lazy native loading implementation plan

## Status and scope

Qt and Tk migrations implemented. Implements the proposed boundaries in
[the design](LazyNativeBackendLoadingPlan.md), including its grouped-module
amendment. A direct focused review identified the grouped failure-publication
gap; the owner adopted whole-group validation and failure isolation. This does
not extend the earlier review-loop GO/GO verdicts or authorize other runtime
contract changes.

Start with the supported Qt catalog, not new Qt type coverage. Preserve authored
names, explicit signatures, handler annotations, mount routing, callable identity,
and ordinary spec objects. Keep lifecycle completion and scheduling unchanged.
Tk now reuses those boundaries; DearPyGui remains a separate follow-up. The bytecode reuse fix remains
in place; this work targets eager definition construction and retained memory too.

## Checkpoints

### Current Qt acceptance

The real catalog now exposes the same 105 supported kinds through a stable
author import and demand-loaded groups capped at four kinds. There are 35 shards,
38 Python files, and 40 inventoried artifacts. All 105 wrapper ASTs, spec
expressions, signatures, and the mount namespace match the accepted eager source.
The registry is a read-only Mapping rather than a concrete frozendict.
Package learnings and unified structural helpers are also demand-loaded.
Import constructs zero kinds; requesting a label constructs four; the six-kind
demo workload constructs 19 across five groups. DearPyGui remains eager; Tk's
subsequent checkpoint is recorded below.

Offline regeneration reconstructs accepted definitions from the active groups.
Promotion waits for the generator subprocess to exit successfully. Import
admission checks completeness without hashing every shard. Builds validate source
hashes and syntax, then verify the finished wheel or source archive against the
captured inventory, including rejection of stale build-cache artifacts. Extracted
source archives can rebuild the wheel with the validator and backend included.
Promotion remains exclusive offline maintenance, not live replacement or a
power-loss durability guarantee.

Three fresh-process measurements per configuration compared caps 1, 4, 8, and
16. With compiler initialization excluded, the six-kind workload's warm median
fell from 31.6 ms eager to 13.4 ms at cap four. Retained Python allocations fell
from 7.54 MB to 1.65 MB. Cap one retained less but required 108 Python files;
caps eight and sixteen retained more unused definitions. Cap four is the chosen
file-count/memory compromise, not a universal optimum.

Including compiler initialization, warm timings remained about one second;
there is no demonstrated material whole-application warm-start speedup. The
same six-kind memory probe fell from 40.17 MB to 34.28 MB, with peak process RSS
about 151.75 MB versus 137.27 MB on this machine. RSS is a peak, not retained
Python memory. First-run timings share caches from preceding workloads and are
not a uniform cold-start comparison. Pytest startup was not separately measured.

Reproduce the definition-cost comparison with dependencies installed:

```sh
PYTHONPATH=.:src python scripts/benchmark_grouped_qt.py \
  --accepted-catalog src/pyrolyze/backends/pyside6/_generated \
  --preload-compiler
```

The implementation evidence below records earlier checkpoints chronologically;
its references to an eager Qt catalog describe those checkpoints, not current
status. Final checkpoint verification, including the archive guard:
1,262 passed and 20 existing skips in 82.17 seconds, with the existing Tix
deprecation warning. The focused Python-assembly run passed 97 checks with four
existing skips. Actual project wheel and source-distribution builds passed both
source and finished-archive admission. Existing native Qt and grid integration
tests are included; no new manual GUI interaction claim is made.

### Tk acceptance

Tk uses the same loader and offline publication machinery. Its accepted 105
kinds are divided by their defining module into 29 shards, capped at four kinds,
with 32 Python files and 34 inventoried artifacts. All spec expressions, wrapper
bodies, and mount namespaces match the accepted eager source by AST comparison.
The stable import preserves the author surface, while the immutable registry
uses Mapping rather than concrete frozendict, as for Qt. Learnings load only on
request. The existing unified Tk adapter does not enumerate native definitions,
so no adapter or compiler changes were required for this checkpoint.

Fresh-process compiler coverage proves importing the facade constructs zero
kinds and compiling a label loads one four-kind group. The six-control benchmark
loads four groups and constructs 16 kinds rather than 105. With compiler startup
excluded, retained definition allocations fell from 1.18 MB to 0.51 MB. Three-run
warm medians were 8.36 ms eager versus 9.15 ms grouped for that workload: no
meaningful warm-start improvement is claimed. Import-only retained allocations
fell from 1.18 MB to 0.12 MB. The cap remains four for consistency with the bounded
Qt policy, not a claim of an independently optimal Tk group size.

Including compiler initialization, the same workload's three-run warm median
was 1.07 seconds eager and 1.03 seconds grouped; this small difference is not
treated as a significant startup win. Retained Python allocations were 25.45 MB
versus 24.78 MB. The definition-only saving is a small share of the complete
first-use footprint. First-run probes share caches from preceding workloads,
so they do not establish a uniform cold-start comparison.

The shared generator command has thin Qt and Tk entry points. Replacement still
waits for a successful generator subprocess, reconstructs accepted source from
current groups, and uses the existing identity-checked promotion/recovery path.
Reconstruction retains the accepted private helper's decorator and explanatory
comment from the shards, rather than substituting the simplified facade helper.
The existing round-trip regression now requires byte-identical regeneration;
both real Qt and Tk catalogs reproduce their admitted identities.
Build admission now explicitly requires both catalog directories. Actual wheel
and source archives passed source and archive validation; the extracted wheel
kept unrelated Tk groups cold, and the extracted real source archive rebuilt.

Verification: the final full default suite passed 1,264 checks with 20 existing
skips in 75.98 seconds, with
the existing Tix deprecation warning. The affected Python-assembly run passed
75 checks with four existing skips, including native-host, grid, unified, and
history/rollback fuzz coverage. After the reconstruction correction, the focused
Python-assembly generator/sparse-loading checks also passed all 43 checks.
No new manual GUI interaction claim is made.

Reproduce Tk's definition-cost comparison:

```sh
PYTHONPATH=.:src python scripts/benchmark_grouped_qt.py \
  --root-module tkinter \
  --accepted-catalog src/pyrolyze/backends/tkinter/_generated \
  --maximum-kinds 4 --preload-compiler
```

Under exclusive offline maintenance, regenerate into a new staging directory
and promote only after generation succeeds:

```sh
PYTHONPATH=.:src python -m pyrolyze_tools.generate_grouped_tk_library \
  --maximum-kinds 4 \
  --staging-dir src/pyrolyze/backends/tkinter/_generated_staging \
  --promote-to src/pyrolyze/backends/tkinter/_generated
```

Backup cleanup remains an explicit identity-checked maintenance operation.
DearPyGui's generated item classes and curated author surface have not changed.

### Implementation evidence

Initial inventory: `PySide6WidgetEngine` and `MountableEngine` accept a Mapping
and retain it without a constructor-time copy. The generated-library tests
explicitly require frozendict, so the representation decision remains a gate.
`_collect_imported_annotated_symbols` in the compiler's `rewrite.py` fetches every
UI_INTERFACE entry. After owner approval, discovery now builds one AST member
index and fetches only referenced entries for imported UI aliases. Narrow tests
cover calls, with scopes, member-value aliases, nested functions, unused imports,
deduplication, unknown names, and propagation of broken-member errors. Dynamic
access does not cause a full-catalog fallback. Existing compiler goldens pass on
the Python assembly backend. The unified Qt adapter and backend package imports
still need their own demand-loading changes; the real catalog remains eager.

`pyrolyze_tools/native_library_grouping.py` now provides the offline partitioning
primitive. Its narrow tests cover deterministic order, positive size caps,
family separation, exact boundaries, size one, invalid inputs, and collision-free
module names.

`pyrolyze_tools/generate_grouped_native_library.py` now emits an empty package
initializer, a lightweight name-only index, and separately importable marked
source modules. It uses the existing semantic emitter with catalog-wide kind
assignment, preserving explicit signatures and raw authored output. The generation
identity covers sources and grouping configuration. Its writer creates only a
new staging directory and refuses an existing destination; partial staging after
a write failure is not publishable. The fake-widget fixture exercises caps one
and two, reproducible regeneration, index-only import, individual group import,
name collisions, and unchanged signature defaults. The existing eager writer
remains unchanged.

The fixture generator now emits an ordinary lazy facade and explicit signature
stub. `backends/lazy_library.py` resolves groups through their index, validates
generation identity, complete spec inventory, manifest kind, compiled classmethod,
and facade binding before publishing caches. Group failures retain messages, not
tracebacks; repeated failures remain isolated from unrelated groups. Reentry
poisons the group even if shard code suppresses its error. Fixture coverage
includes cold concurrent resolution, stable identities, compiler-authored panel
execution, incomplete siblings, generation mismatch, and suppressed reentry.
Inventory validation is once per group class, not once per member; avoid an
N-squared validation scan. Wider compatibility/distribution acceptance and real
Qt migration remain pending.
The live Qt catalog still loads eagerly; this is not completed adoption.

Verification for the facade checkpoint: 60 generator/discovery/resolver checks
pass on Python assembly; the full default suite has 1,236 passes and 20 existing
skips. The resolver fixture installs and restores its own compiler finder so
prior import-hook fault tests cannot turn generated shard imports into raw source
execution. The ordered import-hook/resolver regression passes too. No memory or
startup benefit is claimed before real-catalog migration and measurement.

The grouped writer now writes a deterministic hashed file inventory last and
validates the complete staging directory without executing generated code.
`pyrolyze_tools/generated_library_publication.py` provides offline sibling-directory
promotion with an external pending marker, retained backup, and verified recovery.
Admission refuses pending publication and incomplete or mixed artifacts.
Recovery restores the old generation or leaves no active generation on a failed
first install; an installed candidate is quarantined, not silently deleted.
Identity-checked quarantine cleanup enables retry. Backup cleanup is separate
from admission, so a cleanup failure does not revoke the complete new generation.
Callers must exclude imports, builds, and concurrent maintenance; this is neither
live replacement nor a power-loss durability guarantee.

Fourteen narrow publication checks cover interruption before and after install,
automatic rollback on ordinary rename errors, malformed markers, missing/changed/
extra artifacts, failed restoration followed by retry, and failed backup cleanup.
All pass on Python assembly. The combined generator, discovery, grouping, and
resolver run passes 74 checks on that backend.
Final default regression: 1,250 passed, 20 existing skips, one existing Tix
deprecation warning, in 66.03 seconds. No real backend catalog was changed.

Generated package initializers now reject pending publication, a missing
inventory, and missing inventoried files before importing the index. The facade
also checks the index generation against the inventory. Import admission is a
lightweight completeness check, not a repeated hash/syntax scan of every shard;
requested groups retain their existing semantic validation. Offline source
validation and distribution builds perform the full hash/syntax checks.

`pyrolyze_build_backend.py` wraps setuptools build, metadata, and requirement
hooks with source admission. Pending markers block builds; inventories and
recognizable generated facades identify directories requiring full validation.
Setuptools package data and `MANIFEST.in` include inventories and signature stubs,
and retain the backend/validator in source archives. The distribution fixture
checks every generated artifact in wheel and sdist output and rebuilds a wheel
from the extracted sdist. Real Qt catalog migration and installed application
compatibility/measurement are still pending.

### Planned sequence

1. Establish compatibility and baseline.
   Inventory manifest, wrapper, and WIDGET_SPECS consumers, including compiler
   discovery, native engines, unified attachment, introspection, and tests.
   Record where concrete frozendict behavior is required. Measure fresh-process
   facade import, compilation, first use, and sparse/representative application
   load sets and memory. Separate toolkit import from generated definitions.
   Prove cached classmethod binding and selective imported-symbol recognition in
   the existing canonical compiler fixture. Discuss any public representation or
   compiler-contract decision before implementing it.

2. Prove deterministic grouped generation on the fake-widget fixture.
   Add a positive maximum kinds-per-module generator setting and explicit family
   assignments. Sort kinds stably within each family and partition into bounded
   groups; emit group membership and direct dependencies in a lightweight index.
   Test size-one and grouped output, exact-cap boundaries, invalid settings, and
   byte-identical regeneration. Each kind retains its full metadata and explicit
   wrapper signature. Do not choose the production cap yet.

3. Implement backend-local resolution against that fixture.
   Add index-only facade discovery and a read-only spec Mapping once the
   compatibility decision is settled. Resolve an indexed group through ordinary
   Python imports; validate every indexed group member before exposing any of
   its specs/callables. A malformed member fails the entire group without partial
   publication; cache that failure consistently while unrelated groups remain
   usable. Imported module objects are not a substitute for validation.
   Cache identities, preserve classmethod binding, and retain the design's
   concurrency, reentry, dependency-cycle, and deterministic failure rules.
   Prove same-group co-loading and unrelated-group isolation. Successful behavior
   belongs in canonical fixtures; narrow fault tests cover resolver mechanics.
   Add a valid-plus-malformed-member fault fixture: neither sibling publishes,
   repeated and concurrent requests fail consistently, and another group resolves.

4. Implement safe generation publication and packaging.
   Generate the complete replaceable tree in staging, validate successful output,
   then use the design's exclusive promotion, marker, backup, and recovery protocol.
   Preserve stable public shims and stubs. Test interrupted promotion and retry,
   reject incomplete generations, and verify every indexed module enters wheel
   and sdist artifacts. Do this before replacing the real Qt catalog.

5. Migrate the complete supported Qt catalog.
   Use the shared semantic generator to emit grouped wrappers/specs. Make package
   learnings and unified wrapper attachment demand-driven. Apply only the bounded
   compiler discovery change established in checkpoint one; enumeration must not
   fetch every callable. Verify generated signatures, annotations, descriptors,
   native mount/update behavior, and public import compatibility. Compiling a
   sparse application must leave unrelated groups cold.

6. Validate and select a measured grouping policy.
   Compare eager output with caps 1, 4, 8, and 16, using identical workloads and
   repeated fresh processes. Record actual group sizes, file count, requested and
   constructed kinds, dependency closure, cold/warm timings, retained Python
   allocations, and RSS. Keep instrumentation separate from timing probes.
   Run compiler goldens, both assembly backends, installed-package checks, the
   full regression suite, and interactive samples. Present the tradeoffs before
   choosing a default; do not infer memory savings from file count alone.

## Execution rules

Use red/green/refactor per checkpoint and commit independently verified slices.
Do not remove compatibility assertions merely to fit the new representation.
If compiler discovery forces full catalog loading, binding semantics change, or
group dependencies form cycles, stop and discuss the design rather than hide
the issue with eager fallback. No performance or memory acceptance target is
invented here: acceptance requires preserved behavior, bounded documented load
sets, and measured benefit. Any further review-loop cycle requires a separate
request; the direct focused review is not a replacement for its filed verdicts.

The first executable task is checkpoint one: consumer inventory and the two
small proofs, before changing the generator or the real Qt catalog.
