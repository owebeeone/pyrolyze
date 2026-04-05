# Compiler Static Mount Analysis Design

## Status

This design is suspended.

It is not the current direction for the mount fuzzing system.

Reason:

- the full static analysis problem is too hard relative to its immediate value
- keyed-loop expansion, store-driven structure, and branch-selected mount/advert
  environments all push the design toward runtime truth anyway

This document is being kept only because some of its ideas remain useful,
especially:

- explicit site naming
- explicit site-kind markers
- clear separation between static site identity and runtime site instances

The live direction is now runtime / dynamic analysis. See:

- `dev-docs/DynamicMountAnalysisDesign.md`

## Purpose

This document proposes a compiler-assisted static mount analysis mode for a
constrained subset of authored `@pyrolyze` functions.

The immediate motivation is mount fuzzing:

- mount and advert routing are structurally complex
- rerender-vs-fresh correctness is easy to regress
- hand-written legality registries are likely to drift as the compiler and
  runtime evolve

The goal is to let authored shape functions remain close to normal PyRolyze
code while still generating a precise static description of:

- which mount points are available at each build site
- which mount points are advertised at each build site
- which mount-point environment is passed into nested component/container calls

That metadata then becomes the source of truth for:

- deciding which emitted classes are legal at which call sites
- generating valid fuzz cases
- explaining mount-routing failures
- keeping the fuzz system aligned with real compiler semantics

## Requirements

### 1. Special augmented analyzer function

We need a special augmented analyzer that provides mount input/output analysis
for one constrained `@pyrolyze` function.

#### 1.a Inputs

The analyzer must accept a structured description of the mount environment at
function entry.

That input must include:

- the advertised mount points currently in scope
- the available mount points currently in scope
- the current active mount selector environment
- the `mount(...)` and `advertise_mount(...)` sites already resolved upstream
  into the selector/mount values that will be in force at function entry
- container-call mount availability for any callee `ComponentRef`
  - this may come from:
    - prior analysis of that callee
    - emitted class metadata
    - generated-library mount metadata

In other words, the input is not just a flat set of mount names. It is the
current structural mount environment.

#### 1.b Outputs

The analyzer must return:

- the advertised / available mount points on function return
- the mount-point environment provided to each called `ComponentRef`

This output must be rich enough that a caller can determine:

- what mounts remain available after the function runs
- what mount environment was seen by each nested component/container call

#### 1.c Why this matters

With this information we can determine the allowed emitted classes at
`ComponentRef` call sites and at structural build points inside the analyzed
function.

This is the key requirement for mount fuzzing.

### 2. Special `@pyrolyze(...)` analysis mode

If the `@pyrolyze` decorator contains parameters, and specifically:

```python
@pyrolyze(mount_point_analyser=True)
```

then the compiler should perform a whole-function static mount analysis and
generate an auxiliary analysis function.

For now, the proposal is:

- `mount_point_analyser=True` is the first and only allowed named parameter on
  `@pyrolyze`
- this mode applies only to constrained shape/test functions intended for mount
  analysis and fuzzing

### 3. Generated analysis artifact

For an analyzed function, the compiler should generate a function that computes
the static mount analysis result.

The first proposed output shape is:

```python
dict[str, AllowedMounts]
```

but that is probably not sufficient by itself.

At minimum, the analysis result likely needs to include:

- per-site incoming mount environment
- per-site outgoing mount environment
- per-site provided mount environment for nested calls
- site kind
- whether the site is:
  - slot expression
  - slot call
  - leaf component call
  - container call
  - mount call
  - advert publication
  - keyed loop structural site

So the likely real output is closer to:

```python
dict[str, StaticMountSiteAnalysis]
```

where each site contains one `AllowedMounts` plus other structural facts.

The generated analysis function should take as input a dict of the same general
shape, typically assembled from prior analysis of upstream call sites or other
callees.

## Proposed output model

The exact names are still open, but the analysis result needs a model close to:

```python
@dataclass(frozen=True, slots=True)
class AllowedMounts:
    available_native_mounts: tuple[str, ...]
    advertised_mount_keys: tuple[object, ...]
    has_default_advertised_mount: bool


@dataclass(frozen=True, slots=True)
class StaticMountSiteAnalysis:
    site_name: str
    site_kind: str
    incoming: AllowedMounts
    outgoing: AllowedMounts
    provided_to_callee: AllowedMounts | None
    inside_keyed_loop: bool = False
    loop_site_name: str | None = None
    expands_by_key: bool = False
```

This keeps the first implementation small while still capturing the core
requirement:

- what is visible here
- what leaves here
- what is handed to a callee

We will likely need more fields later, such as:

- whether the site itself introduces a new selector scope
- whether it publishes advertisements
- whether the site is terminal or non-terminal
- whether the site requires container semantics

### Keyed-loop expansion is not a single runtime site

One important correction to the naive `dict[str, AllowedMounts]` model:

- a site inside a keyed loop is one static authored site
- but it may expand to many runtime instances

For example, a site such as `child_call` inside a keyed loop must not be
treated as one unique runtime site.

So the design must distinguish:

- static site identity
- runtime site instance identity

The static analysis output should therefore remain keyed by static site name,
but explicitly mark sites that expand over loop key space.

The likely split is:

```python
StaticSiteId = str

@dataclass(frozen=True, slots=True)
class RuntimeSiteId:
    static_site_id: str
    key_path: tuple[object, ...]
```

That gives us:

- one compiler-produced static record for the authored site
- many runtime instances for different keyed-loop paths

This is the same broad distinction the runtime already makes with `SlotId` plus
`key_path`.

So:

- static analysis should not collapse keyed-loop sites into a single runtime
  identity
- but it also should not force runtime keys into the primary static site map

The correct model is:

- `dict[str, StaticMountSiteAnalysis]` for static meaning
- `RuntimeSiteId(static_site_id, key_path)` for concrete runtime instances

This matters for:

- legality lookup
- graph attribution
- fuzz mutation targeting
- explaining why one authored site produced multiple retained runtime sites

## Constraints on analyzed functions

This mode is only practical if the authored function is constrained enough for
whole-function static analysis.

The intended allowed building blocks are:

1. slot expression
   - including:
     - `advertise_mount(...)`
     - slot-call-based ternaries like `x if y else z`
   - but only in analyzable forms

2. slot call
   - terminal

3. leaf component call
   - terminal

4. container call
   - non-terminal
   - may call a container `ComponentRef`
   - may call `mount(...)`

5. keyed loop
   - non-terminal
   - body contains further analyzable building blocks

The exact restriction set can be refined later, but the main point is:

- analysis mode intentionally accepts a limited authored subset
- this is for test/fuzz shape functions, not arbitrary application code

## Site naming

Static mount analysis is much more useful if the relevant build sites have
stable names.

We need stable names for:

- diff output
- fuzz mutation targets
- legality lookup
- correlating generated metadata back to authored shape structure

### Proposed direction

The most promising direction is to use the shape-field name or a helper derived
from it as the site name.

However, plain `CallShape` is not rich enough for mount analysis.

The shape fields need to encode more than “this is some captured call”.

The analyzer needs to know statically whether a field/site is:

- a mount site
- an advert site
- a container call
- a leaf call
- a slot call
- a slot expression

So the likely direction is:

- keep the field name as the stable site name
- add a special helper/marker type for the analysis-mode shapes that encodes the
  site kind statically

For example, conceptually:

```python
LeafSite("header", ...)
ContainerSite("body", ...)
MountSite("menu_mount", ...)
AdvertSite("body_advert", ...)
SlotExprSite("selector_expr", ...)
```

The exact API is still open, but the design requirement is:

- stable site naming must come from authored structure
- site kind must be explicit enough for static analysis
- keyed-loop expansion must be representable without overloading the static site
  name itself

## Why this is better than a hand-maintained registry

The main advantage of compiler-generated mount analysis is that it becomes the
authoritative source of truth for the constrained shape functions themselves.

That means:

- if the authored shape changes, the analysis changes with it
- if the compiler lowering changes, the analysis still tracks the compiler’s
  current understanding
- the fuzz harness does not need a second manually synchronized legality model

Backend compatibility still comes from backend metadata. Static mount analysis
does not need to answer:

- which exact emitted class fits a mount point

Instead it answers:

- which mount environment exists at each site
- what environment is passed to each nested call

Then backend metadata can answer:

- given that environment, which emitted classes are compatible

## Initial implementation target

The smallest useful first step is:

1. support `@pyrolyze(mount_point_analyser=True)` for a very small authored
   subset
2. generate per-site analysis metadata for:
   - incoming mounts
   - outgoing mounts
   - provided-to-callee mounts
3. require stable named sites in analysis-mode test shapes
4. use that metadata to drive one first mount fuzz harness

That is enough to prove the architecture before broadening the supported syntax.
