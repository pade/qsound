from PySide6.QtCore import QFileInfo, Slot, QUrl
from PySide6.QtMultimedia import QMediaPlayer
from cue.volume import Volume


class AudioCue:
    def __init__(self, filename: QUrl | str) -> None:
        self.__filename = ''
        self.__name = ''
        self.setSource(filename)
        self.__startsAt = 0
        self.__endsAt = 0
        self.__fadeInDuration = 0
        self.__fadeOutDuration = 0
        self.__volume = Volume()
        
    def isValid(self):
        if not QFileInfo(self.__filename.toLocalFile()).exists():
            return False
        player = QMediaPlayer()
        player.setSource(self.__filename)
        return player.hasAudio()

    def setSource(self, filename: QUrl | str) -> None:
        if isinstance(filename, str):
            self.__filename = QUrl.fromLocalFile(filename)
        else:
            self.__filename = filename
        player = QMediaPlayer()
        player.errorOccurred.connect(self.printError)
        player.setSource(self.__filename)
        metadata = player.metaData()
        self.__duration = metadata.keys()
        print(self.__duration)
        self.__name = self.__filename.fileName()

    @Slot(QMediaPlayer.Error, str)
    def printError(self, error, msg):
        print('Error :', error)

    def getStartsAt(self) -> float:
        return self.__startsAt

    @Slot(float)
    def setStartsAs(self, value: float) -> None:
        if (value < 0.0):
            value = 0.0
        self.__startsAt = value

    def getEndsAt(self) -> float:
        return self.__endsAt

    @Slot(float)
    def setEndsAt(self, value: float) -> None:
        if (value < 0.0):
            value = 0.0
        self.__endsAt = value

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
        return self.__volume

    @Slot(Volume)
    def setVolume(self, volume: Volume) -> None:
        self.__volume = volume

    def getName(self) -> str:
        return self.__name

    @Slot(str)
    def name(self, value: str) -> None:
        self.__name = value
