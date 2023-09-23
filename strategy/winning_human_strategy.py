# This is a simple human strategy:
# 6 Marksman, 6 Medics, and 4 Traceurs
# Move as far away from the closest zombie as possible
# If there are any zombies in attack range, attack the closest
# If a Medic's ability is available, heal a human in range with the least health

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

# Key is id, value is a tuple where the first value is attack cooldown and second is ability cooldown
my_cooldowns: dict[str, tuple[int, int]] = {}
actions = [[], [], []]

class WinningHumanStrategy(Strategy):
    def decide_character_classes(
            self,
            possible_classes: list[CharacterClassType],
            num_to_pick: int,
            max_per_same_class: int,
            ) -> dict[CharacterClassType, int]:
        # Using this funtion for initilization
        
        # The maximum number of special classes we can choose is 16
        # Selecting 6 Marksmen, 6 Medics, and 4 Traceurs
        # The other 4 humans will be regular class
        choices = {
            CharacterClassType.MARKSMAN: 5,
            CharacterClassType.MEDIC: 5,
            CharacterClassType.TRACEUR: 5,
            CharacterClassType.DEMOLITIONIST: 1,
        }
        return choices

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
        
        global my_cooldowns
        global actions

        return actions[1]

    def decide_abilities(
            self, 
            possible_abilities: dict[str, list[AbilityAction]], 
            game_state: GameState
            ) -> list[AbilityAction]:
        
        global my_cooldowns
        
        global actions

        return actions[2]
