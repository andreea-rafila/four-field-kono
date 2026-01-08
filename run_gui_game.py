#!/usr/bin/env python3
"""
Launcher for the GUI version of the Pieces Game with Minimax AI.
Run this script to start the game.
"""

if __name__ == "__main__":
    from game.view.gui_view import GameGUI
    import tkinter as tk

    root = tk.Tk()
    gui = GameGUI(root)
    root.mainloop()

