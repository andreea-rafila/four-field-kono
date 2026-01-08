from enum import Enum

class Colour(Enum):
    WHITE = "W"
    BLACK = "B"

class Player:
    def __init__(self, color: Colour, is_computer:bool):
        self.color = color
        self.is_computer = is_computer
