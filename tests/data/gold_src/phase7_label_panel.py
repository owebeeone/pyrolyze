#@pyrolyte
#@pyrolyze
from pyrolyze.api import Label, call_native, pyrolyze


@pyrolyze
def label_panel(text: str) -> None:
    call_native(Label)(text=text)
