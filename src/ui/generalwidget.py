from designer.general import Ui_Form
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, Slot
from typing import Optional


class GeneralWidget(QWidget, Ui_Form):

    nameChanged = Signal(str, name='nameChanged')
    loopChanged = Signal(int, name='loopChanged')

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        self.setupUi(self)
        self.name.editingFinished.connect(self._setName)
        self.loop.valueChanged.connect(self._setLoop)

    def setupUi(self, widget):
        super().setupUi(widget)

    def setOrder(self, value: int) -> None:
        self.order.setText(str(value))

    def setName(self, name: str) -> None:
        self.name.setText(name)

    def setLoop(self, loop: int) -> None:
        if loop < -1:
            loop = -1
        self.loop.setValue(loop)

    @Slot()
    def _setName(self) -> None:
        name = self.name.text()
        self.nameChanged.emit(name)

    @Slot(int)
    def _setLoop(self, value: int) -> None:
        self.loopChanged.emit(value)


    
