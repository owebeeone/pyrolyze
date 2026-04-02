#@pyrolyte
from pyrolyze.api import pyrolyze, pyrolyze_slotted


@pyrolyze_slotted
def format_title(name: str) -> str:
    return f"Hello {name}"


@pyrolyze
def greeting(name: str) -> None:
    title = format_title(name)
    del title
