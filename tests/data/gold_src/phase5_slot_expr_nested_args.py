#@pyrolyte
#@pyrolyze
from pyrolyze.api import pyrolyze, pyrolyze_slotted


@pyrolyze_slotted
def slot_f2(x: int, y: int) -> int:
    return x + y


@pyrolyze_slotted
def slot_f1(value: int) -> tuple[int, int]:
    return value, value * 2


@pyrolyze
def panel(a: int) -> None:
    v1, v2 = slot_f1(slot_f2(1, a))
    pair = (v1, v2)
