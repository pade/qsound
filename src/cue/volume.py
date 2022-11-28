class Volume:
    def __init__(self, left: int = 0, right: int = 0) -> None:
        self.__left = left
        self.__right = right

    @property
    def left(self) -> int:
        return self.__left

    @left.setter
    def left(self, value: int) -> None:
        if value < 0:
            value = 0
        self.__left = value

    @property
    def right(self) -> int:
        return self.__right

    @right.setter
    def right(self, value: int) -> None:
        if value < 0:
            value = 0
        self.__right = value

    def getVolume(self) -> tuple[int, int]:
        return (self.left, self.right)

    def __str__(self) -> str:
        return f'left: {self.left}, right: {self.right}'
