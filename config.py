from enum import Enum
FIELD_SIZE = 6

CIRCLE_CELLS = [
    [(-1, -1), (-1, 0), (-1, 1)],
    [(0, -1), (0, 0), (0, 1)],
    [(1, -1), (1, 0), (1, 1)],
]

ADJACENT_CELLS = [
    (-1, 0), (1, 0), (0, -1), (0, 1)
]

SHIPS_COUNT = {
    3: 1,
    2: 2,
    1: 4,
}


class Symbols(Enum):
    empty: str = 'O'
    ship: str = '■'
    hit: str = 'X'
    miss: str = 'T'
    contour: str = '◦'
    v_contour: str = '•'

