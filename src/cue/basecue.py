from PySide6.QtCore import QObject
from typing import Optional
from engine.player import PlayerStates


class BaseCue (QObject):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        self._state = PlayerStates.NotStarted
        super().__init__(parent)

    def getName(self) -> str:
        return ''

    def getFullDescription(self) -> str:
        return self.getName()

    def getCueState(self) -> PlayerStates:
        return self._state

    def stop(self):
        pass
