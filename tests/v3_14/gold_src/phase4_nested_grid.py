#@pyrolyte
#@pyrolyze
from pyrolyze.api import UIElement, call_native, keyed, pyrolyse


log: list[tuple[object, ...]] = []


@pyrolyse
def row(title: str) -> None:
    log.append(("row", title))
    call_native(UIElement)(kind="row", props={"title": title})


def button(label: str, *, value: int) -> None:
    log.append(("button", label, value))


@pyrolyse
def grid_panel(labels: list[str], values: list[int]) -> None:
    for label in keyed(labels, key=lambda x: x):
        with row(label):
            for value in keyed(values, key=lambda x: x):
                with row(f"{label}:{value}"):
                    button(f"{label}:{value}", value=value)
