from PySide6.QtCore import (
    QAbstractListModel, QObject, Qt, Slot,
    QModelIndex, QPersistentModelIndex
)
from typing import Optional, Union
from cue.audiocue import AudioCue


class CueListModel (QAbstractListModel):
    def __init__(
        self,
        cuelist: Optional[list[AudioCue]] = None,
        parent: Optional[QObject] = None
    ) -> None:
        super().__init__(parent)
        self._cuelist = cuelist or []
        self.currentIndex = QModelIndex()

    def rowCount(self, index: Union[QModelIndex, QPersistentModelIndex]) -> int:
        return len(self._cuelist)

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> str:
        audiocue = self._cuelist[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            fade = audiocue.getFadeDuration()
            fadeInText = f'\u279A {fade.fadeIn:.02f}' if fade.fadeIn else ''
            fadeOutText = f'\u2798 {fade.fadeOut:.02f}' if fade.fadeOut else ''
            loop = audiocue.getLoop()
            loopText = '\u21BA' if loop else ''
            return f'{index.row()} - {audiocue.getName()} {fadeInText} [{audiocue.cueInfo.formatDuration()}] {fadeOutText} {loopText}'
        if role == Qt.ItemDataRole.ToolTipRole:
            return audiocue.getFullDescription()

    def addCue(self, cue: AudioCue) -> None:
        self._cuelist.append(cue)
        self.updateLayout()

    @Slot()
    def updateLayout(self):
        self.layoutChanged.emit()

    def flags(self, index):
        flags = super().flags(index)
        if index.isValid():
            flags |= Qt.ItemFlag.ItemIsDragEnabled
        else:
            flags |= Qt.ItemFlag.ItemIsDropEnabled
        return flags

    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.MoveAction

    def moveRows(
        self,
        sourceParent: Union[QModelIndex, QPersistentModelIndex],
        sourceRow: int,
        count: int,
        destinationParent: Union[QModelIndex, QPersistentModelIndex],
        destinationChild: int
    ) -> bool:
        if sourceRow < 0 \
            or sourceRow >= self.rowCount(sourceParent) \
            or destinationChild < 0 \
            or destinationChild > self.rowCount(destinationParent) \
            or sourceRow == destinationChild \
            or sourceRow == destinationChild - 1 \
            or count != 1\
                or sourceParent.isValid() or destinationParent.isValid():
            return False

        if not self.beginMoveRows(QModelIndex(), sourceRow, sourceRow, QModelIndex(), destinationChild):
            return False
        self._cuelist.insert(destinationChild, self._cuelist.pop(sourceRow))
        self.endMoveRows()
        return True

    def getCue(self, index: QModelIndex) -> AudioCue:
        if index.isValid():
            return self._cuelist[index.row()]
        else:
            return None

    def getAllCue(self) -> list[AudioCue]:
        return self._cuelist