from PySide6.QtCore import QObject, QUrl, QThread, Signal, Slot
from typing import Optional
from pyaudio import PyAudio, paContinue
from pydub import AudioSegment
from pydub.utils import make_chunks


class Player (QThread):

    reader = Signal(int, name="elapsedTime")

    def __init__(self, filename: QUrl, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._elapsedTime = 0
        self._filename = filename

    def _setUp(self, filename: QUrl) -> None:
        self._audio = AudioSegment.from_file(filename.toLocalFile())
        self.player = PyAudio()
        self._stream = self.player.open(
            format=self.player.get_format_from_width(self._audio.sample_width),
            channels=self._audio.channels,
            rate=self._audio.frame_rate,
            output=True,
            # stream_callback=self._loaded_frames
        )

    def run(self):
        self._setUp(self._filename)
        try:
            for chunk in make_chunks(self._audio, 100):
                if self.isInterruptionRequested():
                    break
                self._stream.write(chunk.raw_data)
                self._elapsedTime += 100
                self.reader.emit(self._elapsedTime)

        finally:
            self._stream.stop_stream()
            self._stream.close()
            self.player.terminate()

    def pause(self):
        pass

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
