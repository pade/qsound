from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QDir, QObject
from settings import settings


class MediaFileDialog (QObject):

    SETTING_KEY = 'AudioFile/directory'

    def __init__(self, parent) -> None:
        self.__settings = settings
        self._fileDialog = QFileDialog(parent)
        self._fileDialog.setNameFilter(self.tr('Audio (*.wav *.mp3 *.ogg)'))
        self._fileDialog.setViewMode(QFileDialog.ViewMode.List)
        directory = self.__settings.value(self.SETTING_KEY)
        if directory is None or not QDir(directory).exists():
            directory = QDir().homePath()

        self._fileDialog.setDirectory(directory)
        self._fileDialog.setWindowTitle(QFileDialog.tr('Select audio files'))
        self._fileDialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        # self.__fileDialog.setMimeTypeFilters(AudioCue.getSupportedMimeTypes())

    def getFilenames(self):
        if self._fileDialog.exec():
            directory = self._fileDialog.directory()
            self.__settings.setValue(self.SETTING_KEY, directory.absolutePath())
            return self._fileDialog.selectedFiles()


class ChangeMediaFile(MediaFileDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self._fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)