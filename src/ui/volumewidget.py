from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QSizePolicy
from PySide6.QtCore import Qt, Signal, Slot
from typing import Optional
from ui.volumeslider import VolumeSlider
from cue.volume import Volume


class VolumeWidget (QWidget):

    volume = Signal(Volume, name='volumeChanged')

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        vBox = QVBoxLayout()
        hBox = QHBoxLayout()
        self.setLayout(vBox)
        self.left = VolumeSlider(self.tr('L'))
        self.right = VolumeSlider(self.tr('R'))
        hBox.addWidget(self.left, 0, Qt.AlignmentFlag.AlignLeft)
        hBox.addWidget(self.right, 0, Qt.AlignmentFlag.AlignLeft)
        self.right.slider.valueChanged.connect(self._volumeChange)
        self.left.slider.valueChanged.connect(self._volumeChange)
        self.checkBox = QCheckBox()
        self.checkBox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.checkBox.setText(self.tr('Split channels'))
        self.checkBox.stateChanged.connect(self._setSeparate)
        self.checkBox.setChecked(True)
        vBox.addWidget(self.checkBox, 0, Qt.AlignmentFlag.AlignCenter)
        vBox.addLayout(hBox)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    @Slot()
    def _setSeparate(self):
        if self.checkBox.isChecked():
            self.left.slider.disconnect(self.right.slider)
            self.left.label.setText(self.tr('L'))
            self.right.setEnabled(True)
        else:
            self.right.setEnabled(False)
            self.left.label.setText(self.tr('Master'))
            self.left.slider.valueChanged.connect(self.right.slider.setValue)

    @Slot(Volume)
    def setVolume(self, volume: Volume):
        self.left.slider.setValue(round(volume.left * 10))
        self.right.slider.setValue(round(volume.right * 10))
        self.checkBox.setChecked(volume.separate)

    @Slot()
    def _volumeChange(self):
        self.volume.emit(Volume(self.checkBox.isChecked(), self.left.value() / 10.0, self.right.value() / 10.0))

