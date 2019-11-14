from dlgo.agents import MinimaxAgent
from dlgo.go import Move, Player, GameState
from dlgo.utils import print_board, print_move, point_from_coords


def main():
    game = GameState.new_game(5, 7.5)
    bot = MinimaxAgent(3)

    while not game.is_over:
        print(chr(27) + '[2J')
        if game.last_move is None:
            print(f'{game.next_player} to move')
        else:
            print_move(game.next_player.other, game.last_move)
        print('')
        print_board(game.board)

        if game.next_player is Player.black:
            human_move = input('\n-- ')
            if human_move == 'pass':
                move = Move.pass_turn()
            elif human_move == 'resign':
                move = Move.resign()
            else:
                point = point_from_coords(human_move.strip())
                move = Move.play(point)
        else:
            move = bot.select_move(game)
        game = game.apply_move(move)


if __name__ == '__main__':
    main()
