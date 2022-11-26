from PySide6.QtCore import QFileInfo, Slot, QUrl, QObject
from PySide6.QtMultimedia import QMediaPlayer, QMediaFormat, QAudioOutput
from cue.volume import Volume
from cue.basecue import BaseCue


class AudioCue (BaseCue):
    def __init__(self, filename: QUrl | str) -> None:
        super().__init__()
        self._filename = ''
        self._name = ''
        self._startsAt = 0
        self._endsAt = 0
        self.__fadeInDuration = 0
        self.__fadeOutDuration = 0
        self._volume = Volume()
        self._player = QMediaPlayer()
        self._audioOutput = QAudioOutput()
        self._player.setAudioOutput(self._audioOutput)
        self.setSource(filename)

    @staticmethod
    def getSupportedMimeTypes():
        result = []
        for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode):
            mime_type = QMediaFormat(f).mimeType()
            result.append(mime_type)
        return result

    def isValid(self):
        if not QFileInfo(self.getFullPath()).exists():
            return False
        player = QMediaPlayer()
        player.setSource(self._filename)
        return player.hasAudio()

    def setSource(self, filename: QUrl | str) -> None:
        if isinstance(filename, str):
            self._filename = QUrl.fromLocalFile(filename)
        else:
            self._filename = filename
        self._player.setSource(self._filename)
        # metadata = self._player.metaData()
        # self.__duration = metadata.keys()
        # print(self.isValid())
        self._name = self._filename.fileName()

    def play(self):
        self._player.play()

    @Slot(QMediaPlayer.Error, str)
    def printError(self, error, msg):
        print('Error :', error)

    def getStartsAt(self) -> float:
        return self._startsAt

    @Slot(float)
    def setStartsAs(self, value: float) -> None:
        if (value < 0.0):
            value = 0.0
        self._startsAt = value

    def getEndsAt(self) -> float:
        return self._endsAt

    @Slot(float)
    def setEndsAt(self, value: float) -> None:
        if (value < 0.0):
            value = 0.0
        self._endsAt = value

    def getFadeInDuration(self) -> float:
        return self.__fadeInDuration

    @Slot(float)
    def setFadeInDuration(self, value: float) -> None:
        if (value < 0.0):
            value = 0.0
        self.__fadeInDuration = value

    def getFadeOutDuration(self) -> float:
        return self.__fadeOutDuration

    @Slot(float)
    def setFadeOutDuration(self, value: float) -> None:
        if (value < 0.0):
            value = 0.0
        self.__fadeOutDuration = value

    def getVolume(self) -> Volume:
        return self._volume

    @Slot(Volume)
    def setVolume(self, volume: Volume) -> None:
        self._volume = volume

    def getName(self) -> str:
        return self._name

    def getFullDescription(self) -> str:
        return self._filename.toLocalFile()

    @Slot(str)
    def setName(self, value: str) -> None:
        self._name = value
