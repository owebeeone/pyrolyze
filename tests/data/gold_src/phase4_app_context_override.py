#@pyrolyte
#@pyrolyze
from pyrolyze.api import app_context_override, pyrolyze


THEME_KEY: object = object()
LOCALE_KEY: object = object()


def badge(text: str) -> None:
    print(text)


@pyrolyze
def panel(theme: str, locale: str, show: bool) -> None:
    with app_context_override[THEME_KEY, LOCALE_KEY](theme, locale):
        badge("body")
        if show:
            badge("extra")
