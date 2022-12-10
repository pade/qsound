from typing import Optional
from designer.fade import Ui_FadeWidget
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Slot, Signal, QLocale
from PySide6.QtGui import QDoubleValidator, QValidator
from cue.fade import Fade
import logging

logger = logging.getLogger(__name__)


class FadeValidator (QDoubleValidator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBottom(0.0)
        self.setDecimals(2)
        self.setNotation(QDoubleValidator.Notation.StandardNotation)
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        self.setLocale(locale)

    def validate(self, value: str, nbChar: int) -> object:
        if not nbChar:
            value = '0.0'
        if ',' in value:
            return QValidator.State.Invalid
        return super().validate(value, nbChar)


class FadeWidget(QWidget, Ui_FadeWidget):

    valueChanged = Signal(Fade, name='valueChanged')

    def __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Qt.WindowType.Widget) -> None:
        super().__init__(parent, f)
        self.fadeValues = Fade(0.0, 0.0)
        self.setupUi(self)

    def setupUi(self, FadeWidget):
        super().setupUi(FadeWidget)
        self.fadeInEdit.setText('0.0')
        self.fadeOutEdit.setText('0.0')
        self.fadeInEdit.setValidator(FadeValidator())
        self.fadeOutEdit.setValidator(FadeValidator())
        self.fadeInEdit.editingFinished.connect(self.setFade)
        self.fadeOutEdit.editingFinished.connect(self.setFade)

    @Slot()
    def setFade(self):
        try:
            self.fadeValues.fadeIn = float(self.fadeInEdit.text())
            self.fadeValues.fadeOut = float(self.fadeOutEdit.text())
            self.valueChanged.emit(self.fadeValues)
        except ValueError:
            logger.debug(f'Invalid fade value: "{self.fadeInEdit.text()}" or "{self.fadeOutEdit.text()}"')
