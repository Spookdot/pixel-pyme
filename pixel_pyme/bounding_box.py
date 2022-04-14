from .dict_types import Position


class BoundingBox:
    def __init__(self, left: int, top: int, right: int, bottom: int):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __getitem__(self, key) -> int:
        return self.into_tuple()[key]

    def __setitem__(self, key, value):
        match key:
            case 0:
                self.left = value
            case 1:
                self.top = value
            case 2:
                self.right = value
            case 3:
                self.bottom = value
            case _:
                raise IndexError("Invalid index")

    @classmethod
    def from_position(cls, pos: Position):
        return cls(pos['box_left'], pos['box_top'], pos['box_right'], pos['box_bottom'])

    @classmethod
    def from_tuple(cls, tup: tuple[int, int, int, int]):
        return cls(tup[0], tup[1], tup[2], tup[3])

    @classmethod
    def from_float_tuple(cls, tup: tuple[float, float, float, float], size: tuple[int, int]):
        return cls(int(tup[0] * size[0]), int(tup[1] * size[1]), int(tup[2] * size[0]), int(tup[3] * size[1]))

    def into_tuple(self) -> tuple[int, int, int, int]:
        return self.left, self.top, self.right, self.bottom

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top
