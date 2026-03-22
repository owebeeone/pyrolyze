#@pyrolyte
#@pyrolyze
from pyrolyze.api import pyrolyze


log: list[tuple[object, ...]] = []


def badge(text: str, *, tone: str) -> None:
    log.append(("badge", text, tone))


@pyrolyze
def child_badge(text: str) -> None:
    badge(text, tone="info")


@pyrolyze
def parent_panel(text: str) -> None:
    child_badge(text)
