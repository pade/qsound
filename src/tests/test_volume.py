import unittest
from cue.volume import Volume


class TestVolume (unittest.TestCase):
    def setUp(self) -> None:
        self.__volume = Volume()
        return super().setUp()

    def test_getDefaultVolume(self):
        self.assertEqual(self.__volume.left, 0.0)
        self.assertEqual(self.__volume.right, 0.0)

    def test_setVolume(self):
        self.__volume.left = 2.3
        self.__volume.right = 1.5
        self.assertEqual(self.__volume.left, 2.3)
        self.assertEqual(self.__volume.right, 1.5)

    def test_setNegativeVolume(self):
        self.__volume.left = -2.3
        self.__volume.right = -1.5
        self.assertEqual(self.__volume.getVolume(), (0.0, 0.0))

    def test_getVolume(self):
        self.__volume.left = 1.8
        self.__volume.right = 2.6
        self.assertEqual(self.__volume.getVolume(), (1.8, 2.6))
