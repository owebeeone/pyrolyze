# Host Surface Placement Conformance

## Purpose

This document links the generic host-surface test surface to the existing red
PySide6 regression so the relationship between the two is explicit.

It answers three questions:

1. what generic test shape corresponds to the real backend failure
2. what parts of the real failure are already covered generically
3. what behavior remains backend-specific and still belongs to the PySide6 fix


## Real Backend Target

The real backend regression remains:

- `pyrolyze/tests/test_pyside6_native_host.py`
- `test_native_pyside6_conditional_nested_layout_toggle_keeps_row_above_trailing_label`

That test encodes this authored scenario class:

1. ordered parent `QBoxLayout`
2. widget-like sibling before the retained row
3. stable widget-like sibling between the changing branch and the retained row
4. retained nested `QHBoxLayout` child occupying one parent slot
5. trailing widget-like sibling after the retained row
6. branch churn before the retained nested row
7. retained nested row remains structurally live and interactive
8. parent host placement drifts so the row falls below the trailing label


## Generic Counterpart

The generic test surface that corresponds to this scenario is now:

- `pyrolyze/tests/test_generic_backend_host_surface_runtime.py`
- `test_mixed_host_surface_retained_nested_row_stays_before_trailing_sibling_under_branch_churn`

Supporting adjacent coverage:

- `test_mixed_host_surface_retained_nested_row_stays_before_trailing_sibling_under_tail_branch_churn`
- `pyrolyze/tests/test_generic_backend_host_surface_fuzz.py`
- `test_seeded_host_surface_fuzz_replays_to_fresh_equivalent_state`


## Scenario Mapping

### Real PySide6 Scenario

```text
QBoxLayout parent surface
  top_label          widget
  page_label         widget
  count_row          nested_container
  bottom_label       widget
```

Mutation:

- `top_label` branch changes when count flips
- `page_label` survives
- `count_row` survives
- `bottom_label` survives

Expected parent host order after rerender:

```text
top_label, page_label, count_row, bottom_label
```

Actual red PySide6 order:

```text
top_label, page_label, bottom_label, count_row
```


### Generic Scenario

```text
ordered_slots host surface
  top               widget
  page              widget
  controls          nested_container
  bottom            widget
```

Mutation:

- `top` branch changes text/value
- `page` survives
- `controls` survives
- `bottom` survives

Expected host order after rerender:

```text
top, page, controls, bottom
```

The generic tests assert:

- structural order
- host-surface order
- per-entry child kinds
- rerendered state equals fresh-render state


## What Is Covered Generically

The generic host-surface work now covers the following parts of the bug family:

1. ordered parent host surface semantics
2. mixed widget and nested-container entries on one parent surface
3. retained nested row occupying one stable parent slot
4. sibling churn before the retained nested row
5. sibling churn after the retained nested row
6. fresh-render equivalence for host placement order
7. replayable seeded mutation coverage over the same surface class

That means the generic backend now meaningfully covers the authored scenario
class that the PySide6 bug belongs to.


## Residual Backend-Specific Behavior

The generic surface does not yet model all Qt-specific mechanics.

What remains backend-specific:

1. `QBoxLayout.layout` mounts child layouts via `insertLayout` / `removeItem`,
   not widget placement methods
2. Qt layout items are not the same thing as widgets, so the parent host API is
   item-based in the failing case
3. Qt geometry/layout passes determine the final visual `y` positions measured
   by the red test
4. the concrete PySide6 failure is in the real placement/reconciliation path,
   not just in the abstract final host order

So the generic coverage is now sufficient for the scenario class, but it is
still not a substitute for the real backend conformance test.


## Conformance Conclusion

The generic host-surface tests and the red PySide6 test now align on the same
authored scenario class:

- mixed ordered parent surface
- retained nested child among widget siblings
- branch churn around that retained child
- retained row must stay before trailing sibling

No additional generic host-surface class is required before the PySide6 fix.

The remaining work is backend-specific:

- fix the PySide6 placement/reconciliation path
- keep the red PySide6 test as the real conformance target
- use the generic tests as the backend-independent contract for the same bug
  family
