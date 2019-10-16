import multiprocessing
import os
import sys

from dlgo.datasets.kgs import KGSDataSet, KGSIndex, Sampler, KGSDataGenerator


class ParallelKGSDataSet(KGSDataSet):
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

        self._invoke_workers(data_type, archives, samples_by_archive)

        return (KGSDataGenerator(self.data_dir, data_type, sample_data) if use_generator
                else self._consolidate_chunks(data_type, sample_data))

    def _invoke_workers(self, data_type, archives, samples_by_archive):
        worker_arguments = [(self, archive, data_type, samples_by_archive[archive]) for archive in archives]

        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        try:
            it = pool.imap(self._worker, worker_arguments)
            for _ in it:
                pass
            pool.close()
            pool.join()
        except KeyboardInterrupt:
            print(">>> Caught KeyboardInterrupt, terminating workers")
            pool.terminate()
            pool.join()
            sys.exit(-1)

    @staticmethod
    def _worker(worker_arguments):
        self, archive, data_type, samples = worker_arguments
        try:
            base_name = archive.replace('.tar.gz', '')
            data_file = base_name + data_type
            if not os.path.isfile(os.path.join(self.data_dir, data_file)):
                self._process_zip(archive, data_file, samples)
        except (KeyboardInterrupt, SystemExit):
            print('>>> Exiting child process')
