from PySide6.QtWidgets import QWidget, QTabWidget
from PySide6.QtCore import Qt
from typing import Optional
from ui.volumewidget import VolumeWidget


class AudioCueWidget (QWidget):
    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        self._tab = QTabWidget(self)
        self.volume = VolumeWidget()
        self._tab.addTab(self.volume, self.tr('Volume'))


