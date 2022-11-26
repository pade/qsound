from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal, Slot
from typing import Optional
from ui.slider import Slider
from cue.volume import Volume


class VolumeWidget (QWidget):

    volume = Signal(Volume, name='volumeChanged')

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        self.left = Slider()
        self.right = Slider()
        hbox.addWidget(self.left)
        hbox.addWidget(self.right)
        self.right.slider.valueChanged.connect(self.setVolume)
        self.left.slider.valueChanged.connect(self.setVolume)

    @Slot(int)
    def setVolume(self, value):
        self.volume.emit(Volume(self.left.value(), self.right.value()))

