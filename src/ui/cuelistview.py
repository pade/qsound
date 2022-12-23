from PySide6.QtWidgets import QTableView, QAbstractItemView, QSizePolicy, QWidget
from PySide6.QtCore import QAbstractListModel, Slot
from typing import Optional


class CueListView (QTableView):

    def __init__(self, model: QAbstractListModel, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSortingEnabled(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setModel(model)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setColumnWidth(0, 30)
        self.setColumnWidth(1, 300)
        self.setColumnWidth(2, 80)
        self.setColumnWidth(3, 80)
        self.setColumnWidth(4, 80)
        self.setColumnWidth(5, 10)
