from PySide6.QtCore import QObject, QUrl, QThread, Signal, Slot
from typing import Optional
from pyaudio import PyAudio
from pydub import AudioSegment
from pydub.utils import make_chunks


class Player (QThread):

    elapsedTime = Signal(int, name='elapsedTime')
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

    def run(self):
        try:
            while not self.isInterruptionRequested():
                if not self._pause:
                    data = self._audio[self._elapsedTime:self._elapsedTime+self.CHUNK_SIZE]
                    self.elapsedTime.emit(len(data) + self._elapsedTime)
                    if len(data) == 0:
                        self.requestInterruption()
                    else:
                        self._stream.write(data.raw_data)
                        self._elapsedTime += self.CHUNK_SIZE
                else:
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
        self.requestInterruption()

    # def _loaded_frames(self, dataIn, frameCount, timeInfo, status):
    #     print(f'frameCount: {frameCount}')
    #     print(f'timeInfo: {timeInfo}')
    #     print(f'status: {status}')
    #     time = (frameCount / self.audio.frame_rate) * 1000.0
    #     print(f'time: {time}')
    #     data = self.audio[:time].raw_data
    #     self.audio = self.audio[time:]
    #     return (data, paContinue)
