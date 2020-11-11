from audio.services.preprocessor import *
from audio.services.youtube_handler import *
from audio.utils.reader import *

"""
Database를 initialize하고자 할 때
Initializer가 yotube-dl에서 title 정보를 통해 오디오 링크를 가져온다!

"""


class Initializer:
    csv_reader = CsvReader(test_path + "test.csv")
    __list = []
    #aud = None

    def __init__(self):
        self.audio_info_ldict = {}

    def audio_info_from_csv(self):
        self.audio_info_ldict = Initializer.csv_reader.read(**{'col1': 'audio_info'})
        print(self.audio_info_ldict)

    def download_from_audio_info(self):
        for _dict in self.audio_info_ldict:
            Initializer.__list += list(write_from_meta(_dict['audio_info']))

    def preprocess_with_delegation(self):
        for _dict in self.audio_info_ldict:
            aud = Audio(audio_id="", title=_dict['audio_info'], duration=get_video_duration())
            AudioPreprocessor.preprocess(aud)

    def initialize(self):
        self.audio_info_from_csv()
        self.download_from_audio_info()
        self.preprocess_with_delegation()


if __name__ == '__main__':

    result = CsvReader(test_path + "test.csv").read(
        **{'col1': 'choreo_vid', 'col2': 'choreo_url', 'col3': 'start', 'col4': 'end'})
    print(result)
    print(dsutils.listdict_to_dictlist(result))
