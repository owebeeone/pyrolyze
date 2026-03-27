# PySide6 Nested Layout Failure Analysis

## Purpose

This document describes the current red PySide6 regression precisely enough to
evaluate the host-surface placement design against a real backend failure.

The failing test is:

- `pyrolyze/tests/test_pyside6_native_host.py`
- `test_native_pyside6_conditional_nested_layout_toggle_keeps_row_above_trailing_label`


## The Failing Authored Structure

The test component is authored as:

```python
with Qt.CQMainWindow(windowTitle="Conditional Nested Layout Counter"):
    with Qt.CQWidget(objectName="central_widget"):
        with Qt.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
            if count % 2 == 0:
                Qt.CQLabel(f"Time: {count}", objectName="top_label")
            else:
                Qt.CQLabel("Count is odd - no time", objectName="top_label")
            Qt.CQLabel("Page size: 50", objectName="page_label")
            with Qt.CQHBoxLayout(objectName="count_row"):
                Qt.CQPushButton("-", objectName="decrement_button", ...)
                Qt.CQLabel(f"Count: {count}", objectName="count_label")
                Qt.CQPushButton("+", objectName="increment_button", ...)
            Qt.CQLabel("Description", objectName="bottom_label")
```

The critical detail is that `count_row` is a bare nested `QHBoxLayout`, not a
`QWidget` wrapper that happens to contain a layout.


## Expected Structural Mounted Graph

The structural mounted graph before and after increment should remain:

```text
QMainWindow
  QWidget("central_widget")
    QBoxLayout("top_to_bottom")
      QLabel("top_label")
      QLabel("page_label")
      QHBoxLayout("count_row")
        QPushButton("decrement_button")
        QLabel("count_label")
        QPushButton("increment_button")
      QLabel("bottom_label")
```

The branch under `top_label` changes text when the count flips from even to
odd, but the `count_row` subtree is intended to be retained.


## Expected Host Placement Order

The parent `QBoxLayout` host surface should keep the same slot order across the
update:

```text
QBoxLayout layout slots:
  0 -> top_label
  1 -> page_label
  2 -> count_row
  3 -> bottom_label
```

Within the nested `QHBoxLayout`, the internal order should remain:

```text
count_row slots:
  0 -> decrement_button
  1 -> count_label
  2 -> increment_button
```


## Actual Observed Failure

After clicking `increment_button`, the test still finds:

- `increment_button`
- `bottom_label`
- `count_label`

and `count_label.text()` updates correctly to `Count: 1`.

So the nested row survives structurally and still functions.

But the measured placement order is wrong:

```text
row_global_y == 72
bottom_global_y == 51
```

So the retained row ends up visually below the trailing label:

```text
actual parent placement:
  0 -> top_label
  1 -> page_label
  2 -> bottom_label
  3 -> count_row
```


## Why This Is Not A Demo Bug

The failing test is a small direct PySide6 native-host repro in `pyrolyze`
itself. It does not depend on the demo app.

It uses:

- transformed component source
- `RenderContext`
- `pyrolyze.pyrolyze_native_pyside6.create_host`
- `pyrolyze.pyrolyze_native_pyside6.reconcile_window_content`

So the failure belongs to the backend/runtime mounting path, not the demo code.


## The Relevant Backend Surface Contract

The concrete backend surface here is a generated `QBoxLayout.layout` mount
point, not a generic hand-written helper.

In `pyrolyze/src/pyrolyze/backends/pyside6/generated_library.py`,
`QBoxLayout.layout` is emitted roughly as:

```python
MountPointSpec(
    name="layout",
    accepted_produced_type=TypeRef(expr="PySide6.QtWidgets.QLayout"),
    place_method_name="insertLayout",
    append_method_name="addLayout",
    detach_method_name="removeItem",
    replay_kind=MountReplayKind.INDEX,
    prefer_sync=False,
)
```

That means the relevant host surface is:

- ordered
- index-replayed
- parent-owned
- accepting child layouts

This is not the same surface class as a widget child inserted into a widget
layout through `insertWidget`.


## Why The Current Generic Backend Misses It

The current extended generic backend can validate:

- concrete mount-profile identity
- mutation-policy identity
- structural mounted-graph order
- deterministic mutation sequences
- seeded fuzz replays over mount profiles

That is not yet enough here.

The missing capability is explicit host placement modeling for nested container
children.

Today the generic backend still collapses too much into structural mount
buckets:

- a retained nested child is tracked as structurally present
- its internal child surface can still look correct
- but the parent-owned host slot can drift without the generic model noticing

This PySide6 failure is exactly that shape.


## Structural Retention Versus Host Placement Drift

This bug matters because two statements are simultaneously true:

1. the `count_row` nested container survives as the same authored child
2. the parent `QBoxLayout` places it in the wrong visual order

So structural correctness is not sufficient.

The generic model must be able to say:

- `count_row` is still mounted
- `count_row` still owns its own internal ordered surface
- but the parent `layout` host surface now places `count_row` after
  `bottom_label`


## Why The Wrapped-Widget Variant Does Not Expose The Same Failure

The sibling test that wraps the controls row in a `QWidget` host keeps passing.

That matters because it narrows the failing surface:

- the wrapped form behaves like a widget child occupying one parent slot
- the failing form is a bare nested layout child mounted via `insertLayout` and
  detached via `removeItem`

So the bug is not simply “ordered children are broken.”

It is more specific:

- retained nested layout child
- parent-owned ordered host surface
- sibling churn before the retained child
- child survives structurally
- parent slot placement drifts


## First Generic Surface Needed To Express This Bug

The first generic host-surface profile must represent:

1. ordered parent host surface
2. nested-container child occupies one parent slot
3. nested-container child also owns its own internal ordered surface
4. structural retention can diverge from parent host placement order

This corresponds to the cookbook surface:

- `ordered_nested_container_children`

That surface must support assertions over:

- structural mounted graph
- parent host placement order
- nested child interior placement order
- operation log for parent-slot detach/reinsert


## Minimum Generic Red Test Equivalent

The generic equivalent should encode:

1. parent ordered host surface with four children:
   - conditional `top_label`
   - stable `page_label`
   - retained nested `count_row`
   - trailing `bottom_label`
2. a mutation sequence that flips the conditional branch before the retained
   nested child
3. a retained `count_row` nested surface whose interior children remain correct
4. an expected parent host placement assertion that `count_row` stays before
   `bottom_label`

The generic red case should fail if the parent host placement becomes:

```text
[top_label, page_label, bottom_label, count_row]
```

even if the structural tree still reports:

```text
top_label
page_label
count_row
bottom_label
```


## What This Analysis Implies For The Design

The host-surface placement design is sufficient only if it can model all of the
following independently:

- structural node identity
- retained nested-container identity
- parent-owned host-slot identity
- parent host placement order
- nested child interior placement order

If any of those collapse together, this failure class can escape again.


## Completion Check

The Phase 0B completion gate is satisfied only when an implementer can look at
this document and identify one generic host-surface profile and one generic red
test shape that directly correspond to the current PySide6 failure.
