from typing import Optional
from designer.fade import Ui_FadeWidget
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Slot


class FadeWidget(QWidget, Ui_FadeWidget):
    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        self.setupUi(self)
        