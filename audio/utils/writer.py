from abc import *
import os

from utils.reader import *
import config as c


class AlreadyExistsError(Exception):  # Exception을 상속받아서 새로운 예외를 만듦
    def __init__(self):
        super().__init__("Download failure. There's already downloaded source.")


class Writer(metaclass=abc.ABCMeta):
    def __init__(self, file):
        self._file = file

    @abc.abstractmethod
    def write(self, **kwargs):
        raise NotImplementedError()


class TxtWriter(Writer):
    def write(self, **kwargs):
        try:
            __list__ = [str(i) + "\n" for i in kwargs['list']]
            print(__list__)
            with open(self._file, mode='w', encoding='utf-8') as f:
                f.writelines(__list__)
            return 0
        except IOError:
            sys.stderr.write("No such text file: %s\n" % self._file)
            return 1


class CsvWriter(Writer):
    def write(self, keys, out=None, **kwargs):
        __dict__ = kwargs['dict']  # content  colname : [ctx1, ctx2, ctx3, ...]
        __keys__ = list(__dict__.keys())
        __vals__ = [__dict__[k] for k in __keys__]

        with open(self._file, 'w', encoding="utf-8") as wf:
            csv.DictWriter(wf, keys)

    def append_new_column(self, out=None, **kwargs):
        if not bool(out):
            out = self._file

        __dict__ = kwargs['dict']
        (__keys__, __vals__) = (list(__dict__.keys()), list(__dict__.values()))

        try:
            arr = [{k: __dict__[k][i] for k in __keys__} for i in range(len(__vals__[0]))]
            print(arr)
            with open(self._file, 'r', encoding="utf-8") as rf, open(out, 'w', encoding="utf-8") as wf:
                dict_reader = csv.DictReader(rf, delimiter='\t')
                # 원하는 column 추가
                org_fieldnames = dict_reader.fieldnames[0]
                new_fieldnames = org_fieldnames + "," + ",".join(__keys__)

                writer_csv = csv.DictWriter(wf, list(new_fieldnames.split(",")), delimiter=',', lineterminator='\n')
                writer_csv.writeheader()

                i = 0
                for existed in dict_reader:
                    rdict = {field: item for (field, item) in
                             zip(org_fieldnames.split(","), existed[org_fieldnames].split(","))}
                    rdict.update(arr[i]) if i < len(arr) else rdict
                    writer_csv.writerow(rdict)
                    print(rdict)
                    i += 1
            return 0
        except FileNotFoundError:
            sys.stderr.write("No such text file: %s\n" % self._file)
            return 1


class MusicWriter(Writer):
    def write(self, song, _format="wav", out=e.LP_TEST + e.LF_WAV):
        try:
            store_cmd = r'cd {path} && youtube-dl --download-archive archive.txt --verbose -x --audio-format {format} -w -o "{vid}.%(ext)s" "{url}"'.format(
                path=out, vid=song[0], format=_format, url='https://www.youtube.com/watch?v=' + song[0])
            os.system(store_cmd)

        except IndexError:
            print("Usage: python " + sys.argv[0] + " linkOfVideo")
            exit()

    # return get_console_output(
    #     "youtube-dl --download-archive archive.txt --verbose -x -o {}/%(id)s.%(ext) '{}'".format(
    #         out_path,
    #         download_url), r=False, w=True)


test_path = "C:/Users/Jihee/PycharmProjects/choleor/audio/testfile/"

if __name__ == '__main__':
    vid = ["rpLITtLRltw", "RQTgJRwMdKQ", "3pHYxx9dY_U", "jWhyc6UQ9ss", "jSrxXduIz1U"]
    url = ["https://www.youtube.com/watch?v=rpLITtLRltw", "https://www.youtube.com/watch?v=RQTgJRwMdKQ",
           "https://www.youtube.com/watch?v=3pHYxx9dY_U", "https://www.youtube.com/watch?v=jWhyc6UQ9ss",
           "https://www.youtube.com/watch?v=jSrxXduIz1U"]
    dd = {"choreo_vid": vid, "choreo_url": url}
    CsvWriter(test_path + "/ch_ReadTest.csv").append_new_column(out=test_path + "ch_WriteTest.csv", **{'dict': dd})

if __name__ == '__main__':
    r = CsvReader(test_path + "test.csv").read(
        **{'col1': 'choreo_vid', 'col2': 'choreo_url', 'col3': 'start', 'col4': 'end'})
    a = [[vid, url, float(start), float(end)] for (vid, url, start, end) in
         zip(r['choreo_vid'], r['choreo_url'], r['start'], r['end'])]
    print(a)

    os.chdir(c.LF_WAV)
    res = glob('*.{}'.format('wav'))
    print(res)
