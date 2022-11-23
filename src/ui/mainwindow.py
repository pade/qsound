from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QKeySequence, QCloseEvent
from typing import Optional
from settings import settings
from ui.mediafiledialog import MediaFileDialog


class MainWindow (QMainWindow):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Dialog
    ) -> None:
        super().__init__(parent, flags)
        self.createMenuBar()
        self.setLayout(QHBoxLayout())
        self.setWindowTitle('QSound')

    def createMenuBar(self):
        newAction = QAction(self.tr('New...'), self)
        newAction.setShortcuts(QKeySequence.StandardKey.New)
        quitAction = QAction(self.tr('Quit'), self)
        quitAction.setShortcut(QKeySequence.StandardKey.Quit)
        saveAsAction = QAction(self.tr('Save as...'), self)
        saveAsAction.setShortcut(QKeySequence.StandardKey.SaveAs)
        saveAction = QAction(self.tr('Save'), self)
        saveAction.setShortcut(QKeySequence.StandardKey.Save)

        fileMenu = self.menuBar().addMenu(self.tr('File'))
        fileMenu.addAction(newAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(quitAction)

        mediaCueAction = QAction(self.tr('Add a media cue'), self)
        mediaCueAction.setShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_A)
        )
        mediaCueAction.triggered.connect(self.mediaFileSelector)
        cueMenu = self.menuBar().addMenu(self.tr('Cues'))
        cueMenu.addAction(mediaCueAction)

    def mediaFileSelector(self):
        filesName = MediaFileDialog(self).getFilenames()
        # for file in filesName:
            
    def writeSettings(self):
        settings.beginGroup('MainWindow')
        settings.setValue('size', self.size())
        settings.setValue('position', self.pos())
        settings.endGroup()

    def readSettings(self):
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

    def closeEvent(self, event: QCloseEvent) -> None:
        if (self.mayBeSaved()):
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

