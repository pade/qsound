import unittest
from cue.audiocue import AudioCue
from pathlib import Path


class TestAudioCue (unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.__dir = Path(__file__).parent

    def test_loadFile(self):
        fullpath = Path(self.__dir, './sample-1.mp3')
        audio = AudioCue(str(fullpath))
        self.assertTrue(audio.isValid())