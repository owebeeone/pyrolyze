#@pyrolyte
#@pyrolyze
from pyrolyze.api import pyrolyze, pyrolyze_slotted


@pyrolyze_slotted
def slot_fa(x: int, y: int) -> int:
    return x + y


@pyrolyze_slotted
def slot_fb(x: int, y: int) -> int:
    return x * y


def record(value: int) -> int:
    return value


@pyrolyze
def panel(x: int, y: int) -> None:
    value = slot_fa(x, y) + slot_fb(1, 2)
    record(value)
