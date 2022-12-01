from PySide6.QtWidgets import QWidget, QTabWidget, QSizePolicy
from PySide6.QtCore import Qt, QRect, Slot
from typing import Optional
from ui.volumewidget import VolumeWidget
from ui.soundwiget import Soundwidget


class AudioCueWidget (QWidget):
    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        self._tab = QTabWidget(self)
        self.volume = VolumeWidget()
        self.sound = Soundwidget()
        self._tab.addTab(self.volume, self.tr('Volume'))
        self._tab.addTab(self.sound, self.tr('Sound'))
        self._tab.currentChanged.connect(self.updateSizes)

    @Slot(int)
    def updateSizes(self, index: int) -> None:
        for i in range(self._tab.count()):
            if index != i:
                self._tab.widget(i).setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self._tab.widget(index).setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._tab.widget(index).adjustSize()
        self.resize(self.minimumSizeHint())
        self.adjustSize()




