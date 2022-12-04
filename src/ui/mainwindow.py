from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QSize, Qt, QModelIndex, Slot, QTime
from PySide6.QtGui import QAction, QKeySequence, QCloseEvent
from typing import Optional
from settings import settings
from ui.mediafiledialog import MediaFileDialog
from cue.audiocue import AudioCue
from ui.audiocuewidget import AudioCueWidget
from engine.cuelist import CueListModel
from ui.commands import CommandsWidget
from ui.cuelistview import CueListView


class MainWidget (QWidget):
    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        vBox = QVBoxLayout()
        hBox = QHBoxLayout()
        self._cueListModel = CueListModel()
        self._cueListView = CueListView(self._cueListModel)
        self._cueListView.clicked.connect(self.selectedCue)
        self.audioCueWidget = AudioCueWidget()
        self.audioCueWidget.setEnabled(False)
        self.commands = CommandsWidget()
        hBox.addWidget(self._cueListView, 80)
        hBox.addWidget(self.commands, 20)
        w = QWidget()
        w.setLayout(hBox)
        vBox.addWidget(w, 66)
        vBox.addWidget(self.audioCueWidget, 33)
        self.setLayout(vBox)

    @Slot(QModelIndex)
    def selectedCue(self, index: QModelIndex):
        self.audioCueWidget.setEnabled(True)
        if self._cueListModel.currentIndex.isValid():
            lastCue = self._cueListModel.getCue(self._cueListModel.currentIndex)
            self.audioCueWidget.volume.disconnect(lastCue)
            self.commands.playBtn.disconnect(lastCue)
            self.commands.pauseBtn.disconnect(lastCue)
            self.commands.stopBtn.disconnect(lastCue)
            lastCue.disconnect(self.audioCueWidget.sound)
        self._cueListModel.currentIndex = index
        cue = self._cueListModel.getCue(index)
        self.audioCueWidget.volume.setVolume(cue.getVolume())
        self.audioCueWidget.volume.volumeChanged.connect(cue.setVolume)
        self.audioCueWidget.sound.setSeries(cue.getAudioPoints(), cue.getStartsAt(), cue.getEndsAt())
        cue.audioSignalChanged.connect(self.audioCueWidget.sound.setSeries)
        cue.changedCue.connect(self.audioCueWidget.sound.setPlayCursor)
        self.commands.playBtn.pressed.connect(cue.play)
        self.commands.pauseBtn.pressed.connect(cue.pause)
        self.commands.stopBtn.pressed.connect(cue.stop)
    
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

