#@pyrolyte
#@pyrolyze
from pyrolyze.api import pyrolyse
from pyrolyze_testsupport.imported_annotations import imported_child, imported_upper


log: list[tuple[object, ...]] = []


def record(value: str) -> None:
    log.append(("record", value))


@pyrolyse
def imported_panel(text: str) -> None:
    value = imported_upper(text)
    record(value)
    imported_child(value)
