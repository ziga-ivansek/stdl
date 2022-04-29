import re
from urllib.request import urlretrieve

from tqdm import tqdm


class TQDM_ProgressBar(tqdm):

    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download(url: str, path: str, progressbar: bool = False):
    succes = False
    try:
        if progressbar:
            with TQDM_ProgressBar(unit="B", unit_scale=True, unit_divisor=1024) as t:
                urlretrieve(url, path, reporthook=t.update_to, data=None)
            t.total = t.n

        else:
            urlretrieve(url, path)
        succes = True
    except Exception as e:
        print(e)
    finally:
        return succes
