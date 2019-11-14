from dlgo.go import Score, Move
from .agent import Agent


class TerminationStrategy:
    def should_pass(self, game_state):
        return False

    def should_resign(self, game_state):
        return False


class PassWhenOpponentPasses(TerminationStrategy):
    def should_pass(self, game_state):
        return game_state.last_move is not None and game_state.last_move.is_pass


class ResignLargeMargin(TerminationStrategy):
    def __init__(self, own_color, margin):
        self.own_color = own_color
        self.margin = margin

    def should_resign(self, game_state):
        score = Score.compute(game_state)
        return score.winner is not self.own_color and score.winning_margin >= self.margin


class TerminationAgent(Agent):
    def __init__(self, agent, strategy=None):
        self.base_agent = agent
        self.strategy = strategy or TerminationStrategy()

    def select_move(self, game_state):
        if self.strategy.should_pass(game_state):
            return Move.pass_turn()
        elif self.strategy.should_resign(game_state):
            return Move.resign()
        return self.base_agent.select_move(game_state)
