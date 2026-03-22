#@pyrolyte
#@pyrolyze
from pyrolyze.api import pyrolyze as component, pyrolyze_slotted as slotted


@slotted
def upper(label: str) -> str:
    return label.upper()


def record(value: str) -> str:
    return value


@component
def panel(label: str) -> None:
    value = upper(label)
    record(value)
