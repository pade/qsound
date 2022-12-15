from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QSizePolicy, QLabel, QSpacerItem, QLineEdit
from PySide6.QtCore import Qt, Signal, Slot, QObject
from PySide6.QtGui import QValidator
from typing import Optional
from ui.volumeslider import VolumeSlider
from cue.volume import Volume
from cue.fade import Fade
from ui.fadewidget import FadeWidget
from designer.volume import Ui_Volume

import logging

logger = logging.getLogger(__name__)


class VolumeValidator(QValidator):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)

    def validate(self, value: str, nbChar: int) -> object:
        try:
            if nbChar == 0:
                return QValidator.State.Intermediate
            if nbChar > 5:
                return QValidator.State.Invalid
            if value == '-':
                return QValidator.State.Intermediate
            value = round(float(value) * 10)
            if value < Volume.MIN or value > Volume.MAX:
                return QValidator.State.Invalid
            return QValidator.State.Acceptable
        except ValueError:
            return QValidator.State.Invalid


class VolumeWidget (QWidget, Ui_Volume):

    volumeChanged = Signal(Volume, name='volumeChanged')
    fadeChanged = Signal(Fade, name='fadeChanged')

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        self.setupUi(self)
        self.leftSlider.valueChanged.connect(self._volumeChange)
        self.leftSlider.valueChanged.connect(self._setLeftEditValue)
        self.rightSlider.valueChanged.connect(self._volumeChange)
        self.rightSlider.valueChanged.connect(self._setRightEditValue)
        self.masterSlider.valueChanged.connect(self._volumeChange)
        self.masterSlider.valueChanged.connect(self._setMasterEditValue)

        self.fadeInEdit.editingFinished.connect(self._setFade)
        self.fadeOutEdit.editingFinished.connect(self._setFade)

        self.masterEdit.editingFinished.connect(self._setMasterSliderValue)
        self.leftEdit.editingFinished.connect(self._setLeftSliderValue)
        self.rightEdit.editingFinished.connect(self._setRightSliderValue)
        self.masterEdit.setValidator(VolumeValidator())
        self.leftEdit.setValidator(VolumeValidator())
        self.rightEdit.setValidator(VolumeValidator())

    @Slot(Volume)
    def setVolume(self, volume: Volume):
        self.leftSlider.setValue(round(volume.left * 10))
        self.rightSlider.setValue(round(volume.right * 10))
        self.masterSlider.setValue(round(volume.master * 10))

    def setFade(self, fade: Fade):
        fadeIn = min(99.99, fade.fadeIn)
        fadeOut = min(99.99, fade.fadeOut)
        self.fadeInEdit.setText(str(fadeIn).replace('.', ':'))
        self.fadeOutEdit.setText(str(fadeOut).replace('.', ':'))

    @Slot()
    def _setMasterSliderValue(self):
        self.masterSlider.setValue(round(int(self.masterEdit.text()) * 10))

    @Slot()
    def _setLeftSliderValue(self):
        self.leftSlider.setValue(round(int(self.leftEdit.text()) * 10))

    @Slot()
    def _setRightSliderValue(self):
        self.rightSlider.setValue(round(int(self.rightEdit.text()) * 10))

    @Slot(int)
    def _setMasterEditValue(self, value: int):
        self.masterEdit.setText(self._convertVolumeToString(value))

    @Slot(int)
    def _setLeftEditValue(self, value: int):
        self.leftEdit.setText(self._convertVolumeToString(value))

    @Slot(int)
    def _setRightEditValue(self, value: int):
        self.rightEdit.setText(self._convertVolumeToString(value))

    def _convertVolumeToString(self, value: int):
        if value <= Volume.MIN:
            return '-\u221E'
        else:
            return str(value / 10.0)

    @Slot()
    def _setFade(self):
        try:
            self.fadeChanged.emit(
                Fade(float(self.fadeInEdit.text().replace(':', '.')), float(self.fadeOutEdit.text().replace(':', '.')))
            )
        except ValueError:
            logger.error(f'Invalid fade value: "{self.fadeInEdit.text()}" or "{self.fadeOutEdit.text()}"')

    @Slot()
    def _volumeChange(self):
        self.volumeChanged.emit(Volume(self.masterSlider.value() / 10.0, self.leftSlider.value() / 10.0, self.rightSlider.value() / 10.0))

