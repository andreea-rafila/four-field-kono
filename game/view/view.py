from game.controller.Controller import Controller
from game.model.Player import Player, Colour

controller = Controller()

player1 = None
player2 = None

print("Choose which color to play:")
print("1. Black")
print("2. White")
option = input()
if option == "1":
    player1 = Player(Colour.BLACK, False)
    player2 = Player(Colour.WHITE, True)
elif option == "2":
    player1 = Player(Colour.WHITE, False)
    player2 = Player(Colour.BLACK, True)
else:
    print("Invalid option")
    exit()

to_start = None

print("Choose which color to start:")
print("1. Black")
print("2. White")
option = input()
if option == "1":
    to_start = Colour.BLACK
elif option == "2":
    to_start = Colour.WHITE
else:
    print("Invalid option")
    exit()

controller.initialize(turn=to_start)

while not controller.is_game_over():
    controller.print_current_state()
    if controller.get_turn() == player1.color:
        # HUMAN
        coordinates = input("Give coordinates")
        coordinates = coordinates.split(" ")
        try:
            controller.make_move(player=player1, initial_coordinate=coordinates[0], new_coordinate=coordinates[1])
        except Exception as e:
            print(e)
    else:
        # COMPUTER
        try:
            controller.make_computer_move(player=player2)
        except ValueError as e:
            print(e)

print(f"{controller.get_winner()} wins!")
controller.print_current_state()

