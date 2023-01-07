from cue.basecue import BaseCue
from cue.audiocue import AudioCue
from PySide6.QtCore import Slot


class CueListItem:
    def __init__(self, cue: BaseCue) -> None:
        self._cue = cue
        self.data = ['' for _ in range(6)]
        self.setValue()

    @Slot()
    def setValue(self) -> None:
        self.data[0] = ''
        self.data[1] = self._cue.getName()
        if isinstance(self._cue, AudioCue):
            fade = self._cue.getFadeDuration()
            self.data[2] = f'{fade.fadeIn:.02f}'
            self.data[3] = self._cue.cueInfo.formatDuration()
            self.data[4] = f'{fade.fadeOut:.02f}'
            self.data[5] = '\u21BA' if self._cue.getLoop() else ''
        else:
            self.data[2:6] = ['', '', '', '']

    def getFullDescription(self):
        return self._cue.getFullDescription()

    def getCue(self):
        return self._cue

    def getCueState(self):
        return self._cue.getCueState()
