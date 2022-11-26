from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QToolButton, QSpacerItem,
    QSizePolicy
    
)
from PySide6 import *
from PySide6.QtCore import Qt
from typing import Optional


class CueWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        hBox = QHBoxLayout()
        self.order = QLabel()
        self.name = QLabel()
        self.button = QToolButton()
        self.button.setText('X'),
        hBox.addWidget(self.order)
        hBox.addWidget(self.name)
        spacer = QSpacerItem(150, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        hBox.addSpacerItem(spacer)
        hBox.addWidget(self.button)
        self.setLayout(hBox)
    
    def getText(self) -> str:
        return f'{self.order.text()} - {self.name.text()}'