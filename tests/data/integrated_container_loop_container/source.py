#@pyrolyte
#@pyrolyze

from pyrolyze.api import UIElement, call_native, keyed, pyrolyze


@pyrolyze
def panel(title: str) -> None:
    call_native(UIElement)(kind="panel", props={"title": title})


@pyrolyze
def badge(text: str) -> None:
    call_native(UIElement)(kind="badge", props={"text": text})


@pyrolyze
def board(labels: list[str]) -> None:
    with panel("Board"):
        for label in keyed(labels, key=lambda item: item):
            with panel(f"Cell:{label}"):
                badge(label.upper())
