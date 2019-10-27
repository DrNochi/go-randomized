import gzip
import os
import shutil
import tarfile
import uuid

import numpy as np
from sgfmill.sgf import Sgf_game

from dlgo.boards.fast import FastBoard, FastGameState
from dlgo.datasets.base import DataSet
from dlgo.datasets.kgs.generator import KGSDataGenerator
from dlgo.datasets.kgs.index import KGSIndex
from dlgo.datasets.kgs.sampling import Sampler
from dlgo.encoders.basic import OnePlaneEncoder
from dlgo.gotypes import Point, Move, Player


class KGSDataSet(DataSet):
    def __init__(self, encoder=OnePlaneEncoder(19, 19), cache='.cache/datasets/kgs'):
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
                configs.write('{}|{}'.format(configuration, configuration_id))

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

        data_files = []
        for archive in archives:
            data_files += self._process_archive(archive, games_by_archive[archive])

        return (KGSDataGenerator(data_files) if use_generator
                else self._consolidate_data(data_files))

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
        base_filename = os.path.join(self.data_cache,
                                     os.path.basename(archive.name)[:-4],
                                     os.path.basename(game_file)[:-4])
        features_file = base_filename + '_features.npy'
        labels_file = base_filename + '_labels.npy'
        if os.path.isfile(features_file) and os.path.isfile(labels_file):
            return base_filename

        assert game_file.endswith('sgf')

        positions = self._count_moves(archive, game_file)
        features = np.zeros((positions,) + self.encoder.board_shape)
        labels = np.zeros((positions,) + self.encoder.move_shape)

        sgf_content = archive.extractfile(game_file).read()
        sgf = Sgf_game.from_bytes(sgf_content)

        game = self._get_starting_position(sgf)

        counter = 0
        for node in sgf.main_sequence_iter():
            color, point = node.get_move()

            if color is not None:
                try:
                    assert game.next_player == (Player.black if color == 'b' else Player.white)

                    move = Move.play(Point(point[0] + 1, point[1] + 1)) if point is not None else Move.pass_turn()

                    if move.is_play or self.encoder.can_encode_pass:
                        features[counter] = self.encoder.encode_board(game)
                        labels[counter] = self.encoder.encode_move(move)
                        counter += 1

                    game = game.apply_move(move)
                except AssertionError:
                    print('>>> Corrupted sgf: {} {}'.format(archive, game_file))

        np.save(features_file, features)
        np.save(labels_file, labels)

        return base_filename

    def _count_moves(self, archive, game_file):
        if not game_file.endswith('.sgf'):
            raise ValueError(game_file + ' is not a valid sgf')

        sgf_content = archive.extractfile(game_file).read()
        sgf = Sgf_game.from_bytes(sgf_content)

        moves = 0
        for node in sgf.main_sequence_iter():
            color, point = node.get_move()
            if color is not None and (point is not None or self.encoder.can_encode_pass):
                moves += 1

        return moves

    @staticmethod
    def _get_starting_position(sgf):
        if sgf.get_handicap() is not None and sgf.get_handicap() != 0:
            board = FastBoard(sgf.get_size(), sgf.get_size())

            for setup in sgf.get_root().get_setup_stones():
                for point in setup:
                    row, col = point
                    board.place_stone(Player.black, Point(row + 1, col + 1))

            return FastGameState(board, Player.white, None, None, sgf.get_komi())
        else:
            return FastGameState.new_game(sgf.get_size(), sgf.get_komi())

    @staticmethod
    def _consolidate_data(data_files):
        features_per_chunk = []
        labels_per_chunk = []

        for base_filename in data_files:
            features_file = base_filename + '_features.npy'
            labels_file = base_filename + '_labels.npy'

            features_per_chunk.append(np.load(features_file))
            labels_per_chunk.append((np.load(labels_file)))

        features = np.concatenate(features_per_chunk, axis=0)
        labels = np.concatenate(labels_per_chunk, axis=0)

        return features, labels
