import array
import math
import logging

import numpy as np
from pydub import AudioSegment
from PySide6.QtCore import QFileInfo, Signal, Slot

from cue.basecue import BaseCue
from cue.volume import Volume
from engine.player import Player, PlayerStates


class CueInfo:
    def __init__(self, name: str, duration: float, elapsed: int) -> None:
        self.name = name
        self.duration = duration
        self.elapsed = elapsed

    def formatDuration(self):
        return self.formatTime(self.duration)

    def formatElapsed(self):
        return self.formatTime(self.elapsed)

    def formatTime(self, seconds):
        minutes, sec = divmod(seconds, 60)
        nbOfSeconds = math.floor(sec)
        millisec = math.floor((sec - nbOfSeconds) * 100)
        return f'{int(minutes):02d}:{int(nbOfSeconds):02d}:{int(millisec):02d}'


class AudioCue (BaseCue):

    changedCue = Signal(CueInfo, name='changedCue')
    audioSignalChanged = Signal(list, float, float, name='audioSignalChanged')

    def __init__(self, filename: str) -> None:
        super().__init__()
        self._filename = ''
        self._startsAt = 0.0
        self._endsAt = 0.0
        self.__fadeInDuration = 0.0
        self.__fadeOutDuration = 0.0
        self._audioPoints = []
        self._volume = Volume()
        self.audio = AudioSegment.empty()
        self.player = None
        self._playerState = None
        self.setSource(filename)

    def isValid(self):
        if not QFileInfo(self._filename).exists():
            return False
        # TODO

    def setSource(self, filename: str) -> None:
        self._filename = filename
        self.audio = AudioSegment.from_file(self._filename)
        self._mixAudio = AudioSegment.empty() + self.audio
        self.player = self.createPlayer(self._mixAudio)
        self.cueInfo = CueInfo(
            QFileInfo(self._filename).fileName(),
            self.audio.duration_seconds,
            0
        )
        audio1000Hz, _ = self.audio.set_frame_rate(1000).split_to_mono()
        samples = audio1000Hz.get_array_of_samples()
        buffer = array.array(audio1000Hz.array_type, samples)
        time = np.linspace(
            0,
            len(buffer) / audio1000Hz.frame_rate,
            num=len(buffer)
        )
        self._audioPoints = np.stack((time, buffer), axis=-1).tolist()
        self.setStartsAs(0.0)
        self.setEndsAt(time[-1])

    def _computeAudio(self):
        left, right = self.audio.split_to_mono()
        left = left + self._volume.left
        right = right + self._volume.right
        rawData = AudioSegment.from_mono_audiosegments(left, right).raw_data
        # Directly modify _data to take into account modification while player is playing audio
        self._mixAudio._data = rawData

    def getAudioPoints(self):
        return self._audioPoints

    def createPlayer(self, audio: AudioSegment) -> Player:
        player = Player(audio, self.getStartsAt(), self.getEndsAt())
        player.changedState.connect(self.setPlayerState)
        player.elapsedTime.connect(self.duration)
        return player

    @Slot(int)
    def duration(self, elapsed: int) -> None:
        self.cueInfo.elapsed = elapsed
        self.changedCue.emit(self.cueInfo)

    @Slot()
    def stop(self):
        self.player.stop()

    @Slot()
    def play(self):
        if self._playerState == PlayerStates.Ended or self._playerState == PlayerStates.Stopped:
            self.player = self.createPlayer(self._mixAudio)
        self.player.start()

    @Slot()
    def pause(self):
        self.player.pause()

    @Slot(PlayerStates)
    def setPlayerState(self, state: PlayerStates):
        self._playerState = state
        logging.debug(f'Player state is "{state.name}"')

    def getStartsAt(self) -> float:
        return self._startsAt

    @Slot(float)
    def setStartsAs(self, ms: float) -> None:
        value = self._checkStartOrEndValue(ms)
        # Stop player when changing start cursor
        self.stop()
        self._startsAt = value

    def getEndsAt(self) -> float:
        return self._endsAt

    @Slot(float)
    def setEndsAt(self, ms: float) -> None:
        value = self._checkStartOrEndValue(ms)
        # Stop player when changing end cursor
        self.stop()
        self._endsAt = value

    def _checkStartOrEndValue(self, ms: float):
        if ms < 0.0:
            ms = 0.0
        if ms > len(self.audio):
            ms = float(len(self.audio))
        return ms

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
