from game.model.Player import Colour


def create_board(fill1=None, fill2=None):
    return [
        [fill1, fill1, fill2, fill2]
        for _ in range(4)
    ]


class Board:
    def __init__(self):
        self.board = create_board( "W", "B")
        self.columns = [" ", "A", "B", "C", "D"]
        self.rows = ["1", "2", "3", "4"]

    def print_board(self):
        print(*self.columns)
        i = 0
        for row in self.board:
            print(self.rows[i], *row)
            i += 1

    def get_at_position(self, row: int, column: int):
        return self.board[row][column]

    def set_at_position(self, row: int, column: int, value: str):
        self.board[row][column] = value

    def get_colour_count(self, colour: Colour):
        count = 0
        for row in self.board:
            for cell in row:
                if cell == colour.value:
                    count += 1
        return count

    def copy(self):
        """Return a deep copy of this Board (new Board instance with copied board array).

        Note: We intentionally create a new Board and overwrite its internal board with
        a copied 2D list so minimax simulations can mutate the copy safely.
        """
        new_board = Board()
        new_board.board = [row.copy() for row in self.board]
        new_board.columns = self.columns.copy()
        new_board.rows = self.rows.copy()
        return new_board
