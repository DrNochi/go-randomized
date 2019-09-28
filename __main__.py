from dlgo.agent.naive import RandomBot
from dlgo.goboard import GameState, Move
from dlgo.gotypes import Player
from dlgo.utils import print_board, print_move, point_from_coords
from dlgo.scoring import GameResult
import time


bots = {
    "Random": RandomBot
}


def clear_terminal():
    print(chr(27) + "[2J")


def print_header():
    print("RANDOMIZED - Go Bot")
    print("-------------------")
    print("")


def print_game_state(game_state):
    clear_terminal()
    print_header()

    print_move(game_state.next_player.other,
               game_state.last_move) if game_state.last_move is not None else print("")
    print("")
    print_board(game_state.board)
    print("")


def choose():
    return input("-- ")


def choose_bot(prompt):
    print(prompt)
    i = 1
    i_to_key = {}
    for b in bots:
        print("{n}. {bot}".format(n=i, bot=b))
        i_to_key[i] = b
        i += 1
    print("")
    return bots[i_to_key[int(choose())]]()


clear_terminal()
print_header()
print("Choose a game mode:")
print("1. Bot vs Bot")
print("2. Human vs Bot")
print("3. Human vs Human")
print("")
game_mode = int(choose())

players = {
    Player.black: None,
    Player.white: None
}

if game_mode == 1:
    clear_terminal()
    print_header()
    players[Player.black] = choose_bot("Choose a black bot:")
    print("\n")
    players[Player.white] = choose_bot("Choose a white bot:")
elif game_mode == 2:
    clear_terminal()
    print_header()
    bot = choose_bot("Choose a bot:")

    print("\n")

    print("Choose your color:")
    print("1. Black")
    print("2. White")
    print("")
    color = int(choose())

    if color == 1:
        players[Player.white] = bot
    elif color == 2:
        players[Player.black] = bot
elif game_mode == 3:
    pass


clear_terminal()
print_header()
board_size = int(input("Choose a board size: "))
komi = float(input("Set komi: "))

slow_down_bot = True
if game_mode != 3:
    slow_down_bot = input("Slow down bot (y/n): ") == "y"

game = GameState.new_game(board_size)

while not game.is_over():
    print_game_state(game)

    bot = players[game.next_player]
    if bot is None:
        human_move = choose()
        if human_move == "pass":
            move = Move.pass_turn()
        elif human_move == "resign":
            move = Move.resign()
        else:
            point = point_from_coords(human_move.strip())
            move = Move.play(point)
    else:
        if slow_down_bot:
            time.sleep(0.3)
        move = bot.select_move(game)

    game = game.apply_move(move)

print_game_state(game)
print(GameResult.compute(game, komi))
