import unittest
from unittest.mock import patch

from game.controller.Controller import (
    Controller,
    is_valid_coordinate,
    is_orthogonal_coordinate,
    is_move_or_take,
    string_coordinate_to_indices,
    get_opposite_colour,
    get_opposite_player,
)
from game.model.Board import Board
from game.model.Player import Player, Colour


class TestHelpers(unittest.TestCase):
    def test_valid_coordinate(self):
        self.assertTrue(is_valid_coordinate("A1"))
        self.assertTrue(is_valid_coordinate("d4"))
        self.assertFalse(is_valid_coordinate("E1"))
        self.assertFalse(is_valid_coordinate("A5"))
        self.assertFalse(is_valid_coordinate("Z9"))

    def test_string_coordinate_to_indices(self):
        self.assertEqual(string_coordinate_to_indices("A1"), (0, 0))
        self.assertEqual(string_coordinate_to_indices("D4"), (3, 3))
        self.assertEqual(string_coordinate_to_indices("B3"), (2, 1))

    def test_is_orthogonal_coordinate(self):
        self.assertTrue(is_orthogonal_coordinate("A1", "A2"))  # distance 1
        self.assertTrue(is_orthogonal_coordinate("A1", "A3"))  # distance 2
        self.assertTrue(is_orthogonal_coordinate("A1", "B1"))  # distance 1
        self.assertTrue(is_orthogonal_coordinate("A1", "C1"))  # distance 2
        self.assertFalse(is_orthogonal_coordinate("A1", "B2"))  # diagonal
        self.assertFalse(is_orthogonal_coordinate("A1", "A4"))  # distance 3

    def test_is_move_or_take(self):
        self.assertEqual(is_move_or_take("A1", "A2"), "move")
        self.assertEqual(is_move_or_take("A1", "B1"), "move")
        self.assertEqual(is_move_or_take("A1", "A3"), "take")
        self.assertEqual(is_move_or_take("A1", "C1"), "take")

    def test_opposites(self):
        self.assertEqual(get_opposite_colour(Colour.WHITE), Colour.BLACK)
        self.assertEqual(get_opposite_colour(Colour.BLACK), Colour.WHITE)

        p_w_human = Player(Colour.WHITE, False)
        p_w_comp = Player(Colour.WHITE, True)

        opp1 = get_opposite_player(p_w_human)
        self.assertEqual(opp1.color, Colour.BLACK)
        self.assertTrue(opp1.is_computer)   # opposite of human => computer in your logic

        opp2 = get_opposite_player(p_w_comp)
        self.assertEqual(opp2.color, Colour.BLACK)
        self.assertFalse(opp2.is_computer)  # opposite of computer => human in your logic


class TestControllerCore(unittest.TestCase):
    def setUp(self):
        self.c = Controller()
        self.c.initialize(turn=Colour.WHITE)

    def test_initialize_adds_state(self):
        self.assertEqual(len(self.c.repository.states), 1)
        self.assertEqual(self.c.get_turn(), Colour.WHITE)
        self.assertFalse(self.c.is_game_over())

    def test_is_space_empty_on_initial_board(self):
        board = self.c.get_current_state().board
        # Initial board has no '.' at all
        self.assertFalse(self.c.is_space_empty_on_board("A1", board))
        self.assertFalse(self.c.is_space_empty_on_board("D4", board))

    def test_make_move_rejects_invalid_coordinates(self):
        player = Player(Colour.WHITE, False)
        with self.assertRaises(ValueError):
            self.c.make_move(player, "Z9", "A1")
        with self.assertRaises(ValueError):
            self.c.make_move(player, "A1", "Z9")

    def test_make_move_rejects_non_orthogonal(self):
        player = Player(Colour.WHITE, False)
        with self.assertRaises(ValueError):
            self.c.make_move(player, "A1", "B2")

    def test_make_move_rejects_invalid_move_requirements(self):
        board = self.c.get_current_state().board
        player = Player(Colour.WHITE, False)

        # A1 -> A2 is a "move", but A2 is not empty on initial board
        self.assertTrue(is_orthogonal_coordinate("A1", "A2"))
        self.assertEqual(is_move_or_take("A1", "A2"), "move")
        self.assertFalse(self.c.is_valid_move_or_take(player, "A1", "A2", board))

        with self.assertRaises(ValueError):
            self.c.make_move(player, "A1", "A2")

    def test_valid_take_on_initial_board_white_A1_to_C1(self):
        board = self.c.get_current_state().board
        player = Player(Colour.WHITE, False)

        # On initial board row 1 is: A1=W, B1=W, C1=B, D1=B
        self.assertEqual(is_move_or_take("A1", "C1"), "take")
        self.assertTrue(self.c.is_valid_take_on_board("A1", "C1", player, board))

    def test_make_move_take_updates_board_and_turn(self):
        player = Player(Colour.WHITE, False)

        # Take A1 -> C1 should be valid on initial board by your rules:
        # initial A1=W, middle B1=W, dest C1=B
        self.c.make_move(player, "A1", "C1")

        # state history grows
        self.assertEqual(len(self.c.repository.states), 2)

        new_state = self.c.get_current_state()
        new_board = new_state.board

        # A1 becomes empty
        self.assertEqual(new_board.get_at_position(0, 0), ".")
        # C1 becomes W (overwrites B)
        self.assertEqual(new_board.get_at_position(0, 2), "W")

        # turn flips to opposite player colour (BLACK)
        self.assertEqual(new_state.turn, Colour.BLACK)

    def test_is_final_state_opponent_has_one_piece(self):
        board = self.c.get_current_state().board

        # Force a position: only one BLACK piece on the whole board
        for r in range(4):
            for c in range(4):
                board.set_at_position(r, c, ".")
        board.set_at_position(0, 0, "W")
        board.set_at_position(0, 1, "W")
        board.set_at_position(3, 3, "B")  # only one black piece

        player = Player(Colour.WHITE, False)
        self.assertTrue(self.c.is_final_state_on_board(board, player))

    def test_minimax_root_smoke(self):
        board = self.c.get_current_state().board
        player = Player(Colour.WHITE, True)

        score, move = self.c.minimax_root(board, player, depth=2)
        # move existence depends on available legal moves/takes; on your initial board
        # WHITE has at least the take A1->C1, B1->D1, etc.
        self.assertIsNotNone(score)
        self.assertIsNotNone(move)
        self.assertEqual(len(move), 2)

    def test_make_computer_move_uses_minimax_choice(self):
        player_comp = Player(Colour.WHITE, True)

        # Make minimax deterministic: force it to choose ("A1","C1")
        with patch.object(self.c, "minimax_root", return_value=(999, ("A1", "C1"))):
            self.c.make_computer_move(player_comp)

        board = self.c.get_current_state().board
        self.assertEqual(board.get_at_position(0, 0), ".")
        self.assertEqual(board.get_at_position(0, 2), "W")


if __name__ == "__main__":
    unittest.main()
