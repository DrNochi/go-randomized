from dlgo.go import Move


def is_ladder_capture(game_state, candidate, recursion_depth=50):
    escape_player = game_state.next_player.other
    return any(_is_ladder(True, game_state, candidate, ladder_end, recursion_depth)
               for ladder_end in _guess_adjacent_ladder_ends(game_state, candidate, escape_player))


def is_ladder_escape(game_state, candidate, recursion_depth=50):
    escape_player = game_state.next_player
    return any(_is_ladder(False, game_state, candidate, ladder_end, recursion_depth)
               for ladder_end in _guess_adjacent_ladder_ends(game_state, candidate, escape_player))


def _is_ladder(try_capture, game_state, candidate, ladder_end, recursion_depth):
    if recursion_depth == 0:
        return False

    candidate_move = Move.play(candidate)
    if not game_state.is_valid_move(candidate_move):
        return False

    current_state = game_state.apply_move(candidate_move)
    ladder = current_state.board[ladder_end]

    if try_capture:
        if ladder is None:
            return True
    else:
        if ladder.liberty_count >= 3:
            return True
        elif ladder.liberty_count == 1:
            return False

    opponent_attempts = [_is_ladder(not try_capture, current_state, candidate, ladder_end, recursion_depth - 1)
                         for candidate in ladder.liberties]
    return not any(opponent_attempts)


def _is_potential_ladder(player, group):
    return group is not None and group.color is player and group.liberty_count <= 2


def _guess_adjacent_ladder_ends(game_state, point, escape_player):
    return {
        nb for nb in game_state.board.neighbors(point)
        if _is_potential_ladder(escape_player, game_state.board[nb])
    }
