from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Slot
from typing import Optional
from ui.slider import BaseSlider


class VolumeSlider (BaseSlider):
    MAX = 20
    MIN = -50

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        self.slider.setMaximum(self.MAX)
        self.slider.setMinimum(self.MIN)
        self.slider.setValue(0)
        self.label.setText('0')

    @Slot(int)
    def setLabelValue(self, value):
        if value <= self.MIN:
            value = '-\u221E'
        self.label.setText(str(value))
        self.adjustSize()