from dlgo.go import GameState, Player, Score


def simulate_game(board_size, komi, black_player, white_player):
    game = GameState.new_game(board_size, komi)

    agents = {
        Player.black: black_player,
        Player.white: white_player,
    }

    while not game.is_over:
        next_move = agents[game.next_player].select_move(game)
        game = game.apply_move(next_move)

    return game, Score.compute(game)
