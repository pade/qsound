from designer.general import Ui_Form
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from typing import Optional


class GeneralWidget(QWidget, Ui_Form):
    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        self.setupUi(self)

    def setupUi(self, widget):
        super().setupUi(self, widget)
