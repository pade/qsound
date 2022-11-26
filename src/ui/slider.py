from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel
from PySide6.QtCore import Qt, Slot
from typing import Optional


class Slider(QWidget):

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        vBox.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setTickPosition(QSlider.TickPosition.TicksLeft)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.label = QLabel()
        self.setLabelValue(0)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        vBox.addWidget(self.slider)
        vBox.addWidget(self.label)
        self.slider.valueChanged.connect(self.setLabelValue)

    @Slot(int, result=str)
    def setLabelValue(self, value):
        self.label.setText(f'{value}%')
        self.label.adjustSize()

    @Slot(int, result=int)
    def setValue(self, value):
        self.slider.setValue(value)
    
    def value(self):
        return self.slider.value()

