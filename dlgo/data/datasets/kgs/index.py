import multiprocessing
import os
from collections import namedtuple
from urllib.request import urlopen, urlretrieve


def _download_archive(args):
    info, path = args

    print('>>> Downloading missing archive ' + info.filename)
    urlretrieve(info.url, path)


class ArchiveInfo(namedtuple('ArchiveInfo', 'url filename year games')):
    pass


class KGSIndex:
    def __init__(self, cache):
        self.url = 'http://u-go.net/gamerecords/'
        self.cache = cache
        self.index = os.path.join(cache, '_index')
        self.archive_info = []

        if not os.path.isdir(cache):
            os.makedirs(cache)

        self.load()

    def _load_index(self):
        if os.path.isfile(self.index):
            print('>>> Loading cached index page')
            with open(self.index, 'r') as index_file:
                content = index_file.read()
        else:
            print('>>> Downloading index page')
            with urlopen(self.url) as index_page:
                content = str(index_page.read())
                with open(self.index, 'w') as index_file:
                    index_file.write(content)
        return content

    def _download_archives(self):
        missing = []
        for info in self.archive_info:
            path = os.path.join(self.cache, info.filename)
            if not os.path.isfile(path):
                missing.append((info, path))

        with multiprocessing.Pool() as pool:
            pool.map(_download_archive, missing)

    def load(self):
        index_content = self._load_index()

        urls = [s.split('">Download')[0] for s in index_content.split('<a href="') if s.startswith("https://")]
        urls = [url for url in urls if url.endswith('.tar.gz')]

        for url in urls:
            filename = os.path.basename(url)

            _, date, board_size, games, _ = filename.split('-')
            year = int(date.split('_')[0])
            games = int(games)

            print('>>> Loading archive ' + filename)
            self.archive_info.append(ArchiveInfo(url, filename, year, games))

        self._download_archives()
