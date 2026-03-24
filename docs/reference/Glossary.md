# Glossary

- boundary
  - a rerunnable execution unit managed by `RenderContext`
- committed UI
  - the last successfully committed tuple of `UIElement` values for a context
- component ref
  - a callable with `_pyrolyze_meta`, typed as `ComponentRef[...]`
- container
  - a structural context that can own a committed native root
- keyed loop
  - a structural looping context that manages keyed item identity
- mount point
  - a named backend attachment site that can receive emitted native children
- mount selector
  - a runtime selector value consumed by `mount(...)` to choose a mount point
- mount advertisement
  - metadata published by `advertise_mount(...)` that maps a stable public key
    to one or more internal mount selectors for a native container surface
- default advert
  - a mount advertisement marked with `default=True`, used when resolving
    `with mount(default):` for children on that surface
- loop item
  - a child context for one keyed loop item
- render owner
  - the context that receives emitted UI at commit time
- slotted helper
  - a helper lowered through `call_plain(...)`, usually marked with `@pyrolyze_slotted`
- slot
  - a runtime-owned identity point represented by `SlotId`
- structural owner
  - the context that owns child contexts, visitation, and teardown
