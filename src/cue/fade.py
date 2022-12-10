class Fade:
    def __init__(self, fadeIn: float = 0.0, fadeOut: float = 0.0) -> None:
        self._fadeIn = fadeIn
        self._fadeOut = fadeOut

    @property
    def fadeIn(self) -> float:
        return self._fadeIn

    @fadeIn.setter
    def fadeIn(self, value: float) -> None:
        if value < 0.0:
            value = 0.0
        self._fadeIn = value

    @property
    def fadeOut(self) -> float:
        return self._fadeOut

    @fadeOut.setter
    def fadeOut(self, value: float) -> None:
        if value < 0.0:
            value = 0.0
        self._fadeOut = value

    def getFade(self) -> tuple[float, float]:
        return (self.fadeIn, self.fadeOut)

    def setFade(self, fadeIn: float, fadeOut: float) -> None:
        self.fadeIn = fadeIn
        self.fadeOut = fadeOut

    def __str__(self) -> str:
        return f'\u279A {self.fadeIn:.02f}, \u2798 {self.fadeOut:.02f}'
        
