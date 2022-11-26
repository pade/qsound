from PySide6.QtCore import QObject
from typing import Optional


class BaseCue (QObject):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)

    def getName(self) -> str:
        raise NotImplementedError

    def getFullDescription(self) -> str:
        return self.getName()
