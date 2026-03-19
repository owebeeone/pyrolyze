#@pyrolyte
#@pyrolyze
from pyrolyze.api import ComponentRef, pyrolyse, pyrolyze_slotted


@pyrolyze_slotted
def upper(label: str) -> str:
    return label.upper()


def record(value: str) -> str:
    return value


class PanelFactory:
    prefix: str

    def make(self) -> ComponentRef[[str]]:
        @pyrolyse
        def panel(label: str) -> None:
            value = upper(label)
            record(self.prefix + ":" + value)

        return panel
