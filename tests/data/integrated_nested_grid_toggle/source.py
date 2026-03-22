#@pyrolyte
#@pyrolyze

from typing import Callable

from pyrolyze.api import UIElement, call_native, keyed, pyrolyze, use_state


toggle_setters: dict[tuple[str, int], Callable[[bool | Callable[[bool], bool]], None]] = {}


def remember_toggle(
    label: str,
    value: int,
    setter: Callable[[bool | Callable[[bool], bool]], None],
) -> None:
    toggle_setters[(label, value)] = setter


@pyrolyze
def panel(title: str) -> None:
    call_native(UIElement)(kind="panel", props={"title": title})


@pyrolyze
def button(label: str, *, active: bool) -> None:
    call_native(UIElement)(kind="button", props={"label": label, "active": active})


@pyrolyze
def cell_button(label: str, value: int) -> None:
    on, set_on = use_state(False)
    remember_toggle(label, value, set_on)
    button(f"{label}:{value}:{'on' if on else 'off'}", active=on)


@pyrolyze
def grid_panel(labels: list[str], values: list[int]) -> None:
    with panel("Grid"):
        for label in keyed(labels, key=lambda item: item):
            with panel(label):
                for value in keyed(values, key=lambda item: item):
                    cell_button(label, value)
