from game.model.Board import Board
from game.model.Player import Player, Colour


class State:
    def __init__(self, board: Board, turn: Colour, is_final: bool):
        self.board = board
        self.turn = turn
        self.is_final = is_final
