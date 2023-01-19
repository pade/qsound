import logging
import uuid
from typing import Any, Optional, Union, List

from PySide6.QtCore import (QAbstractTableModel, QMimeData, QModelIndex,
                            QObject, QPersistentModelIndex, Qt, Slot)
from PySide6.QtWidgets import QStyle, QWidget

from cue.audiocue import AudioCue
from cue.basecue import BaseCue
from engine.cuelistitem import CueListItem
from engine.player import PlayerStates

logger = logging.getLogger(__name__)


class CueList:
    def __init__(self) -> None:
        self._data = {}

    def append(self, cue: BaseCue) -> str:
        id = str(uuid.uuid4())
        self._data[id] = cue
        return id

    def remove(self, id: str) -> str:
        try:
            self._data.pop(id)
        except KeyError:
            logger.error(f'Key \'{id}\' not found')

    def getCue(self, id: str) -> BaseCue:
        try:
            return self._data[id]
        except KeyError:
            logger.error(f'Key \'{id}\' not found')
            return None

    def getListOfCue(self) -> List[BaseCue]:
        return list(self._data.values())


class CueListModel (QAbstractTableModel):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.currentIndex = QModelIndex()
        self._data = []
        self._cueList = CueList()
        pixmapi = QStyle.StandardPixmap.SP_MediaPlay
        self._playIcon = QWidget().style().standardIcon(pixmapi)

    def rowCount(self, index: Union[QModelIndex, QPersistentModelIndex] = None) -> int:
        return len(self._data)

    def columnCount(self, index: Union[QModelIndex, QPersistentModelIndex] = None) -> int:
        return 6

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> str:
        cue = self.getCue(index.row())
        if cue is None:
            return
        match role:
            case Qt.ItemDataRole.DisplayRole:
                if index.column() < 6:
                    return self._data[index.row()][index.column()]
            case Qt.ItemDataRole.ToolTipRole:
                return cue.getFullDescription()
            case Qt.ItemDataRole.TextAlignmentRole:
                if index.column() == 1:
                    return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                return Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
            case Qt.ItemDataRole.DecorationRole:
                if index.column() == 0:
                    if cue.getCueState() == PlayerStates.Playing:
                        return self._playIcon

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = None) -> Any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                match section:
                    case 0:
                        return ''
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
            else:
                return section

    def addCue(self, cue: BaseCue) -> None:
        id = self._cueList.append(cue)
        self.setCueData(id, cue)
        self.updateLayout()

    def setCueData(self, id: str, cue: BaseCue) -> None:
        data = [None] * 7
        data[0] = ''
        data[1] = cue.getName()
        if isinstance(cue, AudioCue):
            fade = cue.getFadeDuration()
            data[2] = f'{fade.fadeIn:.02f}'
            data[3] = cue.cueInfo.formatDuration()
            data[4] = f'{fade.fadeOut:.02f}'
            data[5] = '\u21BA' if cue.getLoop() else ''
        else:
            data[2:6] = ['', '', '', '']
        data[6] = id
        index = self._getIndexOfId(id)
        logger.debug(f'Index: {index}')
        if index != -1:
            self._data[index] = data
        else:
            self._data.append(data)
        logger.debug(f'self._data: {self._data}')

    def _getIndexOfId(self, id: str) -> int:
        for index, item in enumerate(self._data):
            if item[6] == id:
                return index
        return -1
     
    @Slot()
    def updateLayout(self):
        for index, item in enumerate(self._data):
            cue = self.getCue(index)
            self.setCueData(item[6], cue)

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

    def insertRows(self, row: int, count: int, parent: Union[QModelIndex, QPersistentModelIndex] = None) -> bool:
        if count != 1:
            return False
        self.beginInsertRows(QModelIndex(), row, row)
        self._data.insert(row, CueListItem(BaseCue()))
        self.endInsertRows()
        return True

    def removeRows(self, row: int, count: int, parent: Union[QModelIndex, QPersistentModelIndex] = None) -> bool:
        self.beginMoveRows(QModelIndex(), row, row + count - 1)
        del self._cuelist[row: row + count]
        self.endRemoveRows()
        return True

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: Union[QModelIndex, QPersistentModelIndex]) -> bool:
        print(data.text())
        if parent.isValid():
            newParent = QModelIndex()
            row = parent.row() + 1
        else:
            newParent = parent

        if row == -1:
            row = self.rowCount()
        return super().dropMimeData(data, action, row, 0, newParent)

    def getCue(self, index: int) -> BaseCue:
        return self._cueList.getCue(self._data[index][6])

    def getAllCues(self) -> list[BaseCue]:
        return self._cueList.getListOfCue()
