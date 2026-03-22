#@pyrolyte
#@pyrolyze
from pyrolyze.api import pyrolyze, pyrolyze_slotted


@pyrolyze_slotted
def upper(label: str) -> str:
    return label.upper()


def record(value: str) -> str:
    return value


class Panel:
    prefix: str

    @pyrolyze
    def show(self, label: str) -> None:
        value = upper(label)
        record(self.prefix + ":" + value)

    @classmethod
    @pyrolyze
    def build(cls, label: str) -> None:
        value = upper(label)
        record(cls.__name__ + ":" + value)

    @staticmethod
    @pyrolyze
    def static(label: str) -> None:
        value = upper(label)
        record("static:" + value)
