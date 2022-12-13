from designer.general import Ui_Form
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, Slot, QFileInfo
from typing import Optional
from ui.mediafiledialog import ChangeMediaFile
from PySide6.QtGui import QValidator


class GeneralWidget(QWidget, Ui_Form):

    nameChanged = Signal(str, name='nameChanged')
    loopChanged = Signal(int, name='loopChanged')
    mediaFileChanged = Signal(str, name='mediaFileChanged')

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        self.setupUi(self)
        self.name.editingFinished.connect(self._setName)
        self.loop.valueChanged.connect(self._setLoop)
        self.changeFilename.clicked.connect(self._changeMediaFile)
        self.mediaFileChanged.connect(self.setFilename)

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
    def _changeMediaFile(self) -> None:
        fileName = ChangeMediaFile(self).getFilenames()
        if fileName is not None:
            self.mediaFileChanged.emit(fileName[0])

    @Slot()
    def _setName(self) -> None:
        name = self.name.text()
        self.nameChanged.emit(name)

    @Slot(int)
    def _setLoop(self, value: int) -> None:
        self.loopChanged.emit(value)

    @Slot(str)
    def setFilename(self, filename: str) -> None:
        file = QFileInfo(filename)
        basename = file.fileName()
        path = file.absolutePath()
        if len(basename) > 50:
            shortName = '...' + basename[-47:]
        else:
            if len(basename) + len(path) > 50:
                index = 50 - len(basename)
                shortName = path[:index-3] + '.../' + basename
            else:
                shortName = filename
        self.fileName.setText(shortName)
        self.fileName.setToolTip(filename)




    
