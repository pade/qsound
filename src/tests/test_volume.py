from cue.volume import Volume


class TestVolume:
    def setup_class(self) -> None:
        self.volume = Volume()

    def test_getDefaultVolume(self):
        assert self.volume.master == 0.0
        assert self.volume.left == 0.0
        assert self.volume.right == 0.0

    def test_setVolume(self):
        self.volume.left = 2.3
        self.volume.right = 1.5
        self.volume.master = 4.5
        assert self.volume.left == 2.3
        assert self.volume.right == 1.5
        assert self.volume.master == 4.5 

    def test_setVolumeOutOfLowRange(self):
        self.volume.left = Volume.MIN - 2.3
        self.volume.right = Volume.MIN - 1.5
        self.volume.master = Volume.MIN - 10
        assert self.volume.getVolume() == (Volume.MIN, Volume.MIN, Volume.MIN)

    def test_setVolumeOutOfUpperRange(self):
        self.volume.left = Volume.MAX + 2.3
        self.volume.right = Volume.MAX + 1.5
        self.volume.master = Volume.MAX + 10
        assert self.volume.getVolume() == (Volume.MAX, Volume.MAX, Volume.MAX)

    def test_getVolume(self):
        self.volume.left = 1.8
        self.volume.right = 2.6
        self.volume.master = 5.0
        assert self.volume.getVolume() == (5.0, 1.8, 2.6)

    def test_printVolume(self):
        self.volume.left = 2.9
        self.volume.right = 3.8
        self.volume.master = 4.2
        assert f'{self.volume}' == '4.2 [2.9 / 3.8]'
