from audio.services.preprocessor import *
from audio.dbmanager.youtube_handler import *
from audio.utils.reader import *
import django

django.setup()
from audio.models import *

"""
Initialize media volume and database
"""


class Initializer:
    aud_ids = []

    @staticmethod
    def initialize(file=TEST_CSV):
        for _aud_info in CsvReader().read(file, **{'col1': 'audio_info'})['audio_info']:
            try:
                _aud_meta = list(write_from_meta(_aud_info))
                Initializer.aud_ids += _aud_meta[0]
                Audio.save(Audio(audio_id=_aud_meta[0], title=_aud_meta[1],
                                 download_url="http://www.youtube.com/watch?v=" + _aud_meta[0], duration=_aud_meta[2]))
                preproc = AudioPreprocessor(*_aud_meta)
                preproc.preprocess()
                _slice_duration = preproc.get_bar_duration()
                print(_aud_meta[0])
                for i in range(len(_slice_duration)):
                    AudioSlice(*(_aud_meta[0] + "ㅡ" + str(i), _slice_duration[i]), preproc.beat_track[i],
                               _aud_meta[0]).save()
            except:
                pass

    @staticmethod
    def add_audio_id_col(in_file="/home/jihee/choleor_media/input.csv",
                         out_file="/home/jihee/choleor_media/output.csv"):
        with open(in_file, 'r') as csvinput:
            with open(out_file, 'w') as csvoutput:
                writer = csv.writer(csvoutput, lineterminator='\n')
                for idx, row in enumerate(csv.reader(csvinput)):
                    try:
                        if row[0] == "choreo_vid":
                            writer.writerow(row + ["audio_id"])
                        else:
                            writer.writerow(row + [search_url_from_meta(row[6]).split("=")[1]])
                            print(search_url_from_meta(row[6]).split("=")[1])
                    except:
                        sys.exit(1)


if __name__ == '__main__':
    # Initializer.initialize()
    Initializer.add_audio_id_col()
    res = []
    # for i in os.listdir("/home/jihee/choleor_media/audio/WAV/"):
    #     if i.split(".")[0] not in os.listdir("/home/jihee/choleor_media/audio/SLICE/".format(i)):
    #         os.remove("/home/jihee/choleor_media/audio/WAV/" + i)
