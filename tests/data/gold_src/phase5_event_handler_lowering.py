#@pyrolyte
#@pyrolyze
from pyrolyze.api import PyrolyzeHandler, UIElement, call_native, pyrolyse


log: list[str] = []


@pyrolyse
def button(
    label: str,
    *,
    on_press: PyrolyzeHandler[[], None] | None = None,
) -> None:
    call_native(UIElement)(
        kind="button",
        props={"label": label, "on_press": on_press},
    )


@pyrolyse
def panel(name: str) -> None:
    button("Save", on_press=lambda: log.append(name))
