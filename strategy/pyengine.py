from enum import Enum
import copy

from game.game_state import GameState

from game.character.character import Character
from game.character.character_class_type import CharacterClassType
from game.character.action.ability_action import AbilityAction
from game.character.action.attack_action import AttackAction
from game.character.action.ability_action_type import AbilityActionType
from game.character.action.attack_action_type import AttackActionType
from game.character.action.move_action import MoveAction

from game.terrain.terrain import Terrain
from game.util.position import Position

MAX_HEALTH = 10
ABILITY_COOLDOWN = 6
STUNNED_DURATION = 1

class AbilityType(Enum):
    BUILD_BARRICADE = "BUILD_BARRICADE"
    HEAL = "HEAL"
    MOVE_OVER_BARRICADES = "MOVE_OVER_BARRICADES",
    ONESHOT_TERRAIN = "ONESHOT_TERRAIN",
    
class_stats = {
    CharacterClassType.NORMAL: {
        "Health": 1,
     "Move_Speed": 3, 
     "Attack_Range": 4, 
     "Attack_Cooldown": 8,
     "Ability": None,
     },
    
    CharacterClassType.ZOMBIE: {
        "Health": 1,
     "Move_Speed": 5, 
     "Attack_Range": 1, 
     "Attack_Cooldown": 0,
     "Ability": None,
     },
    
    CharacterClassType.MARKSMAN: {
        "Health": 1,
     "Move_Speed": 3, 
     "Attack_Range": 4, 
     "Attack_Cooldown": 8,
     "Ability": None,
     },
    
    CharacterClassType.TRACEUR : {
        "Health": 1,
     "Move_Speed": 4, 
     "Attack_Range": 2, 
     "Attack_Cooldown": 4,
     "Ability": AbilityType.MOVE_OVER_BARRICADES,
     },
    
    CharacterClassType.MEDIC: {
        "Health": 2,
     "Move_Speed": 3, 
     "Attack_Range": 3, 
     "Attack_Cooldown": 6,
     "Ability": AbilityType.HEAL,
     },
    
    CharacterClassType.BUILDER : {
        "Health": 1,
     "Move_Speed": 3, 
     "Attack_Range": 4, 
     "Attack_Cooldown": 6,
     "Ability": AbilityType.BUILD_BARRICADE,
     },
    
    CharacterClassType.DEMOLITIONIST: {
        "Health": 1,
     "Move_Speed": 3, 
     "Attack_Range": 2, 
     "Attack_Cooldown": 6,
     "Ability": AbilityType.ONESHOT_TERRAIN,
     },
    
}

def position_to_id(position: Position):
    return f"({position.x}, {position.y})"

def add_positions(p1, p2):
    return Position(p1.x+p2.x, p1.y+p2.y)

class CharacterState:
    def __init__(self, character: Character, cooldowns: tuple(int, int)):
        self.id = character.id
        self.position = character.position
        self.is_zombie = character.is_zombie
        self.class_type = character.class_type
        self.health = character.health
        self.move_speed = class_stats[self.class_type]["Move_Speed"]
        self.attack_range = class_stats[self.class_type]["Attack_Range"]
        self.ability = class_stats[self.class_type]["Ability"]
        self.stunned_effect_left = int(character.is_stunned)
        self.attack_cooldown_left = cooldowns[0]
        self.ability_cooldown_left = cooldowns[1]

    def get_id(self):
        return self.id

    def get_position(self):
        return self.position
    
    def is_zombie(self):
        return self.is_zombie
    
    def is_destroyed(self):
        return self.health == 0
    
    def is_stunned(self):
        return self.stunned_effect_left > 0
    
    def can_move(self):
        return not self.is_stunned()
    
    def can_attack(self):
        return self.attack_cooldown_left == 0 and (not self.is_stunned())
    
    def can_ability(self):
        return self.ability_cooldown_left == 0 and (not self.is_stunned())

    def damage(self):
        if self.health > 0:
            self.health -= 1
        
    def heal(self):
        self.health += 1
        min(self.health, MAX_HEALTH)
        
    def reset_ability_cooldown_left(self):
        self.ability_cooldown_left = ABILITY_COOLDOWN + 1
        
    def reset_attack_cooldown_left(self):
        self.attack_cooldown_left = self.attack_cooldown + 1
        
    def stun(self):
        self.stunned_effect_left = STUNNED_DURATION + 1
        
    def apply_cooldown_and_effect_decay(self):
        if (self.attack_cooldown_left > 0):
            self.attack_cooldown_left -= 1

        if (self.ability_cooldown_left > 0):
            self.ability_cooldown_left -= 1

        if (self.stunned_effect_left > 0):
            self.stunned_effect_left -= 1
        
    def make_zombie(self):
        self.is_zombie = True
        self.class_type = CharacterClassType.ZOMBIE
        self.move_speed = 5
        self.attack_range = 1
        self.ability = None
        
    def clear_actions(self):
        self.attack_action = None
        self.ability_action = None


class TerrainState:
    def __init__(self, terrain: Terrain|None, id, position, health, can_attack_through):
        if terrain:
            self.id = terrain.id
            self.position = terrain.position
            self.health = terrain.health
            self.can_attack_through = terrain.can_attack_through
        else:
            self.id = id
            self.position = position
            self.health = health
            self.can_attack_through = can_attack_through

    def get_id(self):
        return self.id

    def get_position(self):
        return self.position

    def damage(self):
        if self.health > 0:
            self.health -= 1

    def is_destroyable(self):
        return self.health >= 0

    def can_attack_through(self):
        return self.can_attack_through

    def is_destroyed(self):
        return self.health == 0


class PyGameState:
    BOARD_SIZE = 100
    TURNS = 200
    STARTING_ZOMBIES = 5

    DIRECTIONS = [Position(0, 1), Position(0, -1), Position(1, 0), Position(-1, 0)]
    DIAGONAL_DIRECTIONS = [Position(1, 1), Position(1, -1), Position(-1, 1), Position(-1, -1)]

    def __init__(self, game_state: GameState, cooldowns: dict(str, tuple(int, int))):
        self.turn: int = game_state.turn
        self.character_states = list(CharacterState(character, cooldowns[character.id]) for character in game_state.characters.values())
        self.terrain_states = list(Terrain(terrain) for terrain in game_state.terrains.values())

    def get_character_states(self):
        return self.character_states

    def get_terrain_states(self):
        return self.terrain_states

    def get_turn(self):
        return self.turn

    def run_turn(self, move_actions: list[MoveAction], attack_actions: list[AttackAction], ability_actions: list[AbilityAction]) -> GameState:
        new_state = copy.deepcopy(self)
        new_state.turn += 1

        player = new_state.zombie_player if new_state.turn % 2 == 1 else new_state.human_player

        new_state.apply_clear_actions(new_state.character_states)
        new_state.apply_move_actions(move_actions)

        new_state.apply_attack_actions(attack_actions)
        new_state.apply_cooldown_and_effect_decay(player.is_zombie())

        new_state.apply_ability_actions(ability_actions)
        
        return new_state

    def get_zombies_count(self):
        return sum(1 for character_state in self.character_states.values() if character_state.is_zombie())

    def get_humans_count(self):
        return sum(1 for character_state in self.character_states.values() if not character_state.is_zombie())

    def is_finished(self):
        if self.get_humans_count() <= 0:
            return True

        return self.turn >= self.TURNS

    def get_scores(self):
        zombies_count = self.get_zombies_count()
        humans_count = self.get_humans_count()
        humans_infected = zombies_count - self.STARTING_ZOMBIES
        SCALE_FACTOR = 5
        humans_score = self.turn + (humans_count * SCALE_FACTOR)
        zombies_score = self.TURNS - self.turn + (humans_infected * SCALE_FACTOR)

        return (humans_score, zombies_score)

    def get_stats(self):
        zombies_count = self.get_zombies_count()
        humans_count = self.get_humans_count()
        return (self.turn, humans_count, zombies_count)

    def apply_clear_actions(self, character_states):
        for character_state in character_states.values():
            character_state.clear_actions()

    def apply_move_actions(self, move_actions):
        for move_action in move_actions:
            character_id = move_action.executing_character_id
            destination = move_action.destination

            self.character_states[character_id].position = destination

    def apply_attack_actions(self, attack_actions):
        for attack_action in attack_actions:
            attacker_id = attack_action.executing_character_id
            target_id = attack_action.attacking_id
            attack_type = attack_action.type
            
            if attack_type == AttackActionType.CHARACTER:
                target_state = self.character_states[target_id]
                target_state.damage()
                if target_state.is_destroyed():
                    target_state.make_zombie()
            else:
                if self.character_states[attacker_id].ability == AbilityType.ONESHOT_TERRAIN:
                    self.terrain_states[target_id].health = 0
                else:
                    self.terrain_states[target_id].damage()

    def apply_cooldown_and_effect_decay(self, is_zombie):
        for character_state in self.character_states.values():
            if character_state.is_zombie() != is_zombie:
                continue

            character_state.apply_cooldown_and_effect_decay()

    def apply_ability_actions(self, ability_actions):
        for ability_action in ability_actions:
            action_type = ability_action.type
            target_id = ability_action.character_id_target
            target_position = ability_action.positional_target

            if action_type == AbilityActionType.HEAL:
                self.character_states[target_id].heal()

            if action_type == AbilityActionType.BUILD_BARRICADE:
                barricade = TerrainState(None, position_to_id(target_position), target_position, 1, True)
                self.terrain_states.append(barricade)


    def get_terrain_state(self, position):
        return self.terrain_states.get(position_to_id(position))
    
    def get_character_state_at_position(self, position):
        return self.character_states.get(position_to_id(position))

    def is_valid_attack(self, attacker_state, target_state):
        if attacker_state.is_destroyed() or target_state.is_destroyed():
            return False

        if attacker_state.is_zombie() and target_state.is_zombie():
            return False

        if not attacker_state.is_zombie() and not target_state.is_zombie():
            return False

        return True
    
    def get_blocking_terrain(self, pos, ignore_barricades):
        terrain_state = self.get_character_state_at_position(pos)
        
        if terrain_state == None:
            return None

        if terrain_state.is_destroyed():
            blocking = None

        if ignore_barricades and terrain_state.health == 1:
            blocking = None

        return blocking
    
    def in_bounds(self, pos):
        return (0 <= pos.x < self.BOARD_SIZE) and (0 <= pos.y < self.BOARD_SIZE)

    def can_traverse_through(self, pos, is_attack, ignore_barricades):
        if not pos.in_bounds():
            return False

        blocking = self.get_blocking_terrain(pos, ignore_barricades and is_attack)

        if blocking is not None:
            if is_attack and blocking.can_attack_through():
                return True
            return False

        return True

    def get_tiles_in_range(self, start, range, diagonal, is_attack, ignore_barricades, searched = []) -> dict[Position]:
        moves: dict = {}

        if range < 0:
            return moves

        can_traverse_through_start = self.can_traverse_through(start, is_attack, ignore_barricades)
        moves[position_to_id(start)] = start

        if range == 0 or not can_traverse_through_start:
            return moves

        directions = self.DIAGONAL_DIRECTIONS+self.DIRECTIONS if diagonal else self.DIRECTIONS

        for direction in directions:
            new_position = add_positions(start, direction)
            if position_to_id(new_position) in moves:
                continue

            if not is_attack:
                can_traverse = self.can_traverse_through(new_position, is_attack, ignore_barricades)

                if not can_traverse:
                    continue

            moves[position_to_id(new_position)] = new_position
            moves.update(self.get_tiles_in_range(new_position, range - 1, diagonal, is_attack, ignore_barricades, moves))

        return moves

    def get_possible_move_actions(self, is_zombie):
        move_actions = []

        for character_state in self.character_states.values():
            if character_state.is_zombie() != is_zombie:
                continue
            
            if character_state.is_stunned():
                continue

            position = character_state.get_position()
            
            tiles = self.get_tiles_in_range(position, character_state.move_speed, False, False)

            for tile in tiles:
                move_action = MoveAction(character_state.id, tile)
                move_actions.append(move_action)

        return move_actions

    def get_possible_attack_actions(self, is_zombie):
        attack_actions = []

        for character_state in self.character_states.values():
            if character_state.is_zombie != is_zombie:
                continue
            
            attackable = self.get_tiles_in_range(character_state.position, character_state.attack_range, character_state.is_zombie, True, False)

            for position in attackable:
                target = self.get_character_state_at_position(position)
                if target and target.is_zombie != character_state.is_zombie:
                    AttackAction(character_state.id, target.id, AttackActionType.CHARACTER)
                
                target = self.get_terrain_state(position)
                if target:
                    AttackAction(character_state.id, target.id, AttackActionType.TERRAIN)
                    

        return attack_actions

    def get_possible_ability_actions(self, is_zombie):
        ability_actions = []

        for character_state in self.character_states.values():
            if character_state.is_zombie() != is_zombie:
                continue

            if character_state.ability == AbilityType.HEAL:
                targetable = self.get_tiles_in_range(character_state.position, character_state.attack_range, False, False, False)
                for position in targetable:
                    target = self.get_character_state_at_position(position)
                    if (target != None) and (not target.is_zombie):
                        ability_actions += AbilityAction(character_state.id, target.id, None, AbilityActionType.HEAL)
                        
            elif character_state.ability == AbilityType.BUILD_BARRICADE:
                targetable = self.get_tiles_in_range(character_state.position, character_state.attack_range, False, False, False)
                for position in targetable:
                    target = self.get_terrain_state(position)
                    if target == None:
                        ability_actions += AbilityAction(character_state.id, None, position, AbilityActionType.BUILD_BARRICADE)

        return ability_actions
