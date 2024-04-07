import random
from typing import Literal, List, Dict

from errors import *
from config import *


class Dot:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

        self.validation_init_values()

    def validation_init_values(self):
        """
        Валидация значений в конструкторе.

        :return:
        """
        if self.x < 0 or self.y < 0:
            raise BattleShipsInvalidValueError('Значения координат не могут быть меньше 1.')
        if self.x >= FIELD_SIZE or self.y >= FIELD_SIZE:
            raise BattleShipsOutRangeError('Значения координат не могут быть больше размера игрового поля.')

    def __eq__(self, other):
        return True if self.x == other.x and self.y == other.y else False

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    def __init__(self, length: int, start_dot: Dot, direction: Literal['h', 'v'], health: int):
        self.length: int = length
        self.start_dot: Dot = start_dot
        self.direction: str = direction
        self.health: int = health

        self.validation_init_values()

    def validation_init_values(self):
        """
        Валидация значений в конструкторе.

        :return:
        """

        if self.length > 3:
            raise BattleShipsOutRangeError('Корабль не может занимать больше 3-х клеток.')
        if self.length < 1:
            raise BattleShipsInvalidValueError('Корабль не может иметь длину меньше 1.')

        if self.direction == 'h':
            if self.start_dot.x + self.length - 1 > FIELD_SIZE:
                raise BattleShipsOutRangeError(
                    'Корабль не может выходить за пределы поля'
                )
        else:
            if self.start_dot.y + self.length - 1 > FIELD_SIZE:
                raise BattleShipsOutRangeError(
                    'Корабль не может выходить за пределы поля'
                )

        if self.health > self.length:
            raise BattleShipsInvalidValueError(
                'У корабля не может быть больше ХП, чем количество занимаемых им клеток.'
            )
        if self.health < 0:
            raise BattleShipsInvalidValueError(
                'Количество ХП корабля не может быть меньше нуля.'
            )

    def dots(self):
        """
        Возвращает список всех точек, на которых находится корабль
        :return:
        """
        return [
            Dot(self.start_dot.x + i, self.start_dot.y) if self.direction == 'h' else
            Dot(self.start_dot.x, self.start_dot.y + i) for i in range(self.length)
        ]


class Board:
    def __init__(self, _hid: bool):
        self.cell_states: List[List[Symbols]] = [
            [Symbols.empty.value for i in range(FIELD_SIZE)] for i in range(FIELD_SIZE)
        ]
        self.ships: List[Ship] = []
        self.hid: bool = _hid
        self.living_ships_cnt: int = 0

    def add_ship(self, ship: Ship):
        """
        Метод добавления корабля на игровое поле.

        :param ship: Класс корабля.
        :return:
        """
        def check_circle_cells(_dot: Dot) -> bool:
            """
            Проверка на наличие занятых клеток вокруг заданной точки.

            :param _dot: Точка, вокруг которой проверяются клетки на занятость.
            :return: True, если клетки свободны.
            """
            for row in CIRCLE_CELLS:
                for elem in row:
                    try:
                        if _dot.y + elem[0] < 0 or _dot.x + elem[1] < 0:
                            raise IndexError
                        if self.cell_states[_dot.y + elem[0]][_dot.x + elem[1]] == Symbols.ship.value:
                            return False
                    except IndexError:
                        continue
            return True

        on_add = True
        max_count_ships = sum(SHIPS_COUNT.values())
        if self.living_ships_cnt > max_count_ships:
            raise BattleShipsAlreadyShotError()

        for dot in ship.dots():
            if not check_circle_cells(dot):
                on_add = False

        if on_add:
            for dot in ship.dots():
                self.contour(dot)
                self.cell_states[dot.y][dot.x] = Symbols.ship.value
        else:
            raise BattleShipsCellIsBusyError('Одна или несколько ячеек заняты, выберите другие координаты корабля.')

        self.living_ships_cnt += 1
        self.ships.append(ship)

    def contour(self, _dot: Dot, vision: bool = False):
        """
        Метод обводит контуром корабль.

        :param _dot: Координаты точки которую нужно обвести контуром.
        :param vision: Если True, то обводит корабли точками, которые выводятся (для кораблей игрока).
        :return:
        """
        for row in CIRCLE_CELLS:
            for elem in row:
                try:
                    if (_dot.y + elem[0] < 0 or _dot.x + elem[1] < 0 or
                            _dot.y + elem[0] > FIELD_SIZE - 1 or _dot.x + elem[1] > FIELD_SIZE - 1):
                        raise IndexError
                    if self.cell_states[_dot.y + elem[0]][_dot.x + elem[1]] not in [
                        Symbols.empty.value,
                        Symbols.contour.value,
                    ]:
                        continue
                    if vision:
                        self.cell_states[_dot.y + elem[0]][_dot.x + elem[1]] = Symbols.v_contour.value
                    else:
                        self.cell_states[_dot.y + elem[0]][_dot.x + elem[1]] = Symbols.contour.value
                except IndexError:
                    continue

    def shot(self, _dot: Dot) -> bool:
        """
        Метод описывает алгоритм проверки выстрела по доске.

        :param _dot: Координаты выстрела.
        :return: True, если выстрел попал.
        """
        if self.cell_states[_dot.y][_dot.x] == Symbols.ship.value:
            for _ship in self.ships:
                if _dot in _ship.dots():
                    _ship.health -= 1
                    self.cell_states[_dot.y][_dot.x] = Symbols.hit.value
                    if _ship.health == 0:
                        for _coord in _ship.dots():
                            self.contour(_coord, True)
                            self.cell_states[_dot.y][_dot.x] = Symbols.hit.value
                        self.living_ships_cnt -= 1
                    return True

        elif self.cell_states[_dot.y][_dot.x] in [
            Symbols.empty.value,
            Symbols.contour.value,
            Symbols.v_contour.value,
        ]:
            self.cell_states[_dot.y][_dot.x] = Symbols.miss.value
            return False
        else:
            raise BattleShipsAlreadyShotError()

    def show(self):
        """
        Метод выводит в консоль текущее поле.

        :return:
        """
        for i in range(FIELD_SIZE + 1):
            row = []
            for j in range(FIELD_SIZE + 1):
                if j == 0 and i == 0:
                    row.append(' ')
                    continue
                if j == 0:
                    row.append(str(i))
                    continue
                if i == 0:
                    row.append(str(j))
                else:
                    if self.hid and self.cell_states[i - 1][j - 1] in [
                        Symbols.ship.value,
                        Symbols.contour.value,
                    ]:
                        row.append(Symbols.empty.value)
                    else:
                        row.append(self.cell_states[i - 1][j - 1])
            print('|'.join(row))


class Player:
    def __init__(self, _board: Board, _enemy_board: Board):
        self.board = _board
        self.enemy_board = _enemy_board

    def ask(self) -> bool:
        """
        Запрос на выстрел.

        :return: True, если выстрел попал.
        """
        ...

    def move(self) -> bool:
        """
        Метод описывает ход игрока.

        :return: True, если требуется еще один выстрел.
        """
        try:
            result = self.ask()
            if result:
                return True
            else:
                return False
        except Exception:
            raise


class User(Player):
    def ask(self) -> bool:
        target_is_valid = False
        _x, _y = (0, 0)
        while not target_is_valid:
            target = str(input('Введите координаты точки: '))

            try:
                _x, _y = [int(el) for el in target.split(' ')]
                target_is_valid = True
            except ValueError:
                print('Неверный формат координат, введите координаты типа: "1 2", без кавычек.')

        return self.enemy_board.shot(Dot(_x - 1, _y - 1))


class AI(Player):
    shot_dots: List[Dot] = []
    shot_state: List[Literal['hit', 'miss']] = []

    def ask(self):
        def check_prev_hit() -> bool:
            try:
                if self.shot_state[-1] == 'hit':
                    return True
                else:
                    return False
            except IndexError:
                return False

        _x, _y = (0, 0)
        count_failed = 0
        while True:
            random.seed()
            if check_prev_hit() and count_failed < 5:
                _x = self.shot_dots[-1].x
                _y = self.shot_dots[-1].y

                adj_cell = ADJACENT_CELLS[random.randrange(0, 4, 1)]
                _x += adj_cell[0]
                _y += adj_cell[1]

                try:
                    _dot = Dot(_x - 1, _y - 1)
                except (BattleShipsInvalidValueError, BattleShipsOutRangeError):
                    count_failed += 1
                    continue
            else:
                _x = random.randrange(1, FIELD_SIZE, 1)
                _y = random.randrange(1, FIELD_SIZE, 1)

                _dot = Dot(_x - 1, _y - 1)

            if _dot not in self.shot_dots:
                self.shot_dots.append(_dot)
                result = self.enemy_board.shot(_dot)

                if result:
                    self.shot_state.append('hit')
                else:
                    self.shot_state.append('miss')

                return result


class Game:
    def __init__(self):
        self.user_board = self.random_board(Board(False))
        self.ai_board = self.random_board(Board(True))

        self.user = User(self.user_board, self.ai_board)
        self.ai = AI(self.ai_board, self.user_board)

    @staticmethod
    def random_board(board: Board) -> Board:
        is_created = False
        while not is_created:
            count_failed = 0
            board = Board(board.hid)
            for ship_conf in SHIPS_COUNT:
                for ship_count in range(SHIPS_COUNT[ship_conf]):
                    is_apply = False
                    while not is_apply:
                        _x = random.randrange(1, FIELD_SIZE, 1)
                        _y = random.randrange(1, FIELD_SIZE, 1)
                        direction = random.choice(['h', 'v'])
                        ship_coord = Dot(_x - 1, _y - 1)

                        try:
                            ship = Ship(
                                ship_conf,
                                ship_coord,
                                direction,
                                ship_conf,
                            )
                            board.add_ship(ship)
                            is_apply = True
                        except (BattleShipsCellIsBusyError, BattleShipsOutRangeError):
                            count_failed += 1
                            if count_failed > 50:
                                break
                            continue
            if len(board.ships) == sum(SHIPS_COUNT.values()):
                return board

    @staticmethod
    def greet():
        print('''
            Добро пожаловать в Морской Бой.
            
            Вам предстоит сразиться с компьютером на морском поле боя.
            
            Поле боя представляет собой координатную сетку, по горизонтали - x, по вертикали - y.
            
             |1|2|3|4|5|6 <-- координаты x
            1|■|■|■|◦|■|◦
            2|◦|◦|◦|◦|◦|◦
            3|■|◦|■|◦|■|◦
            4|◦|◦|◦|◦|◦|◦
            5|■|■|◦|◦|■|■
            6|◦|◦|◦|◦|◦|◦
            ^
            |
            координаты y
            
            Координаты выстрела вводятся через пробел: "x, y", без кавычек.
            Если введены неверные значения, например выходящие за пределы поля или в место попадания или промаха,
            вас попросят ввести другие координаты.
            
            Удачи!
        ''')

    def loop(self):
        is_game = True
        move = 0
        while is_game:
            if move == 0:
                print('Ход игрока')
                try:
                    result = self.user.move()
                except BattleShipsAlreadyShotError:
                    print('В эту точку уже был выстрел, выберите другую.')
                    continue
                except BattleShipsInvalidValueError:
                    print('Значения координат выходят за пределы поля, выберите другую точку.')
                    continue
            else:
                print('Ход компьютера')
                result = self.ai.move()

            if result:
                print('Есть пробитие!!!')
            else:
                print('Промах!!!')
                if move == 0:
                    move = 1
                else:
                    move = 0

            print('-----ДОСКА ИГРОКА-----')
            self.user_board.show()
            print('---ДОСКА КОМПЬЮТЕРА---')
            self.ai_board.show()
            print('----------------------')

            if self.user_board.living_ships_cnt == 0:
                print('Победил компьютер!')
                is_game = False

            if self.ai_board.living_ships_cnt == 0:
                print('Победил игрок!')
                is_game = False

    def start(self):
        self.greet()
        _start = input('Начать игру? Введите "y" для начала игры: ')
        if _start == 'y':
            print('-----ДОСКА ИГРОКА-----')
            self.user_board.show()
            print('---ДОСКА КОМПЬЮТЕРА---')
            self.ai_board.show()
            self.loop()


def main():
    game = Game()
    game.start()


if __name__ == '__main__':
    main()
