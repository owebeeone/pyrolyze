# Mount Advert Plan 03: Hydo Graph Stability And Stress

## Purpose

This plan verifies the finished advert-routing mechanism under large structural
variation using the Hydo test backend.

The required proof is stronger than "it seems to work once."

We want:

- dramatic mount and structure variation
- exact graph equality between equivalent passes
- exact graph equality between first pass and rerun for the same logical input
- clean detach/reattach behavior when advert structure changes legally


## Inputs

- [01_Api_And_Mount_Restructure.md](01_Api_And_Mount_Restructure.md)
- [02_Advertise_Mount_Implementation.md](02_Advertise_Mount_Implementation.md)
- [MountAdvertsDagBuilder.md](../MountAdvertsDagBuilder.md)


## Scope

This phase covers:

- Hydo-based graph snapshot tooling if needed
- exhaustive rerender equivalence checks
- high-variation nested advert scenarios
- graph cleanup/detach assertions

This is the phase that proves the advert DAG builder is stable, not merely
functional.


## Core Verification Claim

For any legal input tree:

- pass 1 builds graph `G1`
- rerunning with logically identical input builds graph `G2`
- `G1 == G2`

And for legal changed input:

- only the expected routed edges, anchor placements, and mount states differ
- removed adverts and removed consumers detach cleanly
- unchanged subgraphs retain stable identity where intended


## Required Code Changes

## 1. Hydo Graph Snapshot Helper

Files:

- [src/pyrolyze/testing/hydo.py](../../src/pyrolyze/testing/hydo.py)
- or a dedicated test helper module under `tests/`

Required behavior:

- deterministic serialization of mounted graph shape
- include:
  - node kind
  - slot identity
  - routed parent identity
  - anchor placement identity
  - translated selector identity
  - ordered child placement

This helper should be cheap and explicit. Do not rely on reprs of live objects.


## 2. Exact First-Pass vs Rerun Equivalence Tests

Files:

- `tests/test_hydo_mount_advert_graph.py`

Required cases:

- identical tree rendered twice without changes
- identical dynamic key objects recreated but semantically equal
- identical advert/default configuration rebuilt through rerender

Assertion shape:

- exact graph snapshot equality
- exact routed-edge equality
- exact mount-state equality where exposed


## 3. Dramatic Structural Variation Matrix

Files:

- `tests/test_hydo_mount_advert_graph.py`
- possibly `tests/test_generated_hydo_mountable_engine.py`

Required cases:

- nested re-advertise through two or more wrapper layers
- parameterized `cell(row, column)` family growing and shrinking
- default advert moving from one anchor site to another
- advert family disappearing entirely
- consumer subtree disappearing while provider remains
- provider remains while consumers reorder
- mapping one public key to one backend selector, then to another legal backend
  selector on rerender
- mixed native selectors and advert selectors in one consumer list


## 4. Cleanup And No-Zombie Assertions

Files:

- Hydo graph tests
- existing generic mount engine tests if appropriate

Required behavior:

- removed consumers are detached
- removed adverts do not leave routed ghost edges
- removed routed anchors do not retain stale placement state
- repeated rerenders do not accumulate duplicate advert dependencies


## Test Plan

Target: about `14` tests.

Suggested files:

- `tests/test_hydo_mount_advert_graph.py`
- `tests/test_mount_advert_hydo_regressions.py`

Coverage groups:

- exact equality first pass vs rerun
- legal change matrix
- cleanup/no-zombie checks
- mixed native + advert routing
- nested wrapper re-advertise


## Exit Criteria

- Hydo can serialize advert-routed graphs deterministically
- first pass and rerun of equivalent input produce exactly the same graph
- dramatic legal rerender changes only change the expected graph regions
- no stale advert edges or ghost nodes remain after removals
- the advert system is proven stable enough for real toolkit rollout
