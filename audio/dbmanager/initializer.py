from audio.services.preprocessor import *
from audio.dbmanager.youtube_handler import *
from audio.dbmanager.dropper import *
from audio.utils.reader import *
# import django
# django.setup()
from audio.models import *

"""
Initialize media volume and database
"""


class Initializer:
    aud_ids = []

    @staticmethod
    def initialize(start_idx=0, end_idx=-1, _in_csv=LCSV_INPUT, _out_csv=LCSV_OUT):
        """
        :param _in_csv: csv which contains both audio and dance mapping information
        :param _out_csv: csv which will be added audio information [CI]
        :return:
        """
        if end_idx == -1:
            end_idx = len(CsvReader().read(_in_csv, **{'col1': 'audio_info'})['audio_info'])
        print(start_idx, end_idx)
        with open(_in_csv, 'r') as csv_input:
            with open(_out_csv, 'w') as csv_output:
                writer = csv.writer(csv_output, lineterminator='\n')
                for idx, row in enumerate(csv.reader(csv_input)):
                    try:
                        if start_idx <= idx <= end_idx:
                            if idx == 0:
                                writer.writerow(row + ["audio_id"])
                            else:
                                aud_met =[_id, _title, _dur] = list(write_from_meta(row[6]))
                                AudioPreprocessor(*aud_met, bpm=float(row[8])).preprocess()
                                writer.writerow(row + [_id])
                        else:
                            writer.writerow(row)
                    except Exception as e:
                        print(idx, row[6], e)
                        pass
                        # sys.exit(1)

    @staticmethod
    def remove_unsliced():
        for i in os.listdir(LF_WAV):
            audio_id = i.split(".")[0]
            if audio_id not in os.listdir(LF_SLICE):
                # Audio.objects.filter(audio_id=audio_id).delete()
                # os.remove("/home/jihee/choleor_media/audio/WAV/" + i)
                Dropper.drop(audio_id)


# if __name__ == '__main__':
#     Initializer.initialize()

    # a = CsvReader().read("/home/jihee/choleor_media/csv/output.csv", col1="audio_id")['audio_id']
    # print(len(a))
    # print(len(set(a)))