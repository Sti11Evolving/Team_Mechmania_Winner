from strategy.pyengine import PyGameState
import random


def evaluate_state(state:PyGameState):
    human_score, zombie_score = state.get_scores()
    if state.get_is_zombie_turn():
        return zombie_score - human_score
    else:
        return human_score - zombie_score
    
def get_action_set(state: PyGameState):
    return [state.get_possible_actions()[:3], state.get_possible_actions()[3:6]]