from typing import Any, Optional, Union, List

from PySide6.QtCore import (QAbstractTableModel, QMimeData, QModelIndex,
                            QObject, QPersistentModelIndex, Qt, Slot)
from PySide6.QtWidgets import QStyle, QWidget

from cue.basecue import BaseCue
from engine.player import PlayerStates
from engine.cuelistitem import CueListItem


class CueListModel (QAbstractTableModel):
    def __init__(
        self,
        cuelist: Optional[CueListItem] = None,
        parent: Optional[QObject] = None
    ) -> None:
        super().__init__(parent)
        self._cuelist: List[CueListItem] = cuelist or []
        self.currentIndex = QModelIndex()

    def rowCount(self, index: Union[QModelIndex, QPersistentModelIndex] = None) -> int:
        return len(self._cuelist)

    def columnCount(self, index: Union[QModelIndex, QPersistentModelIndex] = None) -> int:
        return 6

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int) -> str:
        cueItem = self._cuelist[index.row()]
        match role:
            case Qt.ItemDataRole.DisplayRole:
                return cueItem.data[index.column()]
            case Qt.ItemDataRole.ToolTipRole:
                return cueItem.getCue().getFullDescription()
            case Qt.ItemDataRole.TextAlignmentRole:
                if index.column() == 1:
                    return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                return Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
            case Qt.ItemDataRole.DecorationRole:
                if index.column() == 0:
                    if cueItem.getCue().getCueState() == PlayerStates.Playing:
                        pixmapi = QStyle.StandardPixmap.SP_MediaPlay
                        icon = QWidget().style().standardIcon(pixmapi)
                        return icon

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
        self._cuelist.append(CueListItem(cue))
        self.updateLayout()

    @Slot()
    def updateLayout(self):
        for item in self._cuelist:
            item.setValue()
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
        self._cuelist.insert(row, CueListItem(BaseCue()))
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

    def getCue(self, index: QModelIndex) -> BaseCue:
        if index.isValid():
            return (self._cuelist[index.row()]).getCue()
        else:
            return None

    def getAllCue(self) -> list[BaseCue]:
        return list(map(lambda x: x.getCue(), self._cuelist))
