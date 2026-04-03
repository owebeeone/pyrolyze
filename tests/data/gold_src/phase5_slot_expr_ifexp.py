#@pyrolyte
#@pyrolyze
from pyrolyze.api import pyrolyze, pyrolyze_slotted


@pyrolyze_slotted
def use_grip(key: str) -> str:
    return key


@pyrolyze
def panel(flag: bool) -> None:
    k = use_grip("A")
    v = 10 if flag else use_grip(k)
