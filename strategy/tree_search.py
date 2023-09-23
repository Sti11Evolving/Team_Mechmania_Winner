from typing import *
import time
import math

from game.game_state import GameState
from game.character.character import Character
from strategy.pyengine import PyGameState, GamePhase
from strategy.state_evaluation import evaluate_state, get_action_set

class Node:
    def __init__(self, state: PyGameState, parent, actions: list = []):
        self.state: PyGameState = state
        self.parent:Node = parent
        self.is_terminal = (state.turn == 200) or (state.get_humans_count() == 0)
        self.is_fully_expanded = self.is_terminal
        self.is_zombie_turn = state.get_is_zombie_turn()
        self.actions = actions
        self.to_explore = []
        self.num_visits = 0
        self.total_reward = 0
        self.children: list[Node] = []
        
class TreeSearch:
    def __init__(self, root_state: GameState, cooldowns, phase: GamePhase, exploration_constant, eps, player_is_zombie, time_limit = 2000):
        self.root: Node = Node(PyGameState(root_state, cooldowns, phase), None)
        self.exploration_constant = exploration_constant
        self.eps = eps
        self.player_is_zombie = player_is_zombie
        self.time_limit = time_limit
    
    def search(self):
        time_limit = time.time() + self.time_limit / 1000
        
        num_rounds = 0
        while time.time() < time_limit:
            self.execute_round()
            num_rounds += 1
            
        best_child = self.get_best_child(self.root, 0)
        
        if best_child:
            print(f"Value: {best_child.total_reward} \t num rounds: {num_rounds}")
        
        if self.player_is_zombie:
            if best_child == None:
                return [[], []]
            return [best_child.actions, self.get_best_child(best_child, 0).actions]
        
        else: 
            if best_child == None:
                return [[], [], []]
            return [best_child.actions, self.get_best_child(best_child, 0).actions, self.get_best_child(self.get_best_child(best_child, 0), 0).actions]
    
    
    def execute_round(self):
        node = self.select_node(self.root)
        if node == None:
            print("Fully explored tree")
            return
        reward = evaluate_state(node.state)
        self.back_propogate(node, reward)
        
    def select_node(self, node: Node):
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_child(node, self.exploration_constant)
            else:
                return self.expand(node)
            
        return node
    
    def expand(self, node: Node):
        if not node.is_fully_expanded and len(node.to_explore) == 0:
            actions = get_action_set(node.state)
            node.to_explore += actions
        
        if not node.is_fully_expanded:
            action = node.to_explore.pop()
            new_node = Node(node.state.run_actions(action), node, action)
            node.children.append(new_node)
            if len(node.to_explore) == 0:
                node.is_fully_expanded = True
                
            return new_node
                
    def back_propogate(self, node: Node, reward):
        is_zombie_turn = node.is_zombie_turn
        while node is not None:
            node.num_visits += 1
            if is_zombie_turn == node.is_zombie_turn:
                node.total_reward += reward
            else:
                node.total_reward -= reward
                is_zombie_turn = node.is_zombie_turn
                
            node = node.parent
            reward *= self.eps
            
    def get_best_child(self, node: Node, exploration_value):
        best_value = float("-inf")
        best_node = None
        
        for child in node.children:
            node_value = child.total_reward / child.num_visits + exploration_value * math.sqrt(2 * math.log(node.num_visits) / child.num_visits)
            if node_value > best_value:
                best_value = node_value
                best_node = child
                
        return best_node
            
            
            
        