from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6 import QtGui
import PySide6
from typing import Optional


class MainWindow (QMainWindow):
    APP_NAME = 'QSound'
    ORGANIZATION = 'Pade'

    def __init__(
        self,
        parent: Optional[PySide6.QtWidgets.QWidget] = None,
        flags: PySide6.QtCore.Qt.WindowType = Qt.WindowType.Dialog
    ) -> None:
        super().__init__(parent, flags)

    def writeSettings(self):
        settings = QSettings(MainWindow.ORGANIZATION, MainWindow.APP_NAME)
        settings.beginGroup('MainWindow')
        settings.setValue('size', self.size())
        settings.setValue('position', self.pos())
        settings.endGroup()

    def readSettings(self):
        settings = QSettings(MainWindow.ORGANIZATION, MainWindow.APP_NAME)
        settings.beginGroup('MainWindow')
        size = settings.value('size')
        if (size is None):
            screen = QApplication.primaryScreen()
            size = QSize(screen.availableGeometry().size())
        self.resize(size)
        pos = settings.value('position')
        if (pos is not None):
            self.move(pos)
        settings.endGroup

    def mayBeSaved(self):
        msg = QMessageBox.warning(
            self,
            self.tr('Confirmation ?'),
            self.tr('Do you really want to quit ?'),
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        return msg == QMessageBox.StandardButton.Ok

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if (self.mayBeSaved()):
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

