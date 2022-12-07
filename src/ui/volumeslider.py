from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Slot, QObject
from PySide6.QtGui import QValidator
from typing import Optional
from ui.slider import BaseSlider


class SliderValidator(QValidator):
    def __init__(self, min, max, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.min = min
        self.max = max

    def validate(self, value, nbChar):
        try:
            if nbChar == 0:
                return QValidator.State.Intermediate
            if nbChar > 5:
                return QValidator.State.Invalid
            if value == '-':
                return QValidator.State.Intermediate
            value = round(float(value) * 10)
            if value < self.min or value > self.max:
                return QValidator.State.Invalid
            return QValidator.State.Acceptable
        except ValueError:
            return QValidator.State.Invalid


class VolumeSlider (BaseSlider):
    MAX = 200
    MIN = -500

    def __init__(self, label: str = None, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(label, parent, f)
        self.slider.setTickInterval(100)
        self.slider.setValue(0)
        self.valueEdit.setText('0.0')
        self.valueEdit.setValidator(SliderValidator(self.MIN, self.MAX))

    @Slot(int)
    def setSliderValue(self, value: str):
        try:
            self.slider.setValue(round(int(value) * 10))
        except ValueError:
            # Value is not an integer, do not update slider
            pass

    @Slot(int)
    def setLabelValue(self, value):
        if value <= self.MIN:
            value = '-\u221E'
        else:
            value = value / 10.0
        self.valueEdit.setText(str(value))
        self.adjustSize()
