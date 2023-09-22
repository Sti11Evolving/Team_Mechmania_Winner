# This is a simple zombie strategy:
# Move directly towards the closest human. If there are any humans in attacking range, attack a random one.
# If there are no humans in attacking range but there are obstacles, attack a random obstacle.

import random
import MCTS
from game.character.action.ability_action import AbilityAction
from game.character.action.attack_action import AttackAction
from game.character.action.move_action import MoveAction
from game.game_state import GameState
from game.character.action.attack_action_type import AttackActionType
from strategy.strategy import Strategy


class WinningZombieStrategy(Strategy):

    def decide_moves(
            self, 
            possible_moves: dict[str, list[MoveAction]], 
            game_state: GameState
            ) -> list[MoveAction]:
        
        choices = []

        for [character_id, moves] in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue

            pos = game_state.characters[character_id].position  # position of the zombie
            closest_human_pos = pos  # default position is zombie's pos
            closest_human_distance = 1984  # large number, map isn't big enough to reach this distance

            # Iterate through every human to find the closest one
            for c in game_state.characters.values():
                if c.is_zombie:
                    continue  # Fellow zombies are frens :D, ignore them

                distance = abs(c.position.x - pos.x) + abs(c.position.y - pos.y) # calculate manhattan distance between human and zombie
                if distance < closest_human_distance:  # If distance is closer than current closest, replace it!
                    closest_human_pos = c.position
                    closest_human_distance = distance

            # Move as close to the human as possible
            move_distance = 1337  # Distance between the move action's destination and the closest human
            move_choice = moves[0]  # The move action the zombie will be taking
            for m in moves:
                distance = abs(m.destination.x - closest_human_pos.x) + abs(m.destination.y - closest_human_pos.y)  # calculate manhattan distance

                # If distance is closer, that's our new choice!
                if distance < move_distance:  
                    move_distance = distance
                    move_choice = m

            choices.append(move_choice)  # add the choice to the list

        return choices

    def decide_attacks(
            self, 
            possible_attacks: dict[str, list[AttackAction]], 
            game_state: GameState
            ) -> list[AttackAction]:
        
        print(MCTS.test)

        choices = []

        for [character_id, attacks] in possible_attacks.items():
            if len(attacks) == 0:  # No choices... Next!
                continue

            humans = []  # holds humans that are in range

            # Gather list of humans in range
            for a in attacks:
                if a.type is AttackActionType.CHARACTER:
                    humans.append(a)

            if humans:  # Attack a random human in range
                choices.append(random.choice(humans))
            else:  # No humans? Shame. The targets in range must be terrain. May as well attack one.
                choices.append(random.choice(attacks))

        return choices
