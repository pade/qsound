import array
import logging
import math

import numpy as np
from pydub import AudioSegment
from PySide6.QtCore import QFileInfo, Signal, Slot
from PySide6 import QtWidgets

from cue.basecue import BaseCue
from cue.fade import Fade
from cue.volume import Volume
from engine.player import Player, PlayerStates

logger = logging.getLogger(__name__)


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
        app = QtWidgets.QApplication.instance()
        app.aboutToQuit.connect(self.quit)
        self.player = None
        self.playerState = PlayerStates.Stopped
        self.setSource(filename)

    @Slot()
    def quit(self):
        if self.player:
            self.player.quit()

    def isValid(self):
        if not QFileInfo(self._filename).exists():
            return False
        # TODO

    def setSource(self, filename: str) -> None:
        self._filename = filename
        self._startsAt = 0.0
        self._endsAt = 0.0
        self._fade = Fade()
        self._loop = 0
        self._audioPoints = []
        self._volume = Volume()
        if self.player:
            self.player.quit()
        self.audio: AudioSegment = AudioSegment.from_file(self._filename)
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
        self._startsAt = 0.0
        self._endsAt = self.audio.duration_seconds
        self.player = Player(self.audio)
        self.player.changedState.connect(self.setPlayerState)
        self.player.elapsedTime.connect(self.duration)
        self.player.start()
        self.player.setLoop(self.getLoop())
        self.player.setStart(self.getStartsAt())
        self.player.setEnd(self.getEndsAt())
        logger.debug('Player created')
    
    def getAudioPoints(self):
        return self._audioPoints

    @Slot(int)
    def setLoop(self, value: int) -> None:
        if value < -1:
            self._loop = 0
        else:
            self._loop = value
        self.player.setLoop(value)

    def getLoop(self):
        return self._loop

    @Slot(int)
    def duration(self, elapsed: int) -> None:
        self.cueInfo.elapsed = elapsed
        self.changedCue.emit(self.cueInfo)

    @Slot()
    def stop(self):
        if self.player:
            self.player.stop()

    @Slot()
    def play(self):
        self.player.play()

    @Slot()
    def pause(self):
        self.player.pause()

    @Slot(PlayerStates)
    def setPlayerState(self, state: PlayerStates):
        logger.debug(f'{self.getName()}: Player state is "{state.name}"')
        self.playerState = state

    def getPlayerState(self) -> PlayerStates:
        return self.playerState

    def getStartsAt(self) -> float:
        return self._startsAt

    @Slot(float)
    def setStartsAs(self, ms: float) -> None:
        self._startsAt = self._convertStartOrEndValue(ms)
        self.player.setStart(self._startsAt)

    def getEndsAt(self) -> float:
        return self._endsAt

    @Slot(float)
    def setEndsAt(self, ms: float) -> None:
        self._endsAt = self._convertStartOrEndValue(ms)
        self.player.setEnd(self._endsAt)

    def _convertStartOrEndValue(self, seconds: float):
        if seconds < 0.0:
            return 0.0
        if seconds > self.audio.duration_seconds:
            return self.audio.duration_seconds
        return seconds

    @Slot(Fade)
    def setFadeDuration(self, fade: Fade) -> None:
        self._fade = fade
        self.player.setFade(fade)

    def getFadeDuration(self) -> Fade:
        return self._fade

    def getVolume(self) -> Volume:
        return self._volume

    @Slot(Volume)
    def setVolume(self, volume: Volume) -> None:
        self._volume = volume
        self.player.setVolume(volume)

    def getName(self) -> str:
        return self.cueInfo.name

    def getFullDescription(self) -> str:
        return QFileInfo(self._filename).absoluteFilePath()

    @Slot(str)
    def setName(self, value: str) -> None:
        self._name = value
        self.cueInfo.name = value
        self.changedCue.emit(self.cueInfo)

    @Slot(str)
    def changeMediaFile(self, fileName: str) -> None:
        self.stop()
        self.setSource(fileName)

    def __str__(self) -> str:
        return f'{self.getName()}'
