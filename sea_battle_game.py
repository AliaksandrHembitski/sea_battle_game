from random import randint


class BoardExcetion(Exception):
    pass


class IncorrectOrientationShip(BoardExcetion):
    """Неверная ориентация корабля."""
    pass


class BoardOutExcetion(BoardExcetion):
    """Выстрел за пределами игрового поля."""
    pass


class IncorrectCoordinateValue(BoardExcetion):
    """Неверное значение координат."""
    pass


class RepeatMove(BoardExcetion):
    """По этим координатам уже был сделан ход."""
    pass


class ImplementedInDescendants(BoardExcetion):
    """Правила наследования"""
    pass


# создание точки определяется координатами x и y
class Dot:
    def __init__(self, coor_x, coor_y):
        self.x = coor_x
        self.y = coor_y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f' Dot ({self.x}, {self.y})'


class Ship:
    def __init__(self, fore, length, direct=1):
        self.fore = fore
        self.length = length
        self.life = length
        self.direct = direct
        self.coor_dot_ship = [fore]

    def dots(self):
        while len(self.coor_dot_ship) != self.length:
            if self.direct == 1:
                self.coor_dot_ship.append(Dot(self.coor_dot_ship[-1].x, self.coor_dot_ship[-1].y + 1))
            elif self.direct == 0:
                self.coor_dot_ship.append(Dot(self.coor_dot_ship[-1].x + 1, self.coor_dot_ship[-1].y))
            else:
                raise IncorrectOrientationShip()
        return self.coor_dot_ship

    def shot(self, dot):
        return dot in self.dots()

    def __repr__(self):
        return f'{self.dots()}'


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size
        self.game_field = [["O"] * size for i in range(size)]
        self.num_wrecked_ships = 0
        self.coor_dot_ship = []  # координаты точек корабля
        self.list_busy_points = []  # координаты точек корабля и контура вокруг корабля
        self.list_of_shots = []  # координаты точек выстрелов корабля

    def __str__(self):
        graph_disp_x_axis = f"  |"
        graph_disp_y_axis = ""
        serial_number = 0

        for i in self.game_field:
            serial_number += 1
            graph_disp_y_axis += f'\n{serial_number} | {" | ".join(i)} |'
            graph_disp_x_axis += f' {serial_number} |'
        if self.hid:
            return (graph_disp_x_axis + graph_disp_y_axis).replace("■", "O")

        return (graph_disp_x_axis + graph_disp_y_axis)

    def out(self, dot):
        return not ((0 < dot.x <= self.size) and (0 < dot.y <= self.size))

    def circuit(self, ship, verb=False):
        near = [(0, 0), (1, 1), (1, -1), (0, 1), (0, -1), (-1, 1), (1, 0), (-1, 0), (-1, -1)]
        for dot in ship.dots():
            for dot_x, dot_y in near:
                coor = Dot(dot.x + dot_x, dot.y + dot_y)
                if 0 < coor.x <= 6 and 0 < coor.y <= 6:
                    if not (self.out(coor)) and (coor not in self.list_busy_points) or verb:
                        if verb and coor not in ship.dots():
                            self.game_field[coor.x - 1][coor.y - 1] = '∙'
                self.list_busy_points.append(coor)

    def add_ship(self, ship):
        for dot in ship.dots():
            if self.out(dot) or dot in self.list_busy_points:
                raise IncorrectCoordinateValue()
        for dot in ship.dots():
            self.game_field[dot.x - 1][dot.y - 1] = "■"
            self.list_busy_points.append(dot)
            self.coor_dot_ship.append(ship)
            self.circuit(ship)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutExcetion()
        if dot in self.list_of_shots:
            print(f'Целься точнее, ты уже стрелял по этим координатам!\n'
                  f'Попробуй еще разок.')
            raise RepeatMove()
        self.list_of_shots.append(dot)
        for ship in self.coor_dot_ship:
            if ship.shot(dot):
                ship.life -= 1
                self.game_field[dot.x - 1][dot.y - 1] = "X"
                if ship.life == 0:
                    self.num_wrecked_ships += 1
                    self.circuit(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.game_field[dot.x - 1][dot.y - 1] = "∙"
        print("Мимо!")
        return False

    def begin(self):
        self.list_busy_points = []

    def definition(self):
        return self.num_wrecked_ships == 1


class Player:
    def __init__(self, board, rival):
        self.board = board
        self.rival = rival

    def ask(self):
        raise ImplementedInDescendants()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.rival.shot(target)
                return repeat
            except BoardExcetion as error:
                print(error)


class AI(Player):
    def ask(self):
        dot = Dot(randint(1, 6), randint(1, 6))
        print(f"Ход компьютера: {dot.x} {dot.y}")
        return dot


class User(Player):
    def ask(self):
        while True:
            shot_coor = input("Ваш ход: ").split()
            if len(shot_coor) != 2:
                print("Введите 2 координаты.")
                continue
            x, y = shot_coor
            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа от 1 до 6.")
                continue
            x, y = int(x), int(y)
            return Dot(x, y)  # если будет смещение по координатам отрегулировать


def greet():
    print('''Хочешь стать настоящим морским волком?!
Ты сделал правильный выбор.
В этой игре ты сможешь проверить себя.
Приветствую тебя храбрец в игре.
    Морской бой!!!
Формат ввода: сначала вводим номер строки, потом вводим номер столбца.''')

class Game:
    def __init__(self, size=6):
        self.size = size
        gamer = self.random_board()
        ai = self.random_board()
        ai.hid = False
        self.ai = AI(ai, gamer)
        self.gamer = User(gamer, ai)

    def game_cycle(self):
        num = 0
        while True:
            print(f'{"-" * 20}\n'
                  f'Поле игрока:\n'
                  f'{self.gamer.board}\n'
                  f'{"-" * 20}\n'
                  f'Поле ИИ:\n'
                  f'{self.ai.board}\n'
                  f'{"-" * 20}\n')
            if num % 2 == 0:
                print("Твой ход!")
                repeat = self.gamer.move()
            else:
                print("Ход ИИ!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.definition():
                print("-" * 20)
                print('Игрок выиграл!')
                print(f'{"-" * 20}\n'
                      f'Поле ИИ:\n'
                      f'{self.ai.board}\n'
                      f'{"-" * 20}\n')
                break

            if self.gamer.board.definition():
                print("-" * 20)
                print('ИИ выиграл!')
                print(f'{"-" * 20}\n'
                      f'Поле игрока:\n'
                      f'{self.gamer.board}\n'
                      f'{"-" * 20}\n')

                break
            num += 1

    def start(self):
        greet()
        self.game_cycle()


    def try_board(self):
        lens = [2,]  # перечень кораблей и их количество
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardExcetion:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board


g = Game()

g.start()
