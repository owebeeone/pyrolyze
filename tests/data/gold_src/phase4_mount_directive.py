#@pyrolyte
from pyrolyze.api import MountSelector, UIElement, call_native, default, mount, pyrolyze

menu: MountSelector = MountSelector.named("menu")
corner: MountSelector = MountSelector.named("corner_widget")


@pyrolyze
def badge(text: str) -> None:
    call_native(UIElement)(kind="badge", props={"text": text})


@pyrolyze
def panel(show_inner: bool) -> None:
    with mount(menu, default):
        badge("File")
        if show_inner:
            with mount(corner(corner="top_left")):
                badge("Edit")
