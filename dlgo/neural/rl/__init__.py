from dlgo.go import Player
from dlgo.utils import simulate_game
from .experience import ExperienceCollector, ExperienceBuffer


def simulate_games(num_games, board_size, komi, agent1, agent2):
    collector1 = ExperienceCollector()
    collector2 = ExperienceCollector()

    color1 = Player.black
    for i in range(num_games):
        collector1.begin_episode()
        agent1.set_collector(collector1)
        collector2.begin_episode()
        agent2.set_collector(collector2)

        if color1 is Player.black:
            black_player, white_player = agent1, agent2
        else:
            white_player, black_player = agent2, agent1

        game, score = simulate_game(board_size, komi, black_player, white_player)

        if score.winner is color1:
            collector1.complete_episode(reward=1)
            collector2.complete_episode(reward=-1)
        else:
            collector2.complete_episode(reward=1)
            collector1.complete_episode(reward=-1)

        color1 = color1.other

    return ExperienceBuffer.combine_experience([collector1, collector2])
