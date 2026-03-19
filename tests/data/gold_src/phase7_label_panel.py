#@pyrolyte
#@pyrolyze
from pyrolyze.api import Label, call_native, pyrolyse


@pyrolyse
def label_panel(text: str) -> None:
    call_native(Label)(text=text)
