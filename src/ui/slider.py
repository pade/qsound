from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLineEdit, QSizePolicy, QLabel
from PySide6.QtCore import Qt, Slot
from typing import Optional
from designer.slider import Ui_baseSlider


class BaseSlider(QWidget, Ui_baseSlider):

    MAX = 1
    MIN = 0

    def __init__(self, label: str = None, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        self.setupUi(self)
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        if label:
            self.label.setText(label)
        self.slider.setMaximum(self.MAX)
        self.slider.setMinimum(self.MIN)
        self.slider.valueChanged.connect(self.setLabelValue)
        self.valueEdit.textEdited.connect(self.setSliderValue)

    @Slot(int)
    def setSliderValue(self, value: str):
        self.slider.setValue(int(value))

    @Slot(int)
    def setLabelValue(self, value: int):
        self.valueEdit.setText(str(value))

    @Slot(int)
    def setValue(self, value):
        self.slider.setValue(value)

    def value(self):
        return self.slider.value()

