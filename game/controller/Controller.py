from typing import Any

from game.model.Board import Board
from game.model.Player import Player, Colour
from game.model.State import State
from game.repository.Repository import Repository

from random import randint

VALID_VALUES = {
    f"{letter}{digit}"
    for letter in ("A", "B", "C", "D")
    for digit in range(1, 5)
}
def get_opposite_colour(colour: Colour) -> Colour:
    if colour == Colour.WHITE:
        return Colour.BLACK
    else:
        return Colour.WHITE

def get_opposite_player(player: Player) -> Player:
    if player.color == Colour.WHITE:
        if player.is_computer:
            return Player(Colour.BLACK, False)
        else:
            return Player(Colour.BLACK, True)
    else:
        if player.is_computer:
            return Player(Colour.WHITE, False)
        else:
            return Player(Colour.WHITE, True)


def is_valid_coordinate(coordinate: str) -> bool:
    return coordinate.capitalize() in VALID_VALUES

def is_orthogonal_coordinate(initial_coordinate: str, new_coordinate: str) -> bool:
    if initial_coordinate[0] == new_coordinate[0]:
        i = abs(int(initial_coordinate[1]) - int(new_coordinate[1]))
        return i == 1 or i == 2
    elif initial_coordinate[1] == new_coordinate[1]:
        i = abs(ord(initial_coordinate[0]) - ord(new_coordinate[0]))
        return i == 1 or i == 2
    return False

def string_coordinate_to_indices(coordinate: str):
    column = ord(coordinate[0].upper()) - ord('A') # D - A = 3   A = 65, B = 66, C = 67, D = 68
    row = int(coordinate[1]) - 1 # -1 to convert to 0-based index
    return row, column

def is_move_or_take(initial_coordinate: str, new_coordinate: str) -> str:
    if initial_coordinate[0] == new_coordinate[0]:
        if abs(int(initial_coordinate[1]) - int(new_coordinate[1])) == 1:
            return "move" # A1 A2
        else:
            return "take" # A1 A3
    else:
        if abs(ord(initial_coordinate[0]) - ord(new_coordinate[0])) == 1:
            return "move" # A1 B1
        else:
            return "take" # A1 C1

class Controller:
    def __init__(self):
        self.repository = Repository()
        # configurable search depth for minimax
        self.minimax_depth = 3

    def initialize(self, turn: Colour):
        state = State(board=Board(), turn=turn, is_final=False)
        self.repository.add_state(state)

    def print_current_state(self):
        last_state = self.get_current_state()
        print("TURN: ", self.get_turn())
        last_state.board.print_board()

    def get_current_state(self) -> Any:
        last_state = self.repository.states[-1]
        return last_state

    def is_game_over(self):
        last_state = self.get_current_state()
        return last_state.is_final

    def get_turn(self):
        last_state = self.get_current_state()
        return last_state.turn

    def is_player_piece_at_string_coordinate_on_board(self, player: Player, coordinate: str, board: Board) -> bool:
        row, col = string_coordinate_to_indices(coordinate)
        return board.get_at_position(row=row, column=col) == self._piece_char_for_player(player)

    def is_player_piece_at_coordinate_on_board(self, player: Player, coord_tuple: tuple[int, int],
                                               board: Board) -> bool:
        row, col = coord_tuple
        return board.get_at_position(row=row, column=col) == self._piece_char_for_player(player)

    def is_opposing_player_piece_at_coordinate_on_board(self, player: Player, coordinate: str, board: Board) -> bool:
        opponent = get_opposite_player(player)
        row, col = string_coordinate_to_indices(coordinate)
        return board.get_at_position(row=row, column=col) == self._piece_char_for_player(opponent)

    def is_valid_move_or_take(self, player: Player, initial_coordinate: str, new_coordinate: str, board: Board) -> bool:
        action = is_move_or_take(initial_coordinate, new_coordinate)
        if action == "move":
            return self.is_valid_move_on_board(initial_coordinate, new_coordinate, player, board)
        elif action == "take":
            # player piece at initial_coordinate, middle player piece, opponent piece at new_coordinate
            return self.is_valid_take_on_board(initial_coordinate, new_coordinate, player, board)
        return False

    def is_valid_take_on_board(self, initial_coordinate: str, new_coordinate: str, player: Player,
                               board: Board) -> bool:
        initial_coordinates_row, initial_coordinates_column = string_coordinate_to_indices(initial_coordinate)
        new_coordinates_row, new_coordinates_column = string_coordinate_to_indices(new_coordinate)
        middle_row = (initial_coordinates_row + new_coordinates_row) // 2
        middle_column = (initial_coordinates_column + new_coordinates_column) // 2
        return (self.is_player_piece_at_string_coordinate_on_board(player, initial_coordinate, board) and
                self.is_player_piece_at_coordinate_on_board(player, (middle_row, middle_column), board) and
                self.is_opposing_player_piece_at_coordinate_on_board(player, new_coordinate, board))

    def is_valid_move_on_board(self, initial_coordinate: str, new_coordinate: str, player: Player,
                               board: Board) -> bool:
        return self.is_player_piece_at_string_coordinate_on_board(player, initial_coordinate, board) and \
            self.is_space_empty_on_board(new_coordinate, board)

    def is_space_empty_on_board(self, coordinate: str, board: Board) -> bool:
        row, col = string_coordinate_to_indices(coordinate)
        return board.get_at_position(row=row, column=col) == '.'

    def make_move(self, player:Player, initial_coordinate:str, new_coordinate:str):
        board = self.get_current_state().board

        if not is_valid_coordinate(initial_coordinate):
            raise ValueError(f"Invalid coordinate: {initial_coordinate} outside the board")
        if not is_valid_coordinate(new_coordinate):
            raise ValueError(f"Invalid coordinate: {new_coordinate} outside the board")
        if not is_orthogonal_coordinate(initial_coordinate, new_coordinate):
            raise ValueError(f"Invalid coordinates: move is not orthogonal")
        if not self.is_valid_move_or_take(player, initial_coordinate, new_coordinate, board):
            raise ValueError(f"Invalid move: does not satisfy move/take requirements")

        modified_board = self.apply_move(player, initial_coordinate, new_coordinate, board)

        # player has right to move  - 2 cases - move or take - their specific requirements W W B
        # player has moves available -> here or in a separate method

        opponent = get_opposite_player(player)
        state = State(board=modified_board, turn=opponent.color, is_final=self.is_final_state_on_board(modified_board, player))
        self.repository.add_state(state)

    def apply_move(self, player:Player, initial_coordinate:str, new_coordinate:str, board: Board) -> Board:
        # make initial_coordinate empty
        initial_row, initial_column = string_coordinate_to_indices(initial_coordinate)
        board.set_at_position(row=initial_row, column=initial_column, value='.')

        # put player piece at new_coordinate
        new_row, new_column = string_coordinate_to_indices(new_coordinate)
        board.set_at_position(row=new_row, column=new_column, value=player.color.value) # name gives "WHITE" or "BLACK", we want "W" or "B"

        # A1 A2 -> move   . W
        #                 .  W  W
        # A1 A3 -> take   A1 A2 A3
        return board

    def make_computer_move(self, player):
        # use minimax to pick best move
        board = self.get_current_state().board

        best_score, best_move = self.minimax_root(board=board, player=player, depth=self.minimax_depth)

        # fallback to random if minimax did not find any move (shouldn't happen if there are moves)
        if best_move is None:
            possible_moves, possible_takes = self.get_possible_moves_for_player_on_board(player, board)
            if not possible_moves and not possible_takes:
                raise ValueError("No possible moves for computer")
            if possible_takes:
                idx = randint(0, len(possible_takes) - 1)
                initial_coordinate, new_coordinate = possible_takes[idx]
            else:
                idx = randint(0, len(possible_moves) - 1)
                initial_coordinate, new_coordinate = possible_moves[idx]
        else:
            initial_coordinate, new_coordinate = best_move

        # apply chosen move to the real board
        modified_board = self.apply_move(player, initial_coordinate, new_coordinate, self.get_current_state().board)
        opponent = get_opposite_player(player)
        state = State(board=modified_board, turn=opponent.color, is_final=self.is_final_state_on_board(modified_board, player))
        self.repository.add_state(state)

    def get_possible_moves_for_player_on_board(self, player: Player, board: Board) -> tuple[
        list[tuple[str, str]], list[tuple[str, str]]]:
        possible_moves = []
        possible_takes = []
        for i in VALID_VALUES:
            for j in VALID_VALUES:
                if is_orthogonal_coordinate(i, j):
                    action = is_move_or_take(i, j)
                    if action == "take":
                        if self.is_valid_take_on_board(initial_coordinate=i, new_coordinate=j, player=player,
                                                       board=board):
                            possible_takes.append((i, j))
                    elif action == "move":
                        if self.is_valid_move_on_board(initial_coordinate=i, new_coordinate=j, player=player,
                                                       board=board):
                            possible_moves.append((i, j))
        return possible_moves, possible_takes

    def is_final_state_on_board(self, board: Board, player: Player) -> bool:
        opposite_player = get_opposite_player(player)
        return board.get_colour_count(opposite_player.color) == 1 or self.get_possible_moves_for_player_on_board(
            opposite_player, board) == ([], [])

    def _piece_char_for_player(self, player: Player) -> str:
        return player.color.value

    # ---------- Evaluation and Minimax ----------
    def evaluate_board(self, board: Board, player: Player) -> int:
        # simple heuristic: piece difference + small mobility bonus
        opponent = get_opposite_player(player)
        player_count = board.get_colour_count(player.color)
        opponent_count = board.get_colour_count(opponent.color)
        piece_diff = player_count - opponent_count
        # mobility
        moves, takes = self.get_possible_moves_for_player_on_board(player, board)
        mobility = len(moves) + 2 * len(takes)
        return piece_diff * 100 + mobility

    def minimax_root(self, board: Board, player: Player, depth: int):
        # return (best_score, best_move_tuple_or_None)
        best_score = float('-inf')
        best_move = None

        possible_moves, possible_takes = self.get_possible_moves_for_player_on_board(player, board)
        all_moves = possible_takes + possible_moves  # prefer takes first if equal score

        if not all_moves:
            return None, None

        for move in all_moves:
            initial, new = move
            board_copy = board.copy()
            # apply to copy
            self.apply_move(player, initial, new, board_copy)
            opponent = get_opposite_player(player)
            # Evaluate from the perspective of the root player (maximizing)
            score = self.minimax(board_copy, opponent, depth-1, False, float('-inf'), float('inf'), player)
            if score is None:
                continue
            if score > best_score:
                best_score = score
                best_move = move

        return best_score, best_move

    def minimax(self, board: Board, player: Player, depth: int, maximizing_player: bool, alpha: float, beta: float, root_player: Player):
        # terminal or depth
        if depth == 0 or self.is_final_state_on_board(board, player):
            # Always evaluate from root_player's perspective so scores are consistent
            return self.evaluate_board(board, root_player)

        if maximizing_player:
            max_eval = float('-inf')
            possible_moves, possible_takes = self.get_possible_moves_for_player_on_board(player, board)
            all_moves = possible_takes + possible_moves
            if not all_moves:
                return self.evaluate_board(board, root_player)
            for move in all_moves:
                initial, new = move
                board_copy = board.copy()
                self.apply_move(player, initial, new, board_copy)
                opponent = get_opposite_player(player)
                eval_score = self.minimax(board_copy, opponent, depth-1, False, alpha, beta, root_player)
                if eval_score is None:
                    continue
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            possible_moves, possible_takes = self.get_possible_moves_for_player_on_board(player, board)
            all_moves = possible_takes + possible_moves
            if not all_moves:
                return self.evaluate_board(board, root_player)
            for move in all_moves:
                initial, new = move
                board_copy = board.copy()
                self.apply_move(player, initial, new, board_copy)
                opponent = get_opposite_player(player)
                eval_score = self.minimax(board_copy, opponent, depth-1, True, alpha, beta, root_player)
                if eval_score is None:
                    continue
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def get_winner(self):
        return get_opposite_colour(self.get_current_state().turn)