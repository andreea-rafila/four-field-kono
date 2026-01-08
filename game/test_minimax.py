from game.controller.Controller import Controller
from game.model.Player import Player, Colour

# quick smoke test for minimax-based computer move
c = Controller()
# choose computer as BLACK and human as WHITE for this test
player_human = Player(Colour.WHITE, False)
player_comp = Player(Colour.BLACK, True)
# start with black to move (computer)
c.initialize(turn=Colour.BLACK)
print('Initial board:')
c.print_current_state()
try:
    c.make_computer_move(player_comp)
    print('After computer move:')
    c.print_current_state()
    print('Test completed successfully')
except Exception as e:
    print('Error during computer move:', e)
