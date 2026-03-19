#@pyrolyte
#@pyrolyze
from pyrolyze.api import pyrolyse, pyrolyze_slotted


@pyrolyze_slotted
def format_title(name: str) -> str:
    return f"Hello {name}"


def record(value: str) -> str:
    return value


@pyrolyse
def greeting(name: str) -> None:
    title = format_title(name)
    label = title + "!"
    record(label)
