import math
import random

from dlgo.agents.base import Agent
from dlgo.agents.random import FastConstrainedRandomAgent


def select_random_child(node):
    return random.choice(node.children)


def select_uct_child(node, temperature):
    log_rollouts = math.log(node.rollouts)

    best_child = None
    best_uct = -1

    for child in node.children:
        uct = child.winning_fraction + temperature * math.sqrt(log_rollouts / child.rollouts)

        if uct > best_uct:
            best_child = child
            best_uct = uct

    return best_child


class MCTSNode:
    def __init__(self, game, parent=None):
        self.state = game

        self.parent = parent
        self.children = []

        self.rollouts = 0
        self.wins = 0

        self.unvisited_moves = game.possible_moves()

    def expand(self):
        index = random.randint(0, len(self.unvisited_moves) - 1)
        move = self.unvisited_moves.pop(index)

        child = MCTSNode(self.state.apply_move(move), self)
        self.children.append(child)

        return child

    def propagate_result(self, win):
        self.rollouts += 1
        if win:
            self.wins += 1

        if self.parent is not None:
            self.parent.propagate_result(not win)

    @property
    def fully_expanded(self):
        return len(self.unvisited_moves) == 0

    @property
    def is_leaf(self):
        return len(self.children) == 0

    @property
    def winning_fraction(self):
        return self.wins / self.rollouts

    def print(self, max_depth=3, indent=''):
        if max_depth < 0:
            return

        if self.parent is None:
            print('%sroot' % indent)
        else:
            player = self.parent.state.next_player
            move = self.state.last_move
            print('%s%s %s %d %.3f' % (
                indent, str(player), str(move.point),
                self.rollouts, self.winning_fraction,
            ))

        for child in sorted(self.children, key=lambda n: n.rollouts, reverse=True):
            child.print(max_depth - 1, indent + '  ')


class MCTSAgent(Agent):
    def __init__(self, rollouts, rollout_agent=FastConstrainedRandomAgent(), selection_policy=select_random_child):
        self.rollouts = rollouts
        self.rollout_agent = rollout_agent
        self.selection_policy = selection_policy

    def select_move(self, game):
        tree = MCTSNode(game)

        for _ in range(self.rollouts):
            node = tree
            while node.fully_expanded and not node.is_leaf:
                node = self.selection_policy(node)

            if not node.fully_expanded:
                node = node.expand()

            next_state = node.state
            while not next_state.is_over():
                next_state = next_state.apply_move(self.rollout_agent.select_move(next_state))

            win = next_state.winner == node.parent.state.next_player
            while node is not None:
                node.rollouts += 1
                if win:
                    node.wins += 1
                node = node.parent
                win = not win

        best_move = None
        best_winning_fraction = -1

        for child in tree.children:
            if child.winning_fraction > best_winning_fraction:
                best_move = child.state.last_move
                best_winning_fraction = child.winning_fraction

        # tree.print()

        return best_move


class StandardMCTSAgent(MCTSAgent):
    def __init__(self, rollouts, temperature):
        super().__init__(rollouts, selection_policy=lambda n: select_uct_child(n, temperature))
