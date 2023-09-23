from typing import *

from game.game_state import GameState
from game.character.character import Character

def num_zombies(characters: dict[str, Character]):
    i = 0
    for character in characters.values():
        if character.is_zombie():
            i += 1
            
    return i
            
def num_humans(characters: dict[str, Character]): 
    return len(characters) - num_zombies(characters)

class Node():
    def __init__(self, state: GameState, parent):
        self.state = state
        self.parent = parent
        self.is_terminal = (state.turn == 200) or (num_zombies(state.characters) == 0) or (num_humans(state.characters) == 0)
        self.num_visits = 0
        self.total_reward = 0
        self.children = {}
        
class TreeSearch():
    def __init__():
        pass
        
        
        