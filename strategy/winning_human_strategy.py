# This is a simple human strategy:
# 6 Marksman, 6 Medics, and 4 Traceurs
# Move as far away from the closest zombie as possible
# If there are any zombies in attack range, attack the closest
# If a Medic's ability is available, heal a human in range with the least health

import random
import strategy.tree_search as tree_search
from game.character.action.ability_action import AbilityAction
from game.character.action.ability_action_type import AbilityActionType
from game.character.action.attack_action import AttackAction
from game.character.action.attack_action_type import AttackActionType
from game.character.action.move_action import MoveAction
from game.character.character_class_type import CharacterClassType
from game.game_state import GameState
from game.util.position import Position
from strategy.strategy import Strategy
from strategy.pyengine import PyGameState

# Key is id, value is a tuple where the first value is attack cooldown and second is ability cooldown
my_cooldowns: dict[str, tuple[int, int]] = {}
my_game_state: PyGameState = None

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
        global my_game_state
        
        # initialize character cooldowns
        if len(my_cooldowns) == 0:
            for character_id in game_state.characters.keys():
                my_cooldowns[character_id] = (0, 0)
                
        my_game_state = PyGameState(game_state, my_cooldowns)
        print(my_game_state.turn, game_state.turn)
        print(my_game_state.is_equal(game_state))
        
            
        choices = []

        for [character_id, moves] in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue

            pos = game_state.characters[character_id].position  # position of the human
            closest_zombie_pos = pos  # default position is zombie's pos
            closest_zombie_distance =  1234  # large number, map isn't big enough to reach this distance
            

            # Iterate through every zombie to find the closest one
            for c in game_state.characters.values():
                if not c.is_zombie:
                    continue  # Fellow humans are frens :D, ignore them

                distance = abs(c.position.x - pos.x) + abs(c.position.y - pos.y)  # calculate manhattan distance between human and zombie
                if distance < closest_zombie_distance:  # If distance is closer than current closest, replace it!
                    closest_zombie_pos = c.position
                    closest_zombie_distance = distance

            # Move as far away from the zombie as possible
            move_distance = -1  # Distance between the move action's destination and the closest zombie
            move_choice = moves[0]  # The move action the human will be taking

            for m in moves:
                distance = abs(m.destination.x - closest_zombie_pos.x) + abs(m.destination.y - closest_zombie_pos.y)  # calculate manhattan distance

                if distance > move_distance:  # If distance is further, that's our new choice!
                    move_distance = distance
                    move_choice = m

            choices.append(move_choice)  # add the choice to the list
            
            my_game_state.run_move(choices)

        return choices

    def decide_attacks(
            self, 
            possible_attacks: dict[str, list[AttackAction]], 
            game_state: GameState
            ) -> list[AttackAction]:
        choices = []
        
        global my_cooldowns
        global my_game_state
        print(my_game_state.is_equal(game_state))

        for [character_id, attacks] in possible_attacks.items():
            if len(attacks) == 0:  # No choices... Next!
                continue

            pos = game_state.characters[character_id].position  # position of the human
            closest_zombie = None  # Closest zombie in range
            closest_zombie_distance = 404  # Distance between closest zombie and human

            # Iterate through zombies in range and find the closest one
            for a in attacks:
                if a.type is AttackActionType.CHARACTER:
                    attackee_pos = game_state.characters[a.attacking_id].position  # Get position of zombie in question
                    
                    distance = abs(attackee_pos.x - pos.x) + abs(attackee_pos.y - pos.y)  # Get distance between the two

                    if distance < closest_zombie_distance:  # Closer than current? New target!
                        closest_zombie = a
                        closest_zombie_distance = distance

            if closest_zombie:  # Attack the closest zombie, if there is one
                choices.append(closest_zombie)
                
            my_game_state.run_attack(choices)

        return choices

    def decide_abilities(
            self, 
            possible_abilities: dict[str, list[AbilityAction]], 
            game_state: GameState
            ) -> list[AbilityAction]:
        choices = []
        
        global my_cooldowns
        global my_game_state
        print(my_game_state.is_equal(game_state))

        for [character_id, abilities] in possible_abilities.items():
            if len(abilities) == 0:  # No choices? Next!
                continue

            # Since we only have medics, the choices must only be healing a nearby human
            human_target = abilities[0]  # the human that'll be healed
            least_health = 999  # The health of the human being targeted

            for a in abilities:
                health = game_state.characters[a.character_id_target].health  # Health of human in question

                if health < least_health:  # If they have less health, they are the new patient!
                    human_target = a
                    least_health = health

            if human_target:  # Give the human a cookie
                choices.append(human_target)
                
            my_game_state.run_ability(choices)
        
        return choices
