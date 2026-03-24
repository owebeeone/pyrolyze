# Mount Medusa Design

## Purpose

This document defines the "Medusa" stress suite for advert-heavy dynamic mount
behavior.

Medusa is not the first test suite to build. It is the bounded, deterministic,
high-variation suite that should come after the staged coverage in
[MountExtendedTestCases.md](MountExtendedTestCases.md).


## What Medusa Is For

Medusa should prove that the advert mechanism converges correctly under very
dramatic legal rerenders.

The key claim it must validate is:

- the same logical decision set should produce the exact same mounted graph
  whether reached by:
  - a fresh render
  - a partial rerender from a very different prior graph

That is the deepest correctness check for dynamic advert surfaces.


## What Medusa Is Not

Medusa is not:

- a fuzz test with ambient random calls during render
- an unbounded generator
- a replacement for the easy readable suites
- the first thing to implement

If the early staged suites are not already clear and stable, Medusa will only
hide problems behind complexity.


## Core Design Rule

Do **not** consume randomness sequentially inside render and hope it remains
stable.

That fails as soon as structure changes, because changed structure changes
which branches execute and therefore changes which random values get consumed.

The decision source must instead be keyed by stable decision points.

Safe choices:

- a precomputed `DecisionTable`
- a precomputed indexed "decision tape"
- a keyed PRNG lookup

Unsafe choice:

- `next(random_values)` driven by whichever branches happen to execute


## Decision Model

A sequential list is acceptable only if each entry is looked up by a stable
decision id, not by raw consumption order.

Recommended conceptual shape:

```python
@dataclass(frozen=True, slots=True)
class DecisionKey:
    cycle: int
    path: tuple[int | str, ...]
    kind: str
    ordinal: int = 0
```

```python
@dataclass(frozen=True, slots=True)
class DecisionTable:
    seed: int
    values: frozendict[DecisionKey, object]
```

Equivalent variant:

- one pre-loaded list plus an index map from `DecisionKey` to list position

What matters:

- the decision key is stable
- the same logical decision point always gets the same value
- branch churn does not perturb unrelated decisions later in the tree


## Main Domain Model

Suggested starting point:

```python
@dataclass(frozen=True, slots=True)
class TestMount:
    name: str
    key_factory: Callable[[DecisionTable, tuple[object, ...]], object]
    target_factory: Callable[[DecisionTable, tuple[object, ...]], tuple[object, ...]]
```

```python
@dataclass(frozen=True, slots=True)
class FuncEntry:
    func_name: str
    default_child_kind: str
    mounts: tuple[TestMount, ...]
```

Possible later expansion:

- accepted child kind/base
- mount interface family
- branching fan-out limit
- whether default advert is allowed


## Structural Shape

Medusa should generate a tree with:

- several container kinds
- one default mount plus `N` additional mounts per container
- different accepted child kinds across some mounts
- multiple public key interfaces
- multiple sibling routed branches
- rerender cycles driven from `use_state(...)`

The recursive builder should make decisions for:

- which container kind appears at this path
- which public mounts are advertised
- whether default is advertised
- which parent public mounts are consumed
- how many child branches are emitted
- which key interface each advert uses
- which backend target selector each public mount maps to


## Render Control

Recommended pattern:

- keep a small cycle index in `use_state(...)`
- each cycle selects one deterministic decision table
- tests can move from cycle `A` to cycle `B`
- tests can also fresh-render cycle `B` directly

This gives the critical comparison:

- fresh render of `B`
- rerender `A -> B`
- rerender `C -> B`

All three should converge to the same mounted graph when `B` is legal.


## Legal And Negative Modes

Medusa should have two bounded modes.

### Legal Mode

Constraints:

- no duplicate public advert keys on one surface
- all child attachments satisfy mount compatibility
- translated selector targets are legal for the chosen backend

Primary assertion:

- same logical decision table => same final mounted graph

Secondary assertions:

- unchanged subtrees keep prior generation
- changed branches take the new generation
- no zombie routed children remain after advert removal
- sibling insertion order is stable

### Negative Mode

Inject one deliberate rule violation at a time:

- duplicate public advert key on one surface
- incompatible child type into constrained mount
- illegal remap from compatible target to incompatible target

Primary assertion:

- stable deterministic failure


## Required Comparisons

Comparing one clean render against one rerender is necessary, but not
sufficient.

Medusa should require at least:

1. fresh render of decision table `D`
2. rerender from prior table `A` to `D`
3. rerender from very different prior table `B` to `D`
4. rerender `D -> D` for idempotence

If all four end at the same mounted graph, that is real convergence evidence.


## Suggested Seed Strategy

Do not try to cover the universe.

Use a small curated set of seeds and cycles chosen because they produce very
different legal shapes.

Suggested first-pass seed set:

- one dense seed with many adverts and branches
- one sparse seed with many missing adverts
- one remap-heavy seed
- one negative duplicate-key seed
- one negative incompatibility seed

The suite should stay bounded and explainable.


## Implementation Advice

Start smaller than the final idea.

Suggested rollout:

1. one legal seed with two container kinds and one extra mount family
2. add comparison of fresh render vs rerender to same target decision table
3. add a second very different prior graph
4. add generation assertions
5. add one negative duplicate-key seed
6. add one negative compatibility seed

Only after that:

- more container kinds
- more key interfaces
- more branching fan-out
- more selector-family shapes


## Exit Criteria

Medusa is doing its job when:

- one fresh render and two very different rerender paths converge to the same
  mounted graph for the same legal decision table
- negative seeds fail deterministically
- generation assertions still make sense to a human reading the test
- the suite remains bounded enough to debug without guessing


## Bottom Line

Medusa should be brutal in structure, not chaotic in execution.

The whole design depends on this rule:

- decisions are stable by key
- not by ambient consumption order

If that rule holds, Medusa becomes a serious convergence test for advert
correctness instead of just a noisy randomized test.
