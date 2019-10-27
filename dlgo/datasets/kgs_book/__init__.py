import glob
import gzip
import os
import shutil
import tarfile

import numpy as np
from sgfmill.sgf import Sgf_game

from dlgo.boards.fast import FastBoard, FastGameState
from dlgo.datasets.base import DataSet
from dlgo.datasets.kgs_book.generator import KGSDataGenerator
from dlgo.datasets.kgs_book.index import KGSIndex
from dlgo.datasets.kgs_book.sampling import Sampler
from dlgo.encoders.basic import OnePlaneEncoder
from dlgo.gotypes import Point, Move, Player


class KGSDataSet(DataSet):
    def __init__(self, encoder=OnePlaneEncoder(19, 19), data_directory='.cache/datasets/kgs'):
        self.encoder = encoder
        self.data_dir = data_directory

    def load_data(self, data_type, samples, use_generator=False):
        kgs = KGSIndex(data_directory=self.data_dir)
        kgs.download_files()

        sampler = Sampler(data_dir=self.data_dir)
        sample_data = sampler.draw_data(data_type, samples)

        archives = set()
        samples_by_archive = {}

        for filename, sample in sample_data:
            archives.add(filename)
            if filename not in samples_by_archive:
                samples_by_archive[filename] = []
            samples_by_archive[filename].append(sample)

        for archive in archives:
            base_name = archive.replace('.tar.gz', '')
            data_file = base_name + data_type
            if not os.path.isfile(os.path.join(self.data_dir, data_file)):
                self._process_zip(archive, data_file, samples_by_archive[archive])

        return (KGSDataGenerator(self.data_dir, data_type, sample_data) if use_generator
                else self._consolidate_chunks(data_type, sample_data))

    def _unzip_data(self, archive):
        archive_path = os.path.join(self.data_dir, archive)
        decompressed_archive = archive_path[:-3]

        with gzip.open(archive_path) as gz:
            with open(decompressed_archive, 'wb') as tar:
                shutil.copyfileobj(gz, tar)

        return decompressed_archive

    def _process_zip(self, archive, data_file, samples):
        decompressed_archive = self._unzip_data(archive)
        tar = tarfile.open(decompressed_archive)
        game_files = tar.getnames()

        examples = self._count_moves(tar, samples, game_files)
        features = np.zeros((examples,) + self.encoder.board_shape)
        labels = np.zeros((examples,) + self.encoder.move_shape)

        counter = 0
        for sample in samples:
            game_file = game_files[sample + 1]

            if not game_file.endswith('.sgf'):
                raise ValueError(game_file + ' is not a valid sgf')

            sgf_content = tar.extractfile(game_file).read()
            sgf = Sgf_game.from_bytes(sgf_content)

            game, first_move_done = self._get_starting_position(sgf)

            for sgf_node in sgf.main_sequence_iter():
                color, point = sgf_node.get_move()

                if color is not None:
                    try:
                        assert game.next_player == (Player.black if color == 'b' else Player.white)

                        move = Move.play(Point(point[0] + 1, point[1] + 1)) if point is not None else Move.pass_turn()

                        if first_move_done and move.is_play:
                            features[counter] = self.encoder.encode_board(game)
                            labels[counter] = self.encoder.encode_move(move)
                            counter += 1

                        game = game.apply_move(move)
                    except AssertionError:
                        print('>>> Corrupted sgf: {} {}'.format(archive, game_file))
                        if first_move_done and point is not None:
                            counter += 1

                    first_move_done = True

        feature_file = os.path.join(self.data_dir, data_file + '_features_%d')
        label_file = os.path.join(self.data_dir, data_file + '_labels_%d')

        chunk = 0
        chunk_size = 1024
        while features.shape[0] >= chunk_size:
            current_features, features = features[:chunk_size], features[chunk_size:]
            current_labels, labels = labels[:chunk_size], labels[chunk_size:]

            np.save(feature_file % chunk, current_features)
            np.save(label_file % chunk, current_labels)

            chunk += 1

        # with open(os.path.join(self.data_dir, data_file), 'w') as file:
        #     file.write('generated {} chunks'.format(chunk))

    def _consolidate_chunks(self, data_type, sample_data):
        archives = set(file_name for file_name, sample in sample_data)

        data_files = []
        for archive in archives:
            data_file = archive.replace('.tar.gz', '') + data_type
            data_files.append(data_file)

        features_per_chunk = []
        labels_per_chunk = []
        for data_file in data_files:
            base_name = data_file.replace('.tar.gz', '')
            file_pattern = os.path.join(self.data_dir, base_name + '_features_*.npy')

            for feature_file in glob.glob(file_pattern):
                label_file = feature_file.replace('features', 'labels')

                chunk_features = np.load(feature_file)
                chunk_labels = np.load(label_file)

                features_per_chunk.append(chunk_features)
                labels_per_chunk.append(chunk_labels)

        features = np.concatenate(features_per_chunk, axis=0)
        labels = np.concatenate(labels_per_chunk, axis=0)

        # np.save(os.path.join(self.data_dir, 'features_{}.npy'.format(data_type)), features)
        # np.save(os.path.join(self.data_dir, 'labels_{}.npy'.format(data_type)), labels)

        return features, labels

    @staticmethod
    def _get_starting_position(sgf):
        if sgf.get_handicap() is not None and sgf.get_handicap() != 0:
            board = FastBoard(19, 19)

            for setup in sgf.get_root().get_setup_stones():
                for move in setup:
                    row, col = move
                    board.place_stone(Player.black, Point(row + 1, col + 1))

            return FastGameState(board, Player.white, None, None, sgf.get_komi()), True
        else:
            return FastGameState.new_game(19, sgf.get_komi()), False

    def _count_moves(self, archive, samples, game_files):
        total = 0

        for sample in samples:
            game_file = game_files[sample + 1]

            if game_file.endswith('.sgf'):
                sgf_content = archive.extractfile(game_file).read()
                sgf = Sgf_game.from_bytes(sgf_content)
                game, first_move_done = self._get_starting_position(sgf)

                moves = 0
                for node in sgf.main_sequence_iter():
                    color, move = node.get_move()
                    if color is not None:
                        if first_move_done:
                            moves += 1
                        first_move_done = True
                total += moves
            else:
                raise ValueError(game_file + ' is not a valid sgf')

        return total
