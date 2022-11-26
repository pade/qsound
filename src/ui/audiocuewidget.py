from PySide6.QtWidgets import QWidget, QTabWidget
from PySide6.QtCore import Qt
from typing import Optional
from ui.volumewidget import VolumeWidget
from PySide6.QtCore import Slot
from cue.volume import Volume


class AudioCueWidget (QWidget):
    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        self._tab = QTabWidget(self)
        self.volume = VolumeWidget()
        self._tab.addTab(self.volume, self.tr('Volume'))
        self.volume.volumeChanged.connect(self.newVolume)

    @Slot(Volume)
    def newVolume(self, volume):
        print(volume)

