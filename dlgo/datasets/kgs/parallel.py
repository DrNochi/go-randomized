import multiprocessing

from dlgo.datasets.kgs import KGSDataSet
from dlgo.datasets.kgs.generator import KGSDataGenerator


class ParallelKGSDataSet(KGSDataSet):
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

        return (KGSDataGenerator(data_files) if use_generator
                else self._consolidate_data(data_files))

    def _invoke_workers(self, archives, games_by_archive):
        args = [(self, archive, games_by_archive[archive]) for archive in archives]
        with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
            return [gf for al in pool.map(self._worker, args) for gf in al]

    @staticmethod
    def _worker(args):
        self, archive, games = args
        return self._process_archive(archive, games)
