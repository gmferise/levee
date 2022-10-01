from .state_machine import Game
from .player import Player

if __name__ == '__main__':
    player = Player('save1')
    game = Game(player)
    # TODO: Main game loop