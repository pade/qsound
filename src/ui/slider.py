from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLineEdit
from PySide6.QtCore import Qt, Slot
from typing import Optional


class BaseSlider(QWidget):

    MAX = 1
    MIN = 0

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        vBox.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setTickPosition(QSlider.TickPosition.TicksLeft)
        self.slider.setMaximum(self.MAX)
        self.slider.setMinimum(self.MIN)
        self.label = QLineEdit()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vBox.addWidget(self.slider)
        vBox.addWidget(self.label)
        vBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider.valueChanged.connect(self.setLabelValue)
        self.label.textEdited.connect(self.setSliderValue)

    @Slot(int)
    def setSliderValue(self, value: str):
        self.slider.setValue(int(value))

    @Slot(int)
    def setLabelValue(self, value: int):
        self.label.setText(str(value))
        self.label.adjustSize()

    @Slot(int)
    def setValue(self, value):
        self.slider.setValue(value)
    
    def value(self):
        return self.slider.value()

