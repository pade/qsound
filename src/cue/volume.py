class Volume:
    def __init__(self, left: float = 0.0, right: float = 0.0) -> None:
        self.__left = left
        self.__right = right

    @property
    def left(self) -> float:
        return self.__left

    @left.setter
    def left(self, value: float) -> None:
        self.__left = value

    @property
    def right(self) -> float:
        return self.__right

    @right.setter
    def right(self, value: float) -> None:
        self.__right = value

    def getVolume(self) -> tuple[float, float]:
        return (self.left, self.right)

    def __str__(self) -> str:
        return f'left: {self.left}, right: {self.right}'
