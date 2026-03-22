#@pyrolyte
#@pyrolyze
from pyrolyze.api import ComponentRef, pyrolyze, pyrolyze_slotted


@pyrolyze_slotted
def upper(label: str) -> str:
    return label.upper()


def record(value: str) -> str:
    return value


def make_panel(prefix: str) -> ComponentRef[[str]]:
    @pyrolyze
    def panel(label: str) -> None:
        value = upper(label)
        record(prefix + ":" + value)

    return panel
