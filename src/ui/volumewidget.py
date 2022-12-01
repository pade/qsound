from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal, Slot
from typing import Optional
from ui.volumeslider import VolumeSlider
from cue.volume import Volume


class VolumeWidget (QWidget):

    volume = Signal(Volume, name='volumeChanged')

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        self.left = VolumeSlider()
        self.right = VolumeSlider()
        hbox.addWidget(self.left)
        hbox.addWidget(self.right)
        self.right.slider.valueChanged.connect(self._volumeChange)
        self.left.slider.valueChanged.connect(self._volumeChange)

    @Slot(Volume)
    def setVolume(self, volume: Volume):
        self.left.slider.setValue(volume.getVolume()[0])
        self.right.slider.setValue(volume.getVolume()[1])

    @Slot()
    def _volumeChange(self):
        self.volume.emit(Volume(self.left.value(), self.right.value()))

