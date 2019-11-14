import gzip
import multiprocessing
import os
import shutil
import tarfile
import uuid

import numpy as np
from sgfmill.sgf import Sgf_game

from dlgo.data.generators import NPZGameDataGenerator
from dlgo.go import Player, Point, Move, Board, GameState
from .index import KGSIndex
from .sampling import Sampler
from ..dataset import DataSet


def _process_one_archive(args):
    self, archive, games = args
    return self._process_archive(archive, games)


class KGSDataSet(DataSet):
    def __init__(self, encoder, cache='.cache/datasets/kgs'):
        self.encoder = encoder
        self.cache = cache

        if not os.path.isdir(cache):
            os.makedirs(cache)

        self.index = KGSIndex(os.path.join(self.cache, 'index'))
        self.sampler = Sampler(self.index)

        self._setup_data_cache()

    def _setup_data_cache(self):
        configuration = str(type(self.encoder))
        configuration_id = None

        file = os.path.join(self.cache, 'configurations')
        if os.path.isfile(file):
            with open(file, 'r') as configs:
                line = configs.readline()
                while line != '':
                    config, config_id = line.split('|')
                    if config == configuration:
                        configuration_id = config_id
                        break
                    line = configs.readline()
        if configuration_id is None:
            configuration_id = uuid.uuid4()
            with open(file, 'a') as configs:
                configs.write(f'{configuration}|{configuration_id}')

        self.data_cache = os.path.join(self.cache, str(configuration_id))

        if not os.path.isdir(self.data_cache):
            os.makedirs(self.data_cache)

    def load_data(self, data_type, samples, use_generator=False):
        sample_data = self.sampler.draw_data(data_type, samples)

        archives = set()
        games_by_archive = {}

        for filename, game in sample_data:
            archives.add(filename)
            if filename not in games_by_archive:
                games_by_archive[filename] = []
            games_by_archive[filename].append(game)

        data_files = self._invoke_workers(archives, games_by_archive)

        return (NPZGameDataGenerator(data_files) if use_generator
                else self._consolidate_data(data_files))

    def _invoke_workers(self, archives, games_by_archive):
        args = [(self, archive, games_by_archive[archive]) for archive in archives]
        with multiprocessing.Pool() as pool:
            return [game for archive in pool.map(_process_one_archive, args) for game in archive]

    def _unzip_data(self, archive):
        path = os.path.join(self.index.cache, archive)
        decompressed_path = path[:-3]

        if not os.path.isfile(decompressed_path):
            with gzip.open(path) as compressed:
                with open(decompressed_path, 'wb') as decompressed:
                    shutil.copyfileobj(compressed, decompressed)

        return decompressed_path

    def _process_archive(self, archive, games):
        archive_data_cache = os.path.join(self.data_cache, archive[:-7])
        if not os.path.isdir(archive_data_cache):
            os.makedirs(archive_data_cache)

        decompressed = self._unzip_data(archive)
        tar = tarfile.open(decompressed)
        game_files = tar.getnames()

        return [self._process_game(tar, game_files[i + 1]) for i in games]

    def _process_game(self, archive, game_file):
        filename = os.path.join(self.data_cache,
                                os.path.basename(archive.name)[:-4],
                                os.path.basename(game_file)[:-4] + '.npz')
        if os.path.isfile(filename):
            return filename, np.load(filename)['features'].shape[0]

        assert game_file.endswith('sgf')

        positions = self._count_moves(archive, game_file)
        features = np.zeros((positions,) + self.encoder.board_shape)
        labels = np.zeros((positions, self.encoder.move_shape))

        sgf_content = archive.extractfile(game_file).read()
        sgf = Sgf_game.from_bytes(sgf_content)

        game = self._get_starting_position(sgf)

        counter = 0
        for node in sgf.main_sequence_iter():
            color, point = node.get_move()

            if color is not None:
                try:
                    assert game.next_player is (Player.black if color == 'b' else Player.white)

                    move = Move.play(Point(point[0] + 1, point[1] + 1)) if point is not None else Move.pass_turn()

                    if move.is_play:
                        features[counter] = self.encoder.encode_board(game)
                        labels[counter] = self.encoder.encode_move(move)
                        counter += 1

                    game = game.apply_move(move)
                except AssertionError:
                    print(f'>>> Corrupted sgf: {archive} {game_file}')

        np.savez_compressed(filename, features=features, labels=labels)

        return filename, positions

    @staticmethod
    def _count_moves(archive, game_file):
        if not game_file.endswith('.sgf'):
            raise ValueError(game_file + ' is not a valid sgf')

        sgf_content = archive.extractfile(game_file).read()
        sgf = Sgf_game.from_bytes(sgf_content)

        moves = 0
        for node in sgf.main_sequence_iter():
            color, point = node.get_move()
            if color is not None and point is not None:
                moves += 1

        return moves

    @staticmethod
    def _get_starting_position(sgf):
        if sgf.get_handicap() is not None and sgf.get_handicap() != 0:
            board = Board(sgf.get_size())

            for setup in sgf.get_root().get_setup_stones():
                for point in setup:
                    row, col = point
                    board.place_stone(Player.black, Point(row + 1, col + 1))

            return GameState(board, Player.white, None, None, sgf.get_komi())
        else:
            return GameState.new_game(sgf.get_size(), sgf.get_komi())

    @staticmethod
    def _consolidate_data(data_files):
        features_per_chunk = []
        labels_per_chunk = []

        for filename, positions in data_files:
            data = np.load(filename)

            features_per_chunk.append(data['features'])
            labels_per_chunk.append(data['labels'])

        features = np.concatenate(features_per_chunk, axis=0)
        labels = np.concatenate(labels_per_chunk, axis=0)

        return features, labels
