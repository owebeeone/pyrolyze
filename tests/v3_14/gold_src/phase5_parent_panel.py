#@pyrolyte
#@pyrolyze
from pyrolyze.api import pyrolyse


log: list[tuple[object, ...]] = []


def badge(text: str, *, tone: str) -> None:
    log.append(("badge", text, tone))


@pyrolyse
def child_badge(text: str) -> None:
    badge(text, tone="info")


@pyrolyse
def parent_panel(text: str) -> None:
    child_badge(text)
