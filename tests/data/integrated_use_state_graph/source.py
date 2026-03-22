#@pyrolyte
#@pyrolyze

from typing import Callable

from pyrolyze.api import Label, call_native, pyrolyze, use_state


captured_setter: Callable[[int | Callable[[int], int]], None] | None = None


def remember_setter(setter: Callable[[int | Callable[[int], int]], None]) -> None:
    global captured_setter
    captured_setter = setter


@pyrolyze
def counter_panel() -> None:
    count, set_count = use_state(0)
    remember_setter(set_count)
    call_native(Label)(text=f"Count: {count}")
