class Chessman:
    def __init__(self, x, y, c_type, side, display):
        self.x = x
        self.y = y
        self.type = c_type
        self.side = side
        self.display = display

    def set_location(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def get_location(self):
        return self.x, self.y

    def check_boundary(self, boundaries: list):
        for b_type, side1, side2 in boundaries:
            if b_type == 1 and side1[0] <= self.x < side2[0] and self.y > side1[1]:
                return False
            elif b_type == 2 and side1[0] <= self.x < side2[0] and self.y < side1[1]:
                return False
            elif b_type == 3 and side1[1] <= self.y < side2[1] and self.x < side1[0]:
                return False
            elif b_type == 4 and side1[1] <= self.y < side2[1] and self.x > side1[0]:
                return False
        return True

    def check_collision(self, chessmen):
        for chessman in chessmen.values():
            if self.get_location() == chessman.get_location() and self != chessman:
                if chessman.side == self.side:
                    return False
                else:
                    if chessman.type + 1 == self.type or chessman.type - 2 == self.type:
                        chessmen.pop(chessman.display)
                        return True
                    else:
                        return False
        return True

    def move(self, displacement: (int, int), chessboard):
        self.x += displacement[0]
        self.y += displacement[1]
        if self.check_boundary(chessboard.boundaries) and self.check_collision(chessboard.chessmen):
            if 0 <= self.x <= chessboard.size[0] and 0 <= self.y <= chessboard.size[1]:
                return True
        else:
            self.x -= displacement[0]
            self.y -= displacement[1]
            return False


class Chessboard:
    def __init__(self, x, y):
        self.size = (x, y)
        self.boundaries = []
        self.chessmen = dict()
        self.background = []
        self.background_unit = Chessman(0, 0, 0, 0, "┼")

    def add_boundary(self, new_boundary: [int, (int, int), (int, int)]):
        # 上下左右，1，2，3，4
        if new_boundary[1] > new_boundary[2]:
            self.boundaries.append([new_boundary[0], new_boundary[2], new_boundary[1]])
        self.boundaries.append(new_boundary)

    def add_chessman(self, chessman: Chessman):
        self.chessmen[chessman.display] = chessman

    def move(self, display, displacement):
        chessman = self.chessmen[display]
        if chessman.move(displacement, self):
            self.background[self.size[1] - 1 - chessman.y + displacement[1]] = \
                self.background[self.size[1] - 1 - chessman.y + displacement[1]][
                :chessman.x - displacement[0]] \
                + self.background_unit.display + \
                self.background[self.size[1] - 1 - chessman.y + displacement[1]][
                chessman.x - displacement[0] + 1:]
            self.background[self.size[1] - 1 - chessman.y] = \
                self.background[self.size[1] - 1 - chessman.y][:chessman.x] + \
                chessman.display + \
                self.background[self.size[1] - 1 - chessman.y][chessman.x + 1:]
            return True
        return False

    def generate_background(self):
        background_unit = self.background_unit
        for i in range(self.size[1]):
            self.background.append("")
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                background_unit.set_location(x, y)
                self.background[self.size[1] - 1 - y] += self.background_unit.display if background_unit.check_boundary(
                    self.boundaries) else "    "

    def load_chessmen(self):
        for chessman in self.chessmen.values():
            self.background[self.size[1] - 1 - chessman.y] = \
                self.background[self.size[1] - 1 - chessman.y][:chessman.x] + \
                chessman.display + \
                self.background[self.size[1] - 1 - chessman.y][chessman.x + 1:]

    def __str__(self):
        return "\n".join(self.background)


if __name__ == "__main__":
    board = Chessboard(7, 7)
    # 上边界
    board.add_boundary([1, (0, 4), (2, 3)])
    board.add_boundary([1, (2, 6), (4, 6)])
    board.add_boundary([1, (5, 4), (8, 4)])
    # 下边界
    board.add_boundary([2, (0, 2), (2, 2)])
    board.add_boundary([2, (2, 0), (4, 0)])
    board.add_boundary([2, (5, 2), (8, 2)])

    board.generate_background()
    print(board)

    board.add_chessman(Chessman(0, 4, 0, 0, "典"))
    board.add_chessman(Chessman(0, 3, 1, 0, "孝"))
    board.add_chessman(Chessman(0, 2, 2, 0, "急"))

    board.add_chessman(Chessman(6, 4, 0, 1, "颠"))
    board.add_chessman(Chessman(6, 3, 1, 1, "笑"))
    board.add_chessman(Chessman(6, 2, 2, 1, "寄"))

    board.load_chessmen()
    print(board)
    board.move("颠", (-5, 0))
    print(board)
    board.move("颠", (0, -2))
    print(board)
    board.move("颠", (-1, 0))
    print(board)