from enum import Enum
from typing import Optional

from pyaudio import PyAudio
from pydub import AudioSegment
from PySide6.QtCore import QObject, QThread, Signal


class PlayerStates (Enum):
    NotStarted = 0
    Playing = 1
    Paused = 2
    Stopped = 3
    Ended = 4


class Player (QThread):

    elapsedTime = Signal(int, name='elapsedTime')
    changedState = Signal(PlayerStates, name='changedState')
    CHUNK_SIZE = 100

    def __init__(self, audio: AudioSegment, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._elapsedTime = 0
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
        self.setPlayerState(PlayerStates.NotStarted)

    def setPlayerState(self, state: PlayerStates) -> None:
        self._playerState = state
        if self._playerOldState != self._playerState:
            self._playerOldState = state
            self.changedState.emit(self._playerState)

    def getPlayerState(self) -> PlayerStates:
        return self._playerState

    def run(self):
        try:
            while not self.isInterruptionRequested():
                if not self._pause:
                    data = self._audio[self._elapsedTime:self._elapsedTime+self.CHUNK_SIZE]
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
        if self.getPlayerState() != PlayerStates.Ended:
            self.setPlayerState(PlayerStates.Stopped)
            self.requestInterruption()
