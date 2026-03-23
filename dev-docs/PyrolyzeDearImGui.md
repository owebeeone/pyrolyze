# **PyrolyzeDearImGui: Architectural Design Document**

## **1\. Overview**

PyrolyzeDearImGui is a design pattern and library implementation intended to "oopify" the **Dear PyGui (DPG)** API. By transforming DPG's flat, imperative function set into a hierarchical class model, we bridge the gap between a high-performance immediate-mode renderer and a modern, declarative composition engine like **Pyrolyze**.

### **The Core Concept**

In DPG, the "Display Layer" is detached. We send messages to create or move nodes, and the engine handles the drawing. This design doc details how to reassemble these messages into a cohesive object model that enforces structural constraints (e.g., you can't put a Window inside a Button) while maintaining the benefits of a detached, reactive UI.

## **2\. Hierarchical Class Model**

The API is divided into three primary base classes that mirror the DPG internal architecture.

### **2.1 DPGNode (The Abstract Handle)**

Every element in the UI is a DPGNode. It is not the "widget" itself, but a **stable handle** (the Tag) that persists even if the physical widget is deleted or moved.

* **Identity:** Managed via a unique tag.  
* **State:** Managed via a kwargs dictionary for properties (width, height, label).  
* **Lifecycle:** Tracks mounted status to prevent sending messages to non-existent nodes.

### **2.2 LeafNode (Factories)**

Maps to mountable\_factory entries in the API dump (e.g., add\_button, add\_input\_text).

* **Constraint:** These nodes are terminal. They cannot have children.  
* **Operations:** Primarily update (configure\_item) and callback execution.

### **2.3 ContainerNode (Context Aliases)**

Maps to mountable\_context\_alias entries (e.g., window, group, table).

* **Responsibility:** Manages the **Container Stack**.  
* **Structural Integrity:** Enforces "Holes" vs "Materials." For example, a Table class only accepts TableColumn and TableRow as children.  
* **Reparenting:** Provides the move\_item logic to shift subtrees between different layout contexts without losing internal child state.

## **3\. Reassembling the API: Operation Mapping**

To put "Humpty Dumpty back together," we categorize the 497+ DPG functions into specific OO behaviors:

| DPG Category | Pyrolyze Operation | Implementation Strategy |
| :---- | :---- | :---- |
| mountable\_factory | **Component Creation** | Instantiated as LeafNode subclasses via the Generator. |
| mountable\_context\_alias | **Structural Scope** | Instantiated as ContainerNode using Python context managers. |
| query\_only | **Reactive Hooks** | Wrapped as use\_item\_state() or use\_mouse\_pos(). Values are fetched during the reconciliation pass. |
| backend\_method\_candidate | **Instance Methods** | dpg.focus\_item(tag) becomes my\_button.focus(). |
| backend\_runtime\_only | **Host Environment** | Hidden from the user; managed by the Pyrolyze.run() entry point. |

## **4\. Structural Constraints & Slots**

One of the primary reasons for this OOP layer is to prevent invalid UI trees.

### **4.1 Strict Parenting**

By defining allowed child types in the class model, we can catch errors at "Model Time" before they hit the C++ renderer:

* **Menu** nodes can only exist inside a MenuBar or Window.  
* **PlotSeries** nodes can only exist inside a PlotAxis.

### **4.2 The "Reparenting" Message**

Since DPG is message-based, "moving" a subtree is a single message: move\_item(tag, parent=new\_parent).

In our OOP model, this allows for **Slotted Content**:

1. A Card component creates a ChildWindow as a "Slot."  
2. The Pyrolyze engine "mounts" user-provided content into that slot.  
3. If the user moves the Card, the physical children stay attached to the slot's tag, avoiding a costly "delete/rebuild" cycle.

## **5\. Parallel with Qt and Modern Frameworks**

The PyrolyzeDearImGui model mirrors high-level constructs found in Qt but with an "Immediate Mode" backend:

### **5.1 Windows and Modals**

Like QMainWindow, our Window class manages top-level viewport state. However, unlike Qt, our Windows are just nodes in a flat registry. Closing a window doesn't necessarily destroy the Python object; it just sends a show=False or unmount message.

### **5.2 Menus and Tooltips (QMenu equivalent)**

In DPG, menus are specialized containers. In our model:

* **ContextMenu**: A container triggered by a parent node's right-click.  
* **Tooltip**: A container that follows the mouse when a parent node is hovered.  
  Pyrolyze manages the "Activation State" (is it open?), and the OO model ensures the menu items are correctly parented to the floating popup.

## **6\. Implementation Workflow**

1. **Generation:** Use generate\_library.py to crawl the API dump and create the class library.  
2. **Reconciliation:** The Pyrolyze engine maintains a "Shadow Tree" of these objects.  
3. **Diffing:** On state change, Pyrolyze compares the new shadow tree with the current DPG state.  
4. **Message Dispatch:**  
   * New Node? \-\> dpg.add\_xxx  
   * Removed Node? \-\> dpg.delete\_item  
   * Moved Node? \-\> dpg.move\_item  
   * Property Change? \-\> dpg.configure\_item

## **7\. Conclusion**

By "oopifying" Dear PyGui, we gain the performance of a GPU-accelerated IMGUI with the developer experience of a managed, hierarchical framework. We stop "scripting a window" and start "composing a system of persistent, reactive parts."