# Architectural Decision Review Triggers

## Purpose And Status

Proposed review practice, with Pyrolyze lifecycle as the first worked case.
This document does not change repository instructions, authorize a rewrite, or
interrupt the current lifecycle integration.

The aim is to recognize decisions whose consequences extend beyond the current
task. A change can pass its tests while making future features require repeated,
coordinated edits across the system. That is a reason to review the representation,
not proof that the implementation is wrong.

## Trigger: One State Concept, Several Transition Paths

> When adding or changing one state concept requires restating its policy across
> several lifecycle transitions, pause feature expansion and review how that
> policy is represented.

The important signal is not the number of files or methods touched. It is that
correctness depends on remembering the same semantic rule in separate places:
initialization, staging, publication, rollback, invalidation, or resource release.

Calling one authoritative policy from several paths is different from manually
reimplementing that policy in each path. Likewise, genuinely different domain
actions should not be combined merely because their code looks similar.

The first question is:

> If we add one field, where must we remember to specify what happens to it on
> success, failure, retry, and retirement?

## Worked Case: Pyrolyze Lifecycle

### First Review Point: Repeated Context Bookkeeping

By 2026-03-24, revision `940b74b` already shows separate staging, commit,
rollback, and deactivation machinery in `src/pyrolyze/runtime/context.py`.
Examples include synchronous and asynchronous effect bindings, mount
advertisements, callback selection, and structural scope passes.

For example, an effect's `staged_request` is set during staging, consumed and
cleared during commit, and cleared separately during rollback and deactivation.
Other owners express related lifecycle policies through their own methods.
Not every operation is interchangeable, but the cross-cutting concern is visible.

This is a defensible early review point, not a claim to have found the first
possible warning. The question available then was whether lifecycle policy
belonged in each context implementation or in an explicit reusable model.
It was not yet a reason to predict YIDL or Astichi.

### Second Review Point: Centralization Without Composability

Revision `bbebfeb`, dated 2026-04-08, introduced the declarative lifecycle
prototype and migration plan. The initial `src/pyrolyze/lifecycle.py` was 542
lines. By revision `d21d390`, dated 2026-04-13, it was 4,124 lines, including
field-kind hierarchies, generated helpers, facade dispatch tables, factories,
hooks, and transaction machinery.

The growth is context, not a failure threshold. The stronger warning is that
moving behavior into a central engine does not by itself make interacting
policies composable. Field kind, storage, facade access, initialization,
conversion, inheritance, and transaction phase can still require coordinated
special cases.

The original [lifecycle proposal](history/legacy-lifecycle/ContextLifecyleMetaprogramming.md)
already recognized the need to declare field policies and optimize them
centrally. The [migration plan](history/legacy-lifecycle/ContextLifecyleMetaprogrammingPlan.md)
explicitly prohibited a parallel handwritten lifecycle mechanism. The later
problem was therefore not simply failing to notice duplication; it was whether
the chosen implementation could express and combine those policies sustainably.

The second review question was:

> Have we made each rule authoritative in one place, or merely moved the places
> that must agree into the same module?

## What To Do When The Trigger Fires

### 1. Write The Rule Before Extending The Machinery

Choose one concrete state concept and describe its transitions in a small table:
what is initialized, what becomes provisional, what publishes, what discards,
and what requires cleanup. Identify the completion owner separately from local
scope exit. Record any unresolved semantics rather than assuming them.

Map each rule to its current implementation sites. Mark where policy is
duplicated, where a path delegates to an authoritative implementation, and where
an action is genuinely domain-specific.

### 2. Probe The Next Combination

Use a plausible extension, not an exhaustive feature matrix. For lifecycle,
that could be an inherited managed field with conversion and a commit hook.
Walk its success, conversion-failure, rollback, and retry paths. Ask which
existing mechanisms must learn about the combination.

A useful counterexample is an exception after provisional state changes but
before publication. Can the declared policy explain the result, or must the
reviewer reconstruct it from several coordinated methods?

This is a reasoning exercise or a small isolated test, not permission to change
public semantics or build the eventual replacement immediately.

### 3. Choose And Record A Bounded Response

Possible outcomes are:

- Continue: the coordinated edits implement distinct responsibilities and the
  authoritative policy is already clear.
- Consolidate: a small policy object, shared operation, or table removes genuine
  duplication without introducing a new framework.
- Explore a model: declaration, validation, variation, and lowering need a more
  explicit representation. Timebox a prototype around the counterexample and
  existing behavioral tests before committing to migration.

Request an independent review of the policy map and counterexample. Another
approval of the feature plan alone does not test the architectural assumption.

Use this short decision record:

- Decision and proposed next extension.
- Facts and constraints known at the time.
- Policy that currently has to be restated.
- Counterexample and observed or predicted result, clearly distinguished.
- Alternatives considered and the cost of changing direction later.
- Chosen response, unresolved semantics, and the next evidence checkpoint.

## Limits And Historical Evidence

Do not conclude that imperative code is inherently unsuitable, that a large file
is automatically wrong, or that every repeated operation requires a DSL.
The target is repeated architectural policy, not removal of ordinary algorithms.

The history supports an earlier opportunity to review the representation. It
does not prove that such a review would have avoided the detour or discovered
the eventual YIDL/Astichi architecture. Distinguish foreseeable coupling from
requirements that genuinely emerged later.

Historical observations can be reproduced from the Pyrolyze repository root:

```sh
git show -s --date=short --format='%h %ad %s' 940b74b bbebfeb d21d390
git show 940b74b:src/pyrolyze/runtime/context.py
git show bbebfeb:src/pyrolyze/lifecycle.py | wc -l
git show d21d390:src/pyrolyze/lifecycle.py | wc -l
```

These are historical source snapshots and author dates, not acceptance claims
about the current runtime. Further cases should be added only after inspecting
their decision-time evidence; this one case is not a validated universal rule.
