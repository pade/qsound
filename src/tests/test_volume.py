import unittest
from cue.volume import Volume


class TestVolume (unittest.TestCase):
    def setUp(self) -> None:
        self.volume = Volume()
        return super().setUp()

    def test_getDefaultVolume(self):
        self.assertEqual(self.volume.left, 0.0)
        self.assertEqual(self.volume.right, 0.0)

    def test_setVolume(self):
        self.volume.left = 2.3
        self.volume.right = 1.5
        self.assertEqual(self.volume.left, 2.3)
        self.assertEqual(self.volume.right, 1.5)

    def test_setNegativeVolume(self):
        self.volume.left = -2.3
        self.volume.right = -1.5
        self.assertEqual(self.volume.getVolume(), (0.0, 0.0))

    def test_getVolume(self):
        self.volume.left = 1.8
        self.volume.right = 2.6
        self.assertEqual(self.volume.getVolume(), (1.8, 2.6))

    def test_printVolume(self):
        self.volume.left = 2.9
        self.volume.right = 3.8
        self.assertEqual(f'{self.volume}', 'left: 2.9, right: 3.8')
