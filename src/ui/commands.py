from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt
from typing import Optional


class CommandsWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        vBox = QVBoxLayout()
        self.playBtn = QPushButton('Play')
        self.pauseBtn = QPushButton('Pause')
        self.stopBtn = QPushButton('Stop')
        vBox.addWidget(self.playBtn)
        vBox.addWidget(self.pauseBtn)
        vBox.addWidget(self.stopBtn)
        self.setLayout(vBox)
        
