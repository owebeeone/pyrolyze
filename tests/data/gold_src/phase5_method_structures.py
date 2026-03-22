#@pyrolyte
#@pyrolyze
from pyrolyze.api import UIElement, call_native, keyed, pyrolyze


log: list[tuple[object, ...]] = []


@pyrolyze
def group(name: str) -> None:
    log.append(("group", name))
    call_native(UIElement)(kind="group", props={"name": name})


def text(value: str) -> None:
    log.append(("text", value))


def label(value: str) -> None:
    log.append(("label", value))


class Panels:
    @pyrolyze
    def instance(self, prefix: str, items: list[str]) -> None:
        with group("instance"):
            for item in keyed(items, key=lambda x: x):
                text(prefix + item)

    @classmethod
    @pyrolyze
    def build(cls, prefix: str, items: list[str]) -> None:
        with group("class"):
            for item in keyed(items, key=lambda x: x):
                label(prefix + item)

    @staticmethod
    @pyrolyze
    def static(prefix: str, items: list[str]) -> None:
        with group("static"):
            for item in keyed(items, key=lambda x: x):
                text(prefix + item)
