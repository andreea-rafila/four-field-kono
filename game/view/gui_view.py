import tkinter as tk
from tkinter import messagebox
from game.controller.Controller import Controller
from game.model.Player import Player, Colour

class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Four-field kono - Minimax AI")
        self.root.geometry("600x650")

        self.controller = Controller()
        self.player1 = None
        self.player2 = None
        self.selected_square = None
        self.board_buttons = {}

        self.initialize_game()

    def initialize_game(self):
        """Ask user to choose color and starting player."""
        # Choose player color
        color_choice = messagebox.askyesno(
            "Color Selection",
            "Do you want to play as BLACK?\n(No = WHITE)"
        )

        if color_choice:  # BLACK
            self.player1 = Player(Colour.BLACK, False)
            self.player2 = Player(Colour.WHITE, True)
        else:  # WHITE
            self.player1 = Player(Colour.WHITE, False)
            self.player2 = Player(Colour.BLACK, True)

        # Choose starting color
        start_choice = messagebox.askyesno(
            "Starting Color",
            "Should BLACK start?\n(No = WHITE)"
        )

        to_start = Colour.BLACK if start_choice else Colour.WHITE
        self.controller.initialize(turn=to_start)

        self.setup_ui()
        self.update_board_display()
        self.check_computer_turn()

    def setup_ui(self):
        """Setup the game board UI."""
        # Title
        title_label = tk.Label(self.root, text="Four-field kono", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Status label
        self.status_label = tk.Label(self.root, text="", font=("Arial", 12), fg="blue")
        self.status_label.pack(pady=5)

        # Board frame
        board_frame = tk.Frame(self.root, bg="gray")
        board_frame.pack(pady=10)

        # Column headers
        header_frame = tk.Frame(board_frame)
        header_frame.pack()
        tk.Label(header_frame, text=" ", width=3).pack(side="left")
        for col in ["A", "B", "C", "D"]:
            tk.Label(header_frame, text=col, width=11, font=("Arial", 10, "bold")).pack(side="left")

        # Board buttons (4x4)
        for row in range(4):
            row_frame = tk.Frame(board_frame)
            row_frame.pack()

            # Row number
            tk.Label(row_frame, text=str(row + 1), width=3, font=("Arial", 10, "bold")).pack(side="left")

            for col in range(4):
                coord = f"{chr(65 + col)}{row + 1}"  # A1, A2, ..., D4
                btn = tk.Button(
                    row_frame,
                    text="",
                    width=6,
                    height=3,
                    font=("Arial", 10, "bold"),
                    command=lambda c=coord: self.on_square_click(c)
                )
                btn.pack(side="left", padx=2, pady=2)
                self.board_buttons[coord] = btn

        # Info frame
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)

        self.info_label = tk.Label(info_frame, text="", font=("Arial", 10), justify="left")
        self.info_label.pack()

        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.move_button = tk.Button(button_frame, text="Make Move", command=self.make_human_move, state="disabled")
        self.move_button.pack(side="left", padx=5)

        reset_button = tk.Button(button_frame, text="Reset Game", command=self.reset_game)
        reset_button.pack(side="left", padx=5)

    def on_square_click(self, coord):
        """Handle board square click."""
        if self.controller.get_turn() != self.player1.color:
            messagebox.showwarning("Not Your Turn", "Wait for the computer to move.")
            return

        board = self.controller.get_current_state().board

        if self.selected_square is None:
            # First click - select origin
            if self.controller.is_player_piece_at_string_coordinate_on_board(self.player1, coord, board):
                self.selected_square = coord
                self.status_label.config(text=f"Selected: {coord}. Click destination.")
            else:
                messagebox.showwarning("Invalid", "No piece of yours at this square.")
        else:
            # Second click - select destination
            if coord == self.selected_square:
                # Deselect
                self.board_buttons[self.selected_square].config(bg="SystemButtonFace")
                self.selected_square = None
                self.status_label.config(text="Selection cleared.")
            else:
                # Try to make move
                self.move_button.config(state="normal")
                self.destination_square = coord
                self.status_label.config(text=f"Move from {self.selected_square} to {coord}. Click 'Make Move'.")

    def make_human_move(self):
        """Execute human player's move."""
        if self.selected_square is None or not hasattr(self, 'destination_square'):
            messagebox.showwarning("Invalid", "Select origin and destination squares.")
            return

        try:
            self.controller.make_move(
                player=self.player1,
                initial_coordinate=self.selected_square,
                new_coordinate=self.destination_square
            )
            self.selected_square = None
            self.move_button.config(state="disabled")
            self.update_board_display()
            self.check_computer_turn()
        except ValueError as e:
            messagebox.showerror("Invalid Move", str(e))

    def check_computer_turn(self):
        """Check if it's the computer's turn and execute its move."""
        if self.controller.is_game_over():
            self.end_game()
            return

        if self.controller.get_turn() == self.player2.color:
            self.status_label.config(text="Computer is thinking...", fg="red")
            self.root.update()

            try:
                self.controller.make_computer_move(player=self.player2)
                self.update_board_display()
                self.root.after(3000, self.check_computer_turn)  # Delay for visibility
            except ValueError as e:
                messagebox.showerror("Computer Error", str(e))
                self.end_game()
        else:
            self.status_label.config(text=f"Your turn ({self.player1.color.value})", fg="green")

    def update_board_display(self):
        """Update the visual board to match the controller state."""
        board = self.controller.get_current_state().board

        for coord, btn in self.board_buttons.items():
            col = ord(coord[0]) - ord('A')
            row = int(coord[1]) - 1
            piece = board.get_at_position(row, col)

            # Set button text and color
            if piece == 'W':
                btn.config(text="W", bg="white", fg="black")
            elif piece == 'B':
                # Use a light-blue background for B so the letter is clearly visible
                btn.config(text="B", bg="#add8e6", fg="black")
            else:  # '.'
                btn.config(text="", bg="lightgray", fg="black")

        # Update info
        white_count = board.get_colour_count(Colour.WHITE)
        black_count = board.get_colour_count(Colour.BLACK)
        self.info_label.config(
            text=f"WHITE: {white_count} | BLACK: {black_count}\nTurn: {self.controller.get_turn().value}"
        )

    def end_game(self):
        """Display game over message."""
        winner = self.controller.get_winner()
        messagebox.showinfo("Game Over", f"{winner.name} wins!")
        self.root.quit()

    def reset_game(self):
        """Reset the game."""
        self.root.destroy()
        root = tk.Tk()
        GameGUI(root)
        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    gui = GameGUI(root)
    root.mainloop()