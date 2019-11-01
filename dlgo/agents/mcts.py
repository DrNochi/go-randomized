import math
import multiprocessing
import random

from dlgo.agents.base import Agent
from dlgo.agents.random import FastConstrainedRandomAgent

_worker_rollout_agent = None


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
            print('%sroot %d %.3f' % (indent, self.rollouts, self.winning_fraction))
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

        worker_count = multiprocessing.cpu_count()
        with multiprocessing.Pool(worker_count, initializer=self._worker_initializer,
                                  initargs=(self.rollout_agent,)) as workers:

            prepared = []
            running = []
            finished = []

            rollout = 0
            while rollout < self.rollouts:
                if len(running) < worker_count and prepared:
                    rollout += 1
                    node = prepared.pop()
                    running.append((
                        workers.apply_async(self._rollout_worker, (node.state, node.parent.state.next_player)),
                        node))
                elif len(prepared) < worker_count:
                    node = self._select_node(tree)
                    prepared.append(node)

                for win, node in finished:
                    self._propagate_result(node, win)
                finished.clear()

                for job, node in running:
                    if job.ready():
                        win = job.get()
                        finished.append((win, node))
                running = [(job, node) for job, node in running if not job.ready()]

            workers.close()
            workers.join()

            for win, node in finished:
                self._propagate_result(node, win)
            for job, node in running:
                self._propagate_result(node, job.get())

        best_move = None
        best_winning_fraction = -1

        for child in tree.children:
            if child.winning_fraction > best_winning_fraction:
                best_move = child.state.last_move
                best_winning_fraction = child.winning_fraction

        # tree.print()

        return best_move

    def _select_node(self, node):
        while node.fully_expanded and not node.is_leaf:
            node.rollouts += 1
            node = self.selection_policy(node)

        if not node.fully_expanded:
            node.rollouts += 1
            node = node.expand()

        node.rollouts += 1
        return node

    @staticmethod
    def _worker_initializer(rollout_agent):
        global _worker_rollout_agent
        _worker_rollout_agent = rollout_agent

    @staticmethod
    def _rollout_worker(state, current_player):
        while not state.is_over():
            state = state.apply_move(_worker_rollout_agent.select_move(state))
        return state.winner == current_player

    @staticmethod
    def _propagate_result(node, win):
        while node is not None:
            if win:
                node.wins += 1
            node = node.parent
            win = not win


class StandardMCTSAgent(MCTSAgent):
    def __init__(self, rollouts, temperature):
        super().__init__(rollouts, selection_policy=lambda n: select_uct_child(n, temperature))
