from PySide6.QtWidgets import QListView, QAbstractItemView, QSizePolicy, QWidget
from PySide6.QtCore import QAbstractListModel
from typing import Optional


class CueListView (QListView):

    def __init__(self, model: QAbstractListModel, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setModel(model)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
