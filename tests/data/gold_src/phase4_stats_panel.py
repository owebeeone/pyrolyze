#@pyrolyte
#@pyrolyze
from pyrolyze.api import UIElement, call_native, pyrolyze


log: list[tuple[object, ...]] = []


@pyrolyze
def section(title: str, *, accent: str) -> None:
    log.append(("section", title, accent))
    call_native(UIElement)(kind="section", props={"title": title, "accent": accent})


def badge(text: str, *, tone: str) -> None:
    log.append(("badge", text, tone))


@pyrolyze
def stats_panel(show_extra: bool, count: int) -> None:
    with section("Stats", accent="green"):
        badge(f"Count: {count}", tone="info")
        if show_extra:
            badge("Visible", tone="success")
        else:
            badge("Hidden", tone="muted")
