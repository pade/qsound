from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QDir
from settings import settings


class MediaFileDialog:

    SETTING_KEY = 'AudioFile/directory'

    def __init__(self, parent) -> None:
        self.__settings = settings
        self.__fileDialog = QFileDialog(parent)
        self.__fileDialog.setNameFilter('Audio (*.wav *.mp3 *.ogg)')
        self.__fileDialog.setViewMode(QFileDialog.ViewMode.List)
        directory = self.__settings.value(self.SETTING_KEY)
        if directory is None or not QDir(directory).exists():
            directory = QDir().homePath()

        self.__fileDialog.setDirectory(directory)
        self.__fileDialog.setWindowTitle(QFileDialog.tr('Select audio files'))
        self.__fileDialog.setFileMode(QFileDialog.FileMode.ExistingFiles)

    def getFilenames(self):
        if self.__fileDialog.exec():
            directory = self.__fileDialog.directory()
            self.__settings.setValue(self.SETTING_KEY, directory.absolutePath())
            return self.__fileDialog.selectedFiles()
