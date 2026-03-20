# Studio Baseline Parity Map

This map links baseline interaction groups from
[Studio App Spec Baseline.md](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/Studio%20App%20Spec%20Baseline.md)
to current Studio implementation status.

| Baseline Area | Current Studio Status | Notes |
|---|---|---|
| Window chrome, edge handles, native title-bar behavior | Partial | Frameless shell, resize handles, custom title bar, and context menu are implemented; Win32-specific move/size semantics remain pending. |
| Explorer activation intent | Partial | Native `QFileSystemModel` + `QTreeView` shell panel is present; command wiring remains pending parity work. |
| File/Edit command surface | Parity placeholder | Explicit placeholder messages are implemented. |
| Bottom panel switching | Partial parity | Native bottom `QTabWidget` with Output/Terminal is implemented; command integration remains placeholder. |
| Inspector hierarchy/screenshot/drawing | Deferred | Placeholder section remains; full inspector migration pending runtime extensions. |
| Persistence restore/save | Deferred | Service contracts exist; full settings lifecycle migration pending. |
