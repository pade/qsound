from PySide6.QtCore import (
    QAbstractTableModel, QObject, Qt, Slot,
    QModelIndex, QPersistentModelIndex)
from PySide6.QtWidgets import QStyle, QWidget
from typing import Optional, Union, Any
from cue.audiocue import AudioCue
from engine.player import PlayerStates


class CueListModel (QAbstractTableModel):
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

    def columnCount(self, index: Union[QModelIndex, QPersistentModelIndex]) -> int:
        return 6

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> str:
        audiocue = self._cuelist[index.row()]
        match role:
            case Qt.ItemDataRole.DisplayRole:
                match index.column():
                    case 0:
                        return index.row()
                    case 1:
                        return audiocue.getName()
                    case 2:
                        fade = audiocue.getFadeDuration()
                        return f'{fade.fadeIn:.02f}' if fade.fadeIn else ''
                    case 3:
                        return audiocue.cueInfo.formatDuration()
                    case 4:
                        fade = audiocue.getFadeDuration()
                        return f'{fade.fadeOut:.02f}' if fade.fadeOut else ''
                    case 5:
                        return '\u21BA' if audiocue.getLoop() else ''
            case Qt.ItemDataRole.DecorationRole:
                if index.column() == 0:
                    if audiocue.getPlayerState() == PlayerStates.Playing:
                        pixmapi = QStyle.StandardPixmap.SP_MediaPlay
                        icon = QWidget().style().standardIcon(pixmapi)
                        return icon
            case Qt.ItemDataRole.ToolTipRole:
                return audiocue.getFullDescription()
            case Qt.ItemDataRole.TextAlignmentRole:
                if index.column() == 1:
                    return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                return Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = None) -> Any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                match section:
                    case 0:
                        return 'N°'
                    case 1:
                        return 'Name'
                    case 2:
                        return 'Fade in'
                    case 3:
                        return 'Duration'
                    case 4:
                        return 'Fade out'
                    case 5:
                        return 'Loop'

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
