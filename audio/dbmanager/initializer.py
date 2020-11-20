from audio.dbmanager.preprocessor import *
from audio.dbmanager.youtube_handler import *
from audio.utils.reader import *
from configuration.config import *
from audio.dbmanager.preprocessor import *
import django

django.setup()
from audio.models import *
from django.conf import settings

"""
Initialize media volume and database
"""


class Initializer:
    @staticmethod
    def initialize(file=TEST_CSV):
        for _aud_info in CsvReader().read(file, **{'col1': 'audio_info'})['audio_info']:
            _aud_meta = list(write_from_meta(_aud_info))
            Audio(*(_aud_meta + ["https://www.youtube.com/watch?v=" + _aud_meta[0]])).save()
            preproc = AudioPreprocessor(*_aud_meta)
            preproc.preprocess()
            _slice_duration = preproc.get_bar_duration()
            print(type(_aud_meta[0]))
            for i in range(len(_slice_duration)):
                AudioSlice(*(_aud_meta[0] + "ㅡ" + str(i), _slice_duration[i]), preproc.beat_track[i],
                           _aud_meta[0]).save()


if __name__ == '__main__':
    Initializer().initialize()
