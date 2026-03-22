#@pyrolyte
#@pyrolyze
from pyrolyze.api import PyrolyzeHandler, UIElement, call_native, pyrolyze


log: list[str] = []


@pyrolyze
def button(
    label: str,
    *,
    on_press: PyrolyzeHandler[[], None] | None = None,
) -> None:
    call_native(UIElement)(
        kind="button",
        props={"label": label, "on_press": on_press},
    )


@pyrolyze
def panel(name: str) -> None:
    button("Save", on_press=lambda: log.append(name))
