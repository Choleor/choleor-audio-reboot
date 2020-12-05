import abc
import sys
from audio.utils.reader import *
from audio.dbmanager.youtube_handler import search_url_from_meta
from configuration.config import *


class AlreadyExistsError(Exception):  # Exception을 상속받아서 새로운 예외를 만듦
    def __init__(self):
        super().__init__("Download failure. There's already downloaded source.")


class Writer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def write(self, **kwargs):
        raise NotImplementedError()


class TxtWriter(Writer):
    def write(self, file, *args):
        try:
            with open(file, mode='w', encoding='utf-8') as f:
                f.writelines(*args)
            return 0
        except IOError:
            sys.stderr.write("No such text file: %s\n" % file)
            return 1


class CsvWriter(Writer):
    def write(self, keys, file, out=None, **kwargs):
        __dict__ = kwargs['dict']  # content  colname : [ctx1, ctx2, ctx3, ...]
        __keys__ = list(__dict__.keys())
        __vals__ = [__dict__[k] for k in __keys__]

        with open(file, 'w', encoding="utf-8") as wf:
            csv.DictWriter(wf, keys)


if __name__ == '__main__':
    CsvWriter().write()

#
# test_path = "C:/Users/Jihee/PycharmProjects/choleor/audio/testfile/"
#
# if __name__ == '__main__':
#     vid = ["rpLITtLRltw", "RQTgJRwMdKQ", "3pHYxx9dY_U", "jWhyc6UQ9ss", "jSrxXduIz1U"]
#     url = ["https://www.youtube.com/watch?v=rpLITtLRltw", "https://www.youtube.com/watch?v=RQTgJRwMdKQ",
#            "https://www.youtube.com/watch?v=3pHYxx9dY_U", "https://www.youtube.com/watch?v=jWhyc6UQ9ss",
#            "https://www.youtube.com/watch?v=jSrxXduIz1U"]
#     dd = {"choreo_vid": vid, "choreo_url": url}
#     CsvWriter(test_path + "/ch_ReadTest.csv").append_new_column(out=test_path + "ch_WriteTest.csv", **{'dict': dd})
#
# if __name__ == '__main__':
#     r = CsvReader(test_path + "test.csv").read(
#         **{'col1': 'choreo_vid', 'col2': 'choreo_url', 'col3': 'start', 'col4': 'end'})
#     a = [[vid, url, float(start), float(end)] for (vid, url, start, end) in
#          zip(r['choreo_vid'], r['choreo_url'], r['start'], r['end'])]
#     print(a)
#
#     os.chdir(c.LF_WAV)
#     res = glob('*.{}'.format('wav'))
#     print(res)
