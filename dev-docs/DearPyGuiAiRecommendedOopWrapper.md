# AI-recommended DearPyGui OOP wrapper (reference only)

**Status:** Archival. This snippet is **not** part of PyRolyze `src`; it was suggested in an external review as a “reconciliation”-style layer over DearPyGui.

**Related:** Gaps and how they compare to the real PyRolyze stack are tracked in [`PyrolyzeDearPyGuiTodos.md`](PyrolyzeDearPyGuiTodos.md).

**Caveats (for anyone copying this):**

- `DPGNode.unmount()` deletes the DPG item and clears `self.children` via `_set_unmounted_recursive`, but **does not remove this node from a parent’s `children` list**—a parent that still holds a reference can retain “zombie” Python objects unless the parent is updated too.
- `_set_unmounted_recursive` is **recursive**; very deep trees can hit `RecursionError` (prefer an explicit stack if this pattern is adopted).
- **Manual string `tag=`** remains globally unique in DPG; duplicated tags in lists still risk collisions.
- **`InputText` factory** forces `on_enter=True` when omitted—opinionated for some UIs (see TODO doc item 6).
- **`PyrolyzeDPGRuntime`** uses `render_dearpygui_frame` + sleep; validate against the DearPyGui version you target (`start_dearpygui` vs manual render loop).

## Source (as provided)

```python
import dearpygui.dearpygui as dpg
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union

class DPGNode(ABC):
    """
    Advanced Reconciliation Node.
    Manages physical DPG state, child ordering, and lifecycle sync.
    """
    def __init__(self, tag: str, **kwargs):
        self.tag = tag
        self.kwargs = kwargs
        self.mounted = False
        self.children: List['DPGNode'] = []
        self._is_container = False

    @abstractmethod
    def mount(self, parent_tag: Optional[str] = None, before: str = ""):
        pass

    def update(self, **new_kwargs):
        """Atomic diffing: only sends messages for changed values."""
        changed = {k: v for k, v in new_kwargs.items() if self.kwargs.get(k) != v}
        if not changed:
            return
            
        self.kwargs.update(changed)
        if self.mounted and dpg.does_item_exist(self.tag):
            dpg.configure_item(self.tag, **changed)

    def unmount(self):
        """Clean destruction of the UI subtree and registry removal."""
        if self.mounted:
            if dpg.does_item_exist(self.tag):
                dpg.delete_item(self.tag)
            self._set_unmounted_recursive()

    def _set_unmounted_recursive(self):
        self.mounted = False
        for child in self.children:
            child._set_unmounted_recursive()
        self.children.clear()

class LeafNode(DPGNode):
    """Value-bearing widgets with no internal hierarchy."""
    def __init__(self, factory_name: str, tag: str, **kwargs):
        super().__init__(tag, **kwargs)
        self.factory_name = factory_name

    def mount(self, parent_tag: Optional[str] = None, before: str = ""):
        if dpg.does_item_exist(self.tag):
            # Stability: If it exists but is in the wrong place, reparent/reorder
            if before:
                dpg.move_item(self.tag, parent=parent_tag or "", before=before)
            self.update(**self.kwargs)
            self.mounted = True
            return

        factory = getattr(dpg, self.factory_name)
        params = {**self.kwargs, "tag": self.tag}
        if parent_tag: params["parent"] = parent_tag
        if before: params["before"] = before
        
        factory(**params)
        self.mounted = True

class ContainerNode(DPGNode):
    """
    Structural Node with Order Reconciliation.
    Ensures children in DPG match the order of self.children.
    """
    def __init__(self, context_alias: str, tag: str, **kwargs):
        super().__init__(tag, **kwargs)
        self.context_alias = context_alias
        self._is_container = True

    def add(self, child: 'DPGNode'):
        self.children.append(child)
        return self

    def mount(self, parent_tag: Optional[str] = None, before: str = ""):
        exists = dpg.does_item_exist(self.tag)
        
        if not exists:
            # First time mount
            context_mgr = getattr(dpg, self.context_alias)
            params = {**self.kwargs, "tag": self.tag}
            if parent_tag: params["parent"] = parent_tag
            if before: params["before"] = before
            
            with context_mgr(**params):
                for child in self.children:
                    child.mount()
        else:
            # Re-mounting / Reconciliation
            if before:
                dpg.move_item(self.tag, parent=parent_tag or "", before=before)
            
            self.update(**self.kwargs)
            
            # Reconciliation Loop: Ensure order and presence
            # We iterate backwards to use the 'before' logic effectively
            last_tag = ""
            for child in reversed(self.children):
                child.mount(parent_tag=self.tag, before=last_tag)
                last_tag = child.tag
                
        self.mounted = True

class TableNode(ContainerNode):
    """
    Specialized structural node for DPG Tables.
    Enforces the 'Columns before Rows' invariant.
    """
    def __init__(self, tag: str, **kwargs):
        super().__init__("table", tag, **kwargs)
        self.columns: List[LeafNode] = []

    def add_column(self, tag: str, **kwargs):
        self.columns.append(LeafNode("add_table_column", tag, **kwargs))
        return self

    def mount(self, parent_tag: Optional[str] = None, before: str = ""):
        exists = dpg.does_item_exist(self.tag)
        if not exists:
            with dpg.table(tag=self.tag, parent=parent_tag or "", before=before, **self.kwargs):
                # RULE: Columns must be created first in a table
                for col in self.columns:
                    col.mount()
                for child in self.children:
                    child.mount()
        else:
            self.update(**self.kwargs)
            # DPG Tables are hard to re-order columns on; we focus on row reconciliation
            last_tag = ""
            for child in reversed(self.children):
                child.mount(parent_tag=self.tag, before=last_tag)
                last_tag = child.tag
        self.mounted = True

# --- Improved Runtime ---

class PyrolyzeDPGRuntime:
    def __init__(self, fps_limit: int = 60):
        dpg.create_context()
        self.root: Optional[DPGNode] = None
        self.target_frame_time = 1.0 / fps_limit

    def start(self, root_node: DPGNode, width=1280, height=720, title="Pyrolyze App"):
        self.root = root_node
        dpg.create_viewport(title=title, width=width, height=height)
        dpg.setup_dearpygui()
        
        self.root.mount()
        dpg.show_viewport()
        
        while dpg.is_dearpygui_running():
            start_time = time.perf_counter()
            
            dpg.render_dearpygui_frame()
            
            # Frame-rate limiting (Back-pressure)
            sleep_time = self.target_frame_time - (time.perf_counter() - start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
                
        dpg.destroy_context()

# --- Factory Helpers ---

def Window(tag: str, **kwargs) -> ContainerNode: return ContainerNode("window", tag, **kwargs)
def Group(tag: str, **kwargs) -> ContainerNode: return ContainerNode("group", tag, **kwargs)
def Button(tag: str, **kwargs) -> LeafNode: return LeafNode("add_button", tag, **kwargs)
def Table(tag: str, **kwargs) -> TableNode: return TableNode(tag, **kwargs)
def TableRow(tag: str, **kwargs) -> ContainerNode: return ContainerNode("table_row", tag, **kwargs)
def InputText(tag: str, **kwargs) -> LeafNode: 
    # Default on_enter to True if not specified
    if 'on_enter' not in kwargs: kwargs['on_enter'] = True
    return LeafNode("add_input_text", tag, **kwargs)
```
