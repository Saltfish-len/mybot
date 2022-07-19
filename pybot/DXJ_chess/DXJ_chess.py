class Chess_type:
    pass


class Chessman:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.type = 0
        self.side = 0

    def get_location(self):
        return self.x, self.y

    def check_boundary(self, boundaries: list):
        for b_type, side1, side2 in boundaries:
            if b_type == 1 and side1[0] <= self.x <= side2[0] and self.y > side1[1]:
                return False
            elif b_type == 2 and side1[0] <= self.x <= side2[0] and self.y < side1[1]:
                return False
            elif b_type == 3 and side1[1] <= self.y <= side2[1] and self.x < side1[0]:
                return False
            elif b_type == 4 and side1[1] <= self.y <= side2[1] and self.x > side1[0]:
                return False
            return True


    def check_collision(self, chessmen: list):
        for chessman in chessmen:
            if self.get_location() == chessman.get_location():
                if chessman.side == self.side:
                    return False
                else:
                    if chessman.type + 1 == self.type or chessman.type - 2 == self.type:
                        chessmen.remove(chessmen)
                        return True
                    else:
                        return False

    def move(self, displacement: (int,int), chessboard):
        self.x += displacement[0]
        self.y += displacement[1]
        if self.check_boundary(chessboard.boundaries) and self.check_collision(chessboard.boundaries):
            return True
        else:
            self.x -= displacement[0]
            self.y -= displacement[1]
            return False


class Chessboard:
    def __init__(self):
        self.boundaries = []
        self.chessmen = []

    def add_boundary(self, new_boundary: [int, (), ()]):
        # 上下左右，1，2，3，4
        self.boundaries.append(new_boundary)

    def add_chessman(self, chessman: Chessman):
        self.chessmen.append(chessman)

    def move(self, chess_type, side, displacement):
        if side:
            for chessman in self.chessmen:
                if chessman.type == chess_type:
                    new_location = chessman.move(displacement)

