#@pyrolyte
#@pyrolyze

from typing import Callable

from pyrolyze.api import UIElement, call_native, keyed, pyrolyze, use_state


toggle_setters: dict[str, Callable[[bool | Callable[[bool], bool]], None]] = {}


def remember_toggle(
    name: str,
    setter: Callable[[bool | Callable[[bool], bool]], None],
) -> None:
    toggle_setters[name] = setter


@pyrolyze
def panel(title: str) -> None:
    call_native(UIElement)(kind="panel", props={"title": title})


@pyrolyze
def item_badge(name: str) -> None:
    on, set_on = use_state(False)
    remember_toggle(name, set_on)
    call_native(UIElement)(kind="badge", props={"text": name, "active": on})


@pyrolyze
def board(items: list[str]) -> None:
    with panel("Board"):
        for item in keyed(items, key=lambda value: value):
            item_badge(item)
