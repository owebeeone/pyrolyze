#@pyrolyte
#@pyrolyze
from pyrolyze.api import UIElement, call_native, pyrolyze


log: list[tuple[object, ...]] = []


@pyrolyze
def row(name: str) -> None:
    log.append(("row", name))
    call_native(UIElement)(kind="row", props={"name": name})


def label(text: str) -> None:
    log.append(("label", text))


@pyrolyze
def pair_panel(v1: str, v2: str) -> None:
    with row("outer"):
        label("row-start")
        with row("inner"):
            label(v1)
            label(v2)
