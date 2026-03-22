#@pyrolyte
#@pyrolyze
from typing import Any

from pyrolyze.api import UIElement, call_native, pyrolyze, ui_interface


@ui_interface
class PySide6UiLibrary:
    @classmethod
    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:
        return UIElement(kind=kind, props=dict(kwds))

    @classmethod
    @pyrolyze
    def CQPushButton(
        cls,
        text: str,
        *,
        flat: bool | None = None,
        enabled: bool | None = None,
    ) -> None:
        call_native(cls.__element)(
            kind="QPushButton",
            text=text,
            flat=flat,
            enabled=enabled,
        )

    @classmethod
    @pyrolyze
    def CQLabel(
        cls,
        text: str,
        *,
        wordWrap: bool | None = None,
        openExternalLinks: bool | None = None,
    ) -> None:
        call_native(cls.__element)(
            kind="QLabel",
            text=text,
            wordWrap=wordWrap,
            openExternalLinks=openExternalLinks,
        )
