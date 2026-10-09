from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest


def test_mount_collectors_share_one_local_graph_walk(monkeypatch: Any) -> None:
    from pyrolyze.runtime import context_bare_refactor_lcm as runtime
    from pyrolyze.runtime.context_state_lcm import mount_render, mount_expr_render
    from pyrolyze.runtime.context_state_lcm.component_render import (
        _enable_component_render,
    )

    root = runtime.RenderContext()
    _enable_component_render(root._state_mgr)
    original = mount_render._graph_states
    walks: list[object] = []

    def walk(render: Any, **kwargs: Any) -> Any:
        walks.append(render)
        return original(render, **kwargs)

    monkeypatch.setattr(mount_render, "_graph_states", walk)
    monkeypatch.setattr(mount_expr_render, "_graph_states", walk)
    root._state_mgr._field_only_completion._advertisements_for(
        root._state_mgr, current=False
    )
    assert len(walks) == 1


@dataclass
class GraphNode:
    children: dict[int, GraphNode] = field(default_factory=dict)
    reads: int = 0
    committed: GraphNode | None = None

    @property
    def children_state(self) -> dict[int, GraphNode]:
        self.reads += 1
        return self.children

    @property
    def current(self) -> GraphNode:
        return self if self.committed is None else self.committed


@pytest.mark.parametrize("count", [10, 100, 1000])
def test_overlapping_completion_roots_are_walked_once(
    monkeypatch: Any, count: int
) -> None:
    from pyrolyze.runtime.context_state_lcm import callback_render, context_base

    monkeypatch.setattr(context_base, "ContextBaseStateMgr", GraphNode)
    leaves = [GraphNode() for _ in range(count)]
    root = GraphNode(dict(enumerate(leaves)))
    detached = GraphNode()
    states = callback_render._graph_states_many(
        (root, *leaves, detached), current=False
    )
    assert states == (root, *leaves, detached)
    assert all(node.reads == 1 for node in states)


def test_graph_walk_views_and_later_mutations_are_independent(monkeypatch: Any) -> None:
    from pyrolyze.runtime.context_state_lcm import callback_render, context_base

    monkeypatch.setattr(context_base, "ContextBaseStateMgr", GraphNode)
    accepted = GraphNode()
    candidate = GraphNode()
    root = GraphNode({0: candidate}, committed=GraphNode({0: accepted}))
    assert callback_render._graph_states_many((root,), current=True)[1] is accepted
    assert callback_render._graph_states_many((root,), current=False)[1] is candidate
    replacement = GraphNode()
    root.children = {0: replacement}
    assert callback_render._graph_states_many((root,), current=False)[1] is replacement


def test_nested_completion_roots_do_not_repeat_descendant_walks(
    monkeypatch: Any,
) -> None:
    from pyrolyze.runtime.context_state_lcm import callback_render, context_base

    monkeypatch.setattr(context_base, "ContextBaseStateMgr", GraphNode)
    roots = [GraphNode() for _ in range(40)]
    for parent, child in zip(roots, roots[1:]):
        parent.children[0] = child
    callback_render._graph_states_many(roots, current=False)
    assert all(node.reads == 1 for node in roots)


def test_render_local_walk_excludes_nested_render_subtrees(monkeypatch: Any) -> None:
    from pyrolyze.runtime.context_state_lcm import (
        callback_render,
        context_base,
        render_context,
    )

    @dataclass
    class RenderNode(GraphNode):
        pass

    monkeypatch.setattr(context_base, "ContextBaseStateMgr", GraphNode)
    monkeypatch.setattr(render_context, "RenderContextStateMgr", RenderNode)
    nested_leaf = GraphNode()
    nested = RenderNode({0: nested_leaf})
    local_leaf = GraphNode()
    root = RenderNode({0: local_leaf, 1: nested})
    states = callback_render._graph_states(root, current=False, render_local=True)
    assert len(states) == 2
    assert states[0] is root and states[1] is local_leaf
    assert nested.reads == nested_leaf.reads == 0
