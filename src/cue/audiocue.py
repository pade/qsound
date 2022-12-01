from PySide6.QtCore import QFileInfo, Slot, Signal
from cue.volume import Volume
from cue.basecue import BaseCue
from engine.player import Player
from pydub import AudioSegment


class CueInfo:
    def __init__(self, name: str, duration: int, elapsed: int) -> None:
        self.name = name
        self.duration = duration
        self.elapsed = elapsed


class AudioCue (BaseCue):

    changedCue = Signal(CueInfo, name='changedCue')

    def __init__(self, filename: str) -> None:
        super().__init__()
        self._filename = ''
        self._startsAt = 0
        self._endsAt = 0
        self.__fadeInDuration = 0
        self.__fadeOutDuration = 0
        self._volume = Volume()
        self.audio: AudioSegment = None
        self.setSource(filename)

    def isValid(self):
        if not QFileInfo(self._filename).exists():
            return False
        # TODO

    def setSource(self, filename: str) -> None:
        self._filename = filename
        self.audio = AudioSegment.from_file(self._filename)
        self._mixAudio = AudioSegment.empty() + self.audio
        self.player = Player(self._mixAudio)
        self.cueInfo = CueInfo(
            QFileInfo(self._filename).fileName(),
            len(self.audio),
            0
        )
        self.player.elapsedTime.connect(self.duration)

    def _computeAudio(self):
        left, right = self.audio.split_to_mono()
        left = left + self._volume.left
        right = right + self._volume.right
        rawData = AudioSegment.from_mono_audiosegments(left, right).raw_data
        # Directly modify _data without to take into account modification while player is playing audio
        self._mixAudio._data = rawData

    @Slot(int)
    def duration(self, elapsed: int) -> None:
        self.cueInfo.elapsed = elapsed
        self.changedCue.emit(self.cueInfo)

    @Slot()
    def stop(self):
        self.player.stop()

    @Slot()
    def play(self):
        self.player.start()

    @Slot()
    def pause(self):
        self.player.pause()

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
        self._computeAudio()

    def getName(self) -> str:
        return self.cueInfo.name

    def getFullDescription(self) -> str:
        return QFileInfo(self._filename).absoluteFilePath()

    @Slot(str)
    def setName(self, value: str) -> None:
        self._name = value
        self.cueInfo.name = value
        self.changedCue.emit(self.cueInfo)

    def __str__(self) -> str:
        return f'{self.getName()}'
