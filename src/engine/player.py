from enum import Enum
from typing import Optional
import logging

from pyaudio import PyAudio
from pydub import AudioSegment
from PySide6.QtCore import QObject, QThread, Signal

logger = logging.getLogger(__name__)


class PlayerStates (Enum):
    NotStarted = 0
    Playing = 1
    Paused = 2
    Stopped = 3
    Ended = 4


class Player (QThread):

    elapsedTime = Signal(int, name='elapsedTime')
    changedState = Signal(PlayerStates, name='changedState')
    CHUNK_SIZE = 100.0

    def __init__(self, audio: AudioSegment, startsAt: float, endsAt: float, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._audio = audio
        self._pause = False
        self._player = PyAudio()
        self._stream = self._player.open(
            format=self._player.get_format_from_width(self._audio.sample_width),
            channels=self._audio.channels,
            rate=self._audio.frame_rate,
            output=True,
        )
        self._playerOldState = None
        self._playerState = None
        self._startsAt = round(startsAt * 1000)
        self._endsAt = round(endsAt * 1000)
        # Start playing at start cursor
        self._elapsedTime = self._startsAt
        self.setPlayerState(PlayerStates.NotStarted)

    def setPlayerState(self, state: PlayerStates) -> None:
        self._playerState = state
        if self._playerOldState != self._playerState:
            self._playerOldState = state
            self.changedState.emit(self._playerState)

    def run(self):
        try:
            logger.debug(f'Playing from {self._startsAt}ms to {self._endsAt}ms')
            while not self.isInterruptionRequested():
                if not self._pause:
                    if self._elapsedTime >= self._endsAt:
                        self.setPlayerState(PlayerStates.Ended)
                        self.requestInterruption()
                    else:
                        segmentSize = min(self._endsAt, self._elapsedTime+self.CHUNK_SIZE)
                        data = self._audio[self._elapsedTime:segmentSize]
                        self.elapsedTime.emit(len(data) + self._elapsedTime)
                        if len(data) == 0:
                            self.setPlayerState(PlayerStates.Ended)
                            self.requestInterruption()
                        else:
                            self.setPlayerState(PlayerStates.Playing)
                            self._stream.write(data.raw_data)
                            self._elapsedTime += self.CHUNK_SIZE
                else:
                    self.setPlayerState(PlayerStates.Paused)
                    self.msleep(50)
        finally:
            self._stream.stop_stream()
            self._stream.close()
            self._player.terminate()

    def pause(self):
        self._pause = True

    def start(self):
        if self.isRunning():
            self._pause = False
        elif self.isFinished():
            # Thread already finished, nothing to do
            return
        else:
            super().start()

    def stop(self):
        if self._playerState != PlayerStates.Ended:
            self.setPlayerState(PlayerStates.Stopped)
            self.requestInterruption()

    
