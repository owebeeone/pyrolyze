# Lazy Native Backend Loading Plan

Status: Qt and Tk grouped loading implemented; current acceptance and measurements are
recorded in [the implementation plan](LazyNativeBackendLoadingImplementationPlan.md).
Historical review scope below is unchanged. DearPyGui remains a separate follow-up.
Recorded: 2026-10-10. Source inspection began at Pyrolyze
`87db47160f845e9b3633163c214f0b0fad76a2ec`, with existing local work present.
All source paths below are relative to the Pyrolyze repository root.

This supplements `dev-docs/LazyLoadingOptimizationRequirements.md`. The first
deliverable is widget-level loading of the generated PySide6 catalog, with
explicit callable signatures preserved across the whole supported catalog.
Member-level loading and broad metadata compaction remain outstanding requirements,
not acceptance criteria silently declared complete by this checkpoint.
`dev-docs/RenderingBackendBugList.md` item 6 and
`dev-docs/RenderingBackendDiscussionReport.md` keep this optimization separate
from reconciliation fixes, toolkit layout costs, and lifecycle adoption.

Draft isolation: GWZ local cloning from the main workspace was attempted but
refused with `UnsupportedSourceLayout` for submodule Git files/external metadata;
no clone was reserved. This document is staged outside the live checkout for
review and deliberate placement at `dev-docs/LazyNativeBackendLoadingPlan.md`.
No source-layout conversion or lifecycle work is part of this proposal.

## Source-confirmed loading paths

| Path / symbol | Observed cost or constraint |
| --- | --- |
| `pyrolyze_tools/generate_semantic_library.py`: `generate_library_source`, `_render_widget_specs`, `_render_widget_method` | Qt/Tk emission puts every `UiWidgetSpec`, nested member descriptor, manifest entry, selector, and explicit reactive classmethod into one marked module. |
| `src/pyrolyze/backends/pyside6/generated_library.py`: `PySide6UiLibrary` | Class-body execution constructs the whole `WIDGET_SPECS` dictionary; wrapper definitions all execute on import. The inspected file has 49,950 lines. This is source size, not measured time or retained memory. |
| `src/pyrolyze/import_hook.py`: `_PyRolyzeLoader.exec_module`, `_resolve_artifact`, `source_to_code`; `src/pyrolyze/importer.py` | The marked module is transformed as a module. Persistent artifacts and Python bytecode can avoid some compilation work, but execution still constructs its descriptors and wrappers. Factories inside the same giant marked source would still leave parsing/transformation and wrapper construction eager. |
| `src/pyrolyze/backends/pyside6/__init__.py` | Importing any child module first executes package imports of engine, generated library, and the large `LEARNINGS` table. Generation-time learnings are an additional eager payload independent of runtime specs. Tk's package initializer has the same generated-library/learnings pattern. |
| `src/pyrolyze/api.py`: `ui_interface`; `src/pyrolyze/backends/model.py`: `UiInterface`, `UiInterfaceEntry` | The decorator binds the manifest owner, without scanning methods. The current manifest contains only public name/kind pairs; it does not supply parameter/event facts to the compiler. |
| `src/pyrolyze/compiler/kernels/v3_14/rewrite.py`: `_collect_imported_annotated_symbols` | For every imported UI class, it loops over every manifest entry, calls `getattr`, `inspect.signature`, and runtime type-hint resolution. A lazy attribute resolver alone would load the full catalog during compilation. Broad exceptions elsewhere in import discovery must not silently turn a known lazy-load failure into missed compiler recognition. |
| `src/pyrolyze/unified/__init__.py`, `unified/factory.py`, `unified/qt.py`: `_register_structural_component_refs` | Unified module exports already use module `__getattr__`, and the factory imports only the selected adapter. However, Qt adapter startup loops over the native manifest and attaches every wrapper. This must become demand-driven while retaining `QtUx.CQ*` and native callable identity. |
| `src/pyrolyze/pyrolyze_native_pyside6.py`: `create_host`; `backends/pyside6/engine.py`: `PySide6WidgetEngine.__init__` | Host startup imports the generated catalog and passes `WIDGET_SPECS` into the engine. It creates/reuses `QApplication`; this is a real host resource, separate from catalog realization. |
| `src/pyrolyze/backends/mountable_engine.py`: `__init__`, `_spec_for`, `_mountable_type_for`, `_create_mountable` | Engine construction stores a `Mapping` without enumerating it. `_spec_for` uses `.get(kind)`; native types already use import-and-cache lookup. Actual widget construction occurs later in `_create_mountable`. This gives a usable lazy-spec boundary without changing mounting algorithms. |
| `pyrolyze_tools/dearpygui_emit_library.py`: `render_generated_library_py`; `backends/dearpygui/generated_library.py`, `__init__.py`, `author_ui.py` | DPG emission eagerly defines generated `M_*` adapter classes and specs; package startup attaches the existing curated `DearPyGuiUiLibrary.C` author surface. Adapter constructors call the active host to create native items; defining their classes is not item creation. |

Distinguish three stages in all measurements and diagnostics: (1) constructing
Python wrappers/spec metadata, (2) importing the toolkit and its annotation or
base types, and (3) creating live widgets/host resources. Qt engine/host imports
already need `PySide6.QtWidgets`; sharding cannot remove that native binding cost
when the host or a widget needs it. No timing profile was run for this design,
and source-confirmed eagerness does not establish the dominant startup bottleneck.

## Generated boundaries and three surfaces

Use ordinary importable Python modules, not a new plugin system, binary metadata
format, runtime reflection discovery, or a second transform cache.

```text
Before: src/pyrolyze/backends/pyside6/
  generated_library.py       # manifest + all specs + all CQ* methods
  learnings.py               # eagerly re-exported by package initializer

After (proposed): src/pyrolyze/backends/pyside6/
  generated_library.py       # stable compatibility re-export; no generated payload
  generated_library.pyi      # stable explicit re-export of the generated facade type
  _generated/__init__.py     # empty; never imports shards
  _generated/facade.py       # public class, mounts, UI_INTERFACE, WIDGET_SPECS
  _generated/facade.pyi      # explicit classmethod signatures, for static tools
  _generated/index.py        # public name / kind -> module, families, generation stamp
  _generated/names.json      # per-kind member-name/family lists; tooling reads on request
  _generated/q_label.py      # marked source: QLabel spec + explicit CQLabel method
  _generated/q_push_button.py
  _generated/q_hbox_layout.py
  _generated/shared/widget_base.py  # only genuinely shared definitions
  _loading.py               # backend-owned attribute resolution and spec Mapping
```

Revision after the GO/GO review: configurable grouped shards replace the fixed
one-kind default. This amendment needs focused review; the previous verdicts
apply to the earlier committed design, not this grouping policy.

The offline generator accepts a positive maximum kinds-per-module setting.
One is supported, but the production default remains undecided until measurement.
Keep each kind's full member metadata together. Use explicit family assignments
and stable kind ordering to partition families into bounded groups; do not depend
on discovery order or runtime reflection. Record configuration, group membership,
and dependency closure in the generated index and generation stamp. Identical
input and configuration must produce byte-identical output. The per-kind filenames
above illustrate size one; grouped output uses deterministic group filenames.

Resolving any member imports and constructs every definition in its group, plus
declared dependencies. This is intentional co-loading, not per-kind laziness.
Record the full load set in the index and acceptance fixture. Keep unrelated
families separate; shared helpers remain separate and do not count as kinds.
Do not group all `QWidget` subclasses, all controls, or all layouts together merely
because they share native ancestry. Native inheritance does not require loading
the ancestor's Pyrolyze wrapper/spec. Start with distinct label, push-button, and
layout groups for the dependency proof; unrelated chart/designer/dialog
definitions must remain cold.

| Surface | Proposed responsibility |
| --- | --- |
| Author-facing | Keep `PySide6UiLibrary as Qt`, `Qt.CQLabel(...)`, `with Qt.CQMainWindow(...)`, `Qt.mounts.*`, and `QtUx.CQ*`. Tk keeps `TkinterUiLibrary.C*`; DPG keeps the existing curated `.C` forms when migrated. No replacement generic callable or extra public per-shard API. |
| Registration/tooling | The generated index explicitly registers supported public names, kinds, shard paths, direct shared dependencies, and generation compatibility. `UI_INTERFACE` remains the owner-bound name/kind manifest. Name-only tooling reads the manifest or per-kind name data, never wrapper attributes. |
| Runtime-only | `_loading.py` supplies cached attribute resolution and a read-only `Mapping[str, UiWidgetSpec]` for `WIDGET_SPECS`. Shards export one ordinary resolved spec and an internal class carrying the existing generated method. These are implementation helpers, not application authoring APIs. |

The top-level index contains strings and small immutable records, not closures
over expanded metadata, function bodies, `inspect.Signature` objects, or all
inherited parameter sets. Use public-name and kind indexes pointing at the same
entry. Per-kind member names live in a generated tooling sidecar so availability
inspection need not build specs, and importing the facade need not decode the
full member catalog. The loader imports only the indexed module using
`importlib.import_module`; it never walks a package with `pkgutil` or `dir`.

Keep `#@pyrolyze` in the first two lines of every shard containing reactive
methods. The facade, index, shared metadata modules, and loader need no marker
unless they contain reactive definitions. Leave checked-in artifacts as authored
source, never transformed output. The existing import hook transforms only the
requested small shard and preserves packed tail-`kwds` lowering.

Keep every replaceable generated artifact under the single `_generated/` root,
including the facade, stubs and inventory. The public `generated_library` module
and stub are stable re-export shims, not per-generation artifacts. Authors keep
the same import path and class identity through these re-exports; loading the
small generated facade must not import widget shards. Establish the shims once
as a normal reviewed source migration, not during later catalog regeneration.

The generated method keeps its full explicit parameters, positional/keyword-only
shape, annotations, defaults (`MISSING` versus `...` included), handlers and
boundary coercions. Do not synthesize a generic `*args, **kwargs` callable and
attach an artificial signature. Emit the `.pyi` facade from the same parameter
model so IDEs see the full API without importing shards.

For the first Qt prototype, retain the internal class name `PySide6UiLibrary`
inside each shard so class-qualified metadata and private `__element` lookup do
not change accidentally. The public facade retains the small `__element` helper.
On first class attribute lookup, a small metaclass resolver imports the shard,
gets its raw classmethod descriptor, binds it to the public facade once, and
caches that bound callable on the facade. Preserve `cls` binding, component
metadata, signature/type-hint resolution and packed-call behavior in a focused
proof before adopting this mechanism. Do not publish a bound method belonging
to a different owner or rebuild callable refs at every lookup. `QtUx` forwards
to this same cached callable; its manifest stays bound to the unified class.
If this cannot preserve the existing compiler/runtime contract, stop for review.

## Triggers, dependency closure and identity

```python
# Existing author syntax, unchanged; compile this component as today.
from pyrolyze.api import pyrolyze
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt

@pyrolyze
def caption() -> None:
    Qt.CQLabel("Ready", enabled=True)
```

```python
# Registration/runtime inspection, not an alternative author callable surface.
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt

known_kinds = tuple(Qt.WIDGET_SPECS)       # names only; no widget shards
label_spec = Qt.WIDGET_SPECS["QLabel"]   # load q_label and declared shared dependencies
assert Qt.WIDGET_SPECS["QLabel"] is label_spec
label_callable = Qt.CQLabel             # same shard; no second definition
assert Qt.CQLabel is label_callable
```

First reference means an actual qualified wrapper resolution, including the
compiler's resolution of a referenced imported member. First mount means the
engine requests a kind through `WIDGET_SPECS.get`, including unified leaves that
emit `UIElement(kind="QLabel", ...)` without touching `CQLabel`. Explicit
per-widget descriptor/signature introspection loads the same shard. With the
first widget-level layout, any of these loads both that widget's spec and method;
splitting those within a widget is later work. No widget instance is created by
spec or method resolution.

Each shard imports only its actual shared metadata/helper modules and native
types required by its signature or runtime definition. Shared modules must not
import widgets, their facade, learnings, or a full registry. Annotation type
imports may load toolkit modules, but must not load the corresponding Pyrolyze
widget definitions. Emit explicit direct dependencies in the index and check
that shared-fragment imports form a DAG. No live reflection or widget probing
at runtime; generator discovery/probing remains an offline regeneration cost.

`sys.modules` is the module cache. Each shard constructs one immutable spec and
its descriptors per indexed kind at module execution. The facade caches each
requested bound callable, and
the spec mapping retains that same spec. Engines/hosts share definitions, but
keep their native object/type caches and mount state as today. Key caches by
backend module and kind/public name, not by render, host, props, or lifecycle
generation. Return cached structures on warm lookup without merging fragments
again; native object construction remains per mount.

Serialize first resolution/publication with a small backend-owned reentrant
lock and a resolution-in-progress check, using Python import locking for module
execution. Validate every indexed member of a loaded group before publishing any
of its specs or callables through the facade or spec mapping. A malformed member
fails the whole group; no valid sibling may escape through a partial cache.
Cache the group failure consistently with requested-member diagnostic context,
without retaining tracebacks. Unrelated groups remain usable. Successful imports
may remain in Python's module cache, but do not prove validated publication.
Test a group containing one valid and one malformed member, subsequent sibling
requests, concurrent resolution, and an unaffected unrelated group. Reentrant cycles
report the requested dependency chain; concurrent lookups must return identical
published objects. Loading never creates GUI resources and does not relax toolkit
thread rules. No production reload/invalidation API in slice one: regeneration
requires a fresh process. Any future invalidation needs an explicit live-mount
contract; import-hook cache invalidation alone cannot safely replace live specs.

## Preventing accidental catalog realization

- `WIDGET_SPECS` implements `__iter__`, `__len__`, containment and key views from
  the index. `__getitem__`/`.get` resolve one kind by loading its entire group
  and declared dependencies. `.get` defaults only for an
  unknown key; it must propagate failures for a known entry. `.values()`,
  `.items()`, and `dict(WIDGET_SPECS)` explicitly traverse resolved values and
  may load the catalog when consumed. Startup/registration code must not use them.
- `UI_INTERFACE` enumeration and `dir` on the author facade advertise names
  without loading them. `inspect.signature(Qt.CQLabel)` loads its widget group.
  Full `inspect.getmembers(Qt)` or explicit consumption of all spec values is
  deliberate full introspection and may load all definitions; document that
  distinction. Documentation generation consumes discovery/name artifacts
  offline rather than requiring a full live catalog import.
- Package initializers must expose engine/library/learnings through selective
  module attribute loading, following `unified/__init__.py`. Keep `LEARNINGS`
  available on explicit access without importing it during normal runtime
  registration. Shard package initializers must be empty.
- The Qt generated facade's `__all__` exports the facade/support names, not
  individual widgets. Star import must not walk widget attributes. Audit package
  re-exports so star importing a Qt package may obtain its exported helpers but
  does not realize the widget catalog. Do not use star imports between shards.
- Replace unified Qt's attachment loop with selective class/instance forwarding;
  import/factory construction copies only manifest and mounts, never methods.
  Plain unified leaf emission stays as today and resolves a spec on first mount.
- Keep host initialization's existing mapping handoff; no conversion to
  `frozendict`, `dict`, or prewarming every kind. Engine startup already stores
  the mapping and needs no generic engine rewrite.

**Stop-and-discuss compiler decision:** the current imported-symbol collector
requires a bounded recognition change. Proposed route: identify actual
qualified member references in the authored AST for each imported UI alias and
inspect only those manifest members, then reuse the existing signature/hint
recognition and lowering. Cover calls, `with`, event arguments, member-value
aliases and nested functions; preserve existing fallback for ordinary imported
non-UI symbols. Never use "cannot statically resolve" as permission to enumerate
the whole catalog. Dynamic attribute access must retain its existing recognition
or existing diagnostic behavior, proven before implementation. An alternative
compact signature manifest is possible but would expand the shared registration
contract and risks duplicating compiler facts; it is not implicitly approved.
Approve the exact recognition boundary before changing `rewrite.py`, and stop
again if public source behavior or runtime metadata would change. A backend-only
loader cannot meet compilation acceptance without resolving this decision.

## Diagnostics and generated artifact consistency

Use the existing exception/diagnostic conventions with context fields/messages;
do not invent passive error tags or a new error-code enum. Distinguish unknown
kind/name (index miss, preserving existing unsupported-kind or attribute errors),
known widget with unavailable member (per-kind metadata/validation error), missing
or malformed shard/spec (generated artifact error), and unsupported toolkit
version (compatibility error). Include backend, kind, requested member if any,
indexed module, generation stamp and chained cause. Never silently fall back to
full discovery or return `None` for a known broken definition.

Record the toolkit generation version and supported range plus generator/schema
revision; do not reject every patch version without evidence of incompatibility.
Validate index/shard stamps and spec kind/dependencies at first use, before native
construction. Cache deterministic first-use failures as lightweight failure
records so a repeated request reports the same attributable problem without
rebuilding or retaining tracebacks. Failed module imports may leave successful
shared imports cached; never publish a partial widget or invalidate other kinds.
Fixing installed artifacts requires a fresh process in slice one.

Generator changes belong in `pyrolyze_tools/generate_semantic_library.py` and its
writer. Keep discovery/learnings as the source of truth and produce a sorted
multi-file artifact set: facade, index, shards, name data, stubs and generation
inventory. Stable filename assignment must handle existing kind/public-name
collisions rather than recomputing names independently per shard. Regenerate to
an empty sibling staging directory and validate the complete set before promotion.
Require the generator to exit successfully and complete-inventory validation
to pass; successful exit alone is not proof that every artifact is present.
Promotion is an exclusive offline maintenance operation, never a live runtime
update: stop processes using the destination and exclude imports, builds,
packaging and concurrent writers until promotion or recovery completes.

Promotion moves directories, never copies files over the existing catalog.
Use same-filesystem sibling paths and refuse unexpected backup/pending state.
Before renaming anything, record the validated old and candidate inventory
identities in a promotion marker outside both directory roots. Rename the old
`_generated/` directory to the retained backup, then rename the complete staging
directory to `_generated/`. Do not describe these two renames as one atomic
swap: there is an interruption window with no active directory. Validate the
promoted inventory before removing the marker and admitting imports or builds.
The generated root contains only owned output; stale shards disappear with the
whole old directory. Unrelated handwritten files remain outside this root.

On any promotion error or restart with a pending marker, restore the complete
old directory before retrying: if it is still active, leave it intact; if it is
in the backup location, move any candidate active directory aside and rename
the backup to `_generated/`. Validate the old inventory before clearing the
marker. Recovery is idempotent; keep the marker and backup if restoration or
validation fails, report the failing operation, and prohibit destination use.
For first generation with no old catalog, failed promotion returns to an absent
destination, which is not admitted for import or packaging; retry from a newly
validated candidate. Never delete the retained old generation until candidate
validation and marker clearing succeed. Backup cleanup failure after admission
does not invalidate the complete new catalog; it prevents another promotion
until the backup is safely cleaned under the same exclusive access.

Build/package entry points reject a pending marker, absent required catalog or
incomplete/mixed generated inventory. Imports during maintenance are unsupported;
after restart, the maintenance operator must recover before starting consumers.
Runtime stamp checks remain defense in depth, not recovery. This is a bounded
offline directory-promotion contract for process interruption and filesystem
errors, not live update support or a power-loss durability claim. Prove the
writer and packaging admission checks in slice 1 before catalog migration.

No timestamps,
absolute paths or hand-maintained signature copies. Two runs with pinned
Python/toolkit/generator/learnings inputs must have identical bytes and inventory.

Packaging follows `pyproject.toml`'s `src` package discovery: every generated
package has `__init__.py`; explicitly include JSON name data and `.pyi` artifacts
in wheel/sdist configuration. Ship authored shard sources so the existing import
hook works from an installed wheel. Verify ordinary installed wheel and sdist
installs outside the checkout, with pytest plugin and supported Python startup
hook setup (`pyrolyze-import-hook-pth`). Editable checkout success is insufficient.
Frozen/zip deployments require a separately declared support scope, not an
unverified dynamic-import claim; list indexed modules for such future packagers.

Later compaction should start with exact shared fragments, not canonicalizing
names by spelling alone. Family fragments carry full descriptor semantics;
merge explicitly ordered families, then widget-local additions/overrides and
exclusions. Conflicting family definitions require an explicit local override;
excluding an absent member is a generation error. Preserve annotations, defaults,
accessors, source prop groups, modes, coercions, events, mount routing and identity
flags. Cache the final ordinary spec, never merge on updates. Initially keep
widget-local expanded data wherever equality/reuse is unproven. The optional
`shared/widget_base.py` boundary is for verified sharing, not a prerequisite
broad compaction campaign or a claim that R2 is complete.

## Bounded implementation slices and coverage

Future implementation follows AGENTS.md red/green/refactor and full regression
rules. This document adds no tests or implementation. Do not edit lifecycle
plans, gates, ownership, completion queues, render scheduling or dirty tracking.
Any need for a shared runtime contract change is another stop-and-discuss gate.

| Slice | Scope and exit evidence |
| --- | --- |
| 0: decisions and baseline | Approve the imported-symbol recognition boundary, cached classmethod binding proof, and `WIDGET_SPECS` concrete-type compatibility. Inventory consumers and collect the measurements below. Tests currently assert `frozendict`; switching to a read-only `Mapping` must be a recorded representation decision, not merely weakening assertions to make tests pass. |
| 1: generated dependency proof | Use the existing fake-widget generator fixture to emit two related widgets plus an unrelated family into separate modules. Prove index-only startup, declared dependency closure, ordinary specs, explicit signatures, stable identities, deterministic errors, and byte-reproducible regeneration. Prototype backend-local loading before widening to the real catalog. |
| 2: Qt catalog and integration | Migrate all supported Qt kinds into shards, keeping signatures and names; close package/learnings and unified attachment eagerness. Apply only the approved bounded compiler recognition change. Native host startup, compiling a one-widget application and first mount must avoid unrelated definitions. A partially sharded catalog is not final Qt acceptance. |
| 3: distribution and acceptance | Exercise installed wheel/sdist paths, import-hook cache states, compiler goldens, canonical render/update coverage and the configured supported runtime matrix. Record timings/memory/load sets and practical tradeoffs before claiming an optimization. |
| Later, separate | Tk generator support; DPG shard emission and adapter-class exports; member-level loading; broad metadata factoring. UIKit or other future backends reuse index/import/spec boundaries when needed, without becoming first-slice dependencies. |

Tk can use the same emitter structure with `CButton`, `CFrame`, etc., its native
type names and mount selectors. DPG keeps its separate emitter and curated author
forms: split generated factory classes with their specs and load only required
`items.py` helpers. Preserve `mounted_type_name` compatibility through selective
module `__getattr__` exports where needed. DPG currently exports every generated
`M_*` class in `__all__`: preserving that star-import shape while avoiding every
class load needs an explicit compatibility decision before the DPG slice. Do
not silently remove exports or add proxy classes. No Qt-only assumptions in
the index/mapping pattern, and no speculative native bridge/ABI abstraction now.

Canonical acceptance extends existing harnesses rather than duplicating render
success paths in bespoke units:

- `tests/test_generate_semantic_library_tool.py` owns the generator fixture;
  capture the complete generated file inventory/content as its canonical output.
  Extend `tests/test_generated_backend_libraries.py` to validate every shard's
  authored-source marker, no compiled output, signatures and ordinary spec data.
  Full catalog introspection here is deliberate; keep cold-load checks isolated.
- Add one authored imported-UI fixture to `tests/data/gold_src/` and
  `tests/data/gold_cases.toml`, with output in `tests/data/v3_14/goldens/`.
  Run `tests/test_ast_goldens.py` and preserve the existing
  `phase7_ui_interface_kwds_native_wrapper.py` packed-call fixture. Imported alias,
  qualified calls/containers and handler recognition must retain equivalent
  lowering and source errors. Narrow recognition failures belong in compiler
  unit coverage; do not duplicate successful render assertions there.
- A fresh-process load-state fixture records import, enumeration, compilation,
  single-widget lookup, first mount, repeat lookup and repeated render phases.
  Assert zero widget shards after backend import/host creation; after a request
  assert exactly that shard plus its declared dependency closure. Include an
  unrelated family, two related widgets sharing dependencies, and unified/native
  alias identity. Measure full-introspection behavior separately. Existing pytest
  module imports eagerly warm many backends, so in-process test order is not a
  valid coldness proof.
- Use `tests/test_pyside6_native_host.py`,
  `tests/test_examples_grid_app_pyside6_native.py` and existing
  `tests/unified/` render/reference-shell coverage for unchanged prop omission,
  events, mounts, identity and retained-object updates. Prefer canonical generic
  backend fixtures for toolkit-independent outcomes. Do not claim to fix the
  documented nested-layout ordering defect or change expectations for it here.
- Narrow loader tests cover unknown kinds, unavailable members, wrong generation
  stamps, absent files, malformed metadata, incompatible toolkit versions,
  dependency cycles, concurrent first requests and deterministic repeated errors.
  Reuse `tests/test_import_hook_cache.py` and
  `tests/test_importer_cache_fingerprint.py` for cache fingerprint mechanics.
- Generator promotion tests inject interruption and filesystem errors before
  and after each directory rename and marker transition, including recovery
  failures and repeated recovery. Verify the marker blocks build/package
  admission until recovery or candidate validation completes; recovery yields
  exactly the old complete owned set, or successful promotion the new complete
  set, never an admitted mixture. Check unrelated files remain byte-identical,
  retry succeeds, and a fresh-process one-widget lookup plus package-inventory
  validation succeeds after admission. Include failures before marker creation
  and during final validation/marker clearing, first-generation promotion and
  post-admission backup cleanup. Prove failed generator exit never promotes
  output. The writer must demonstrate this
  contract in slice 1 before slice 2 can replace the real catalog.
- Distribution verification builds wheel/sdist, inspects inventory, installs in
  fresh environments and repeats the same one-widget fixture there. Run the
  configured matrix through `tests/versioned_test_harness.py`; regenerate goldens
  only after reviewing why output changed. No timing thresholds in correctness
  tests and no acceptance by bytecode-cache warmth alone.

## Reproducible measurements

Create a future contributor measurement entry point with fixed scenario arguments
and JSON output; no benchmark was implemented or executed for this draft. Run
baseline and candidate from recorded revisions using the same toolkit/interpreter,
OS, hardware, environment, startup-hook setup, dependency builds, GC policy and
sample count. Report distribution (median and spread), raw records and command
lines, not a single favorable sample or invented speedup target.

| Scenario | Measurement boundary and cache state |
| --- | --- |
| Cold backend import | Fresh process for every sample: import facade alone; separately import selected unified adapter and create host. Use `PYROLYZE_ENABLE_CACHE=1` with a separate empty `PYROLYZE_CACHE_DIR` and absent ordinary bytecode for the cold-transform set. Then run fresh-process samples with deliberately primed transform and bytecode caches for the warm-cache set. Also record the default in-memory artifact-cache setup. Fresh process is essential in all sets; warm disk cache is not warm definitions. |
| First use | In a fresh process after timed facade import, separately time first `CQLabel` reference/signature inspection, first spec lookup and first native mount. Alternate their ordering in separate scenarios because the first trigger warms the widget for the others. Include label+button and a layout shell; report authored-module compilation separately to expose compiler-driven loading. Host/application creation and toolkit import have distinct spans. |
| Repeated use | In the same process after first use, time repeated cached lookups, repeated mounts and retained-node updates separately. Verify no extra shard loads or spec/descriptor reconstruction. Do not fold native allocation/layout/event pumping into a claimed resolver-only gain. |
| Deliberate catalog introspection | Fresh-process full spec traversal and full callable inspection, reported as their own workload. Capture any cost moved from startup to full inspection. |

At every phase record loaded generated modules from `sys.modules`, resolved kind
and shared-definition counts, source/transformed byte totals where available,
and identity checks. Measure Python allocations/peak with `tracemalloc` in a
separate instrumented run and process current/peak RSS with an OS-appropriate
method (record units and tool); toolkit native allocations are not fully visible
to `tracemalloc`. Record memory deltas from a pre-import checkpoint, not merely
peak RSS for the entire process. Use `perf_counter_ns` spans for wall time;
instrumented load/transform accounting may need separate runs to avoid skew.

Compare the eager catalog with group-size candidates such as 1, 4, 8, and 16,
using identical sparse and representative application workloads. Report the
configured cap, actual group sizes, module count, constructed versus requested
kinds, dependency loads, cold/warm timing, and retained Python memory and RSS.
Add generator coverage for deterministic grouping, same-group co-loading,
cross-group isolation, and unchanged callable/spec identity under concurrent
and reentrant resolution. The cap is a definition-count bound, not a memory bound.
Choose the default from measured file-count, first-use, and memory tradeoffs;
do not promise proportional memory savings or reduced Qt native-library memory.

Python-cold import is not a claim of cold filesystem/OS caches. Label that state
honestly. Keep visible-window layout/paint/event-pump measurements separate from
metadata startup; nothing here attributes existing GUI slowdown to catalog size.
Acceptance requires bounded load sets and semantic/package parity first, then
published evidence of the actual startup/first-use/memory tradeoff.

## Decisions to close before implementation

1. Approve the bounded compiler reference-selection change and prove alias,
   container, handler and dynamic-reference compatibility; otherwise stop.
2. Accept the read-only lazy mapping representation for `WIDGET_SPECS`, preserving
   resolved-value semantics, and verify cached descriptor binding preserves the
   author/compiler contract. Any runtime contract expansion requires discussion.
3. Pin regeneration toolkit versions/compatibility policy, first-use error
   presentation, and distribution targets for the Qt checkpoint. DPG star-export
   compatibility and member-level compaction decisions can wait for later slices.
4. Resolve GWZ cloning support for this workspace layout before adopting a clone
   as an integration vehicle; move this standalone draft into the live repository
   only deliberately. Lifecycle integration continues independently.

This plan changes no backend, generator, compiler, runtime, lifecycle or tests.
