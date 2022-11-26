from PySide6.QtMultimedia import QAudioOutput, QMediaFormat, QMediaPlayer
from PySide6.QtCore import QUrl, QThread
import time

player = QMediaPlayer()
audioOutput = QAudioOutput()
player.setAudioOutput(audioOutput)
player.setSource(QUrl.fromLocalFile('./sample-1.wav'))
audioOutput.setVolume(0.5)
player.play()
