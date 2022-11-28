from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QListView
from PySide6.QtWidgets import QApplication, QMessageBox, QAbstractItemView, QSizePolicy
from PySide6.QtCore import QSize, Qt, QModelIndex, Slot, Signal, QTime
from PySide6.QtGui import QAction, QKeySequence, QCloseEvent
from typing import Optional
from settings import settings
from ui.mediafiledialog import MediaFileDialog
from cue.audiocue import AudioCue
from ui.audiocuewidget import AudioCueWidget
from engine.cuelist import CueListModel


class MainWidget (QWidget):
    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        vBox = QVBoxLayout()
        self._cueListModel = CueListModel()
        self._cueListView = QListView()
        self._cueListView.setDragEnabled(True)
        self._cueListView.setAcceptDrops(True)
        self._cueListView.setDropIndicatorShown(True)
        self._cueListView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._cueListView.setAlternatingRowColors(True)
        self._cueListView.setModel(self._cueListModel)
        self._cueListView.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self._cueListView.clicked.connect(self.selectedCue)
        self.audioCueWidget = AudioCueWidget()
        self.audioCueWidget.setEnabled(False)
        vBox.addWidget(self._cueListView)
        vBox.addWidget(self.audioCueWidget)
        self.setLayout(vBox)

    @Slot(QModelIndex)
    def selectedCue(self, index: QModelIndex):
        self.audioCueWidget.setEnabled(True)
        if self._cueListModel.currentIndex.isValid():
            lastCue = self._cueListModel.getCue(self._cueListModel.currentIndex)
            self.audioCueWidget.volume.disconnect(lastCue)
        self._cueListModel.currentIndex = index
        cue = self._cueListModel.getCue(index)
        self.audioCueWidget.volume.setVolume(cue.getVolume())
        self.audioCueWidget.volume.volumeChanged.connect(cue.setVolume)
    
    def addCue(self, cue: AudioCue) -> None:
        self._cueListModel.addCue(cue)

    def stop(self):
        for cue in self._cueListModel.getAllCue():
            cue.stop()


class MainWindow (QMainWindow):

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        flags: Qt.WindowType = Qt.WindowType.Dialog
    ) -> None:
        super().__init__(parent, flags)
        self.createMenuBar()
        self.setWindowTitle('QSound')

        self.mainWidget = MainWidget()
        self.setCentralWidget(self.mainWidget)
        
    def createMenuBar(self):
        newAction = QAction(self.tr('New...'), self)
        newAction.setShortcuts(QKeySequence.StandardKey.New)
        quitAction = QAction(self.tr('Quit'), self)
        quitAction.setShortcut(QKeySequence.StandardKey.Quit)
        quitAction.triggered.connect(self.quit)
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

    @Slot()
    def mediaFileSelector(self):
        filesName = MediaFileDialog(self).getFilenames()
        if filesName is not None:
            for file in filesName:
                self.mainWidget.addCue(AudioCue(file))
            
    def writeSettings(self):
        settings.setValue('size', self.size())
        settings.setValue('position', self.pos())

    def readSettings(self):
        size = settings.value('size')
        if (size is None):
            screen = QApplication.primaryScreen()
            size = QSize(screen.availableGeometry().size())
        self.resize(size)
        pos = settings.value('position')
        if (pos is not None):
            self.move(pos)

    def mayBeSaved(self):
        msg = QMessageBox.warning(
            self,
            self.tr('Confirmation ?'),
            self.tr('Do you really want to quit ?'),
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        return msg == QMessageBox.StandardButton.Ok

    @Slot()
    def quit(self):
        if self.beforeQuit:
            QApplication.quit()

    def beforeQuit(self) -> bool:
        if self.mayBeSaved():
            self.mainWidget.stop()
            someMsAfter = QTime.currentTime().addMSecs(500)
            while QTime.currentTime() < someMsAfter:
                pass
            self.writeSettings()
            return True
        return False

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.beforeQuit():
            event.accept()
        else:
            event.ignore()

