# This is a simple zombie strategy:
# Move directly towards the closest human. If there are any humans in attacking range, attack a random one.
# If there are no humans in attacking range but there are obstacles, attack a random obstacle.

import random
from strategy.tree_search import TreeSearch
from game.character.action.ability_action import AbilityAction
from game.character.action.ability_action_type import AbilityActionType
from game.character.action.attack_action import AttackAction
from game.character.action.attack_action_type import AttackActionType
from game.character.action.move_action import MoveAction
from game.character.character_class_type import CharacterClassType
from game.game_state import GameState
from game.util.position import Position
from strategy.strategy import Strategy
from strategy.pyengine import PyGameState, GamePhase


my_cooldowns: dict[str, tuple[int, int]] = {}
actions = [[], []]

class WinningZombieStrategy(Strategy):
    
    def decide_moves(
            self, 
            possible_moves: dict[str, list[MoveAction]], 
            game_state: GameState
            ) -> list[MoveAction]:
        
        global my_cooldowns
        global actions
        
        # initialize character cooldowns
        if len(my_cooldowns) == 0:
            for character_id in game_state.characters.keys():
                my_cooldowns[character_id] = (0, 0)
                
        TS = TreeSearch(game_state, my_cooldowns, GamePhase.MOVE, .1, .9, False)
        actions = TS.search()

        return actions[0]

    def decide_attacks(
            self, 
            possible_attacks: dict[str, list[AttackAction]], 
            game_state: GameState
            ) -> list[AttackAction]:
        
        global actions

        return actions[0]
