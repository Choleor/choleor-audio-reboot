from audio.dbmanager.preprocessor import *
from audio.dbmanager.youtube_handler import *
from audio.utils.reader import *
from audio.utils.writer import TxtWriter
import glob
from configuration.config import *

"""
media volume initializer
"""


class MediaHandler:
    csv_reader = CsvReader()
    audio_meta_list = []

    @staticmethod
    def media_initialize(file=test_path + "test.csv"):
        for _aud_info in MediaHandler.csv_reader.read(file, **{'col1': 'audio_info'})['audio_info']:
            MediaHandler.audio_meta_list.append(list(write_from_meta(_aud_info)))
        for meta_list in MediaHandler.audio_meta_list:
            AudioPreprocessor(*meta_list).preprocess()



    @staticmethod
    def drop(audio_id):
        # volume data 삭제
        if os.path.exists(LF_WAV + audio_id + ".wav"):
            os.remove(LF_WAV + audio_id + ".wav")

        for folder_path in [LF_SLICE, LF_CH_BPM]:
            for file_path in glob.glob(folder_path + '{}{}_*.wav'):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print("Error while deleting file : ", file_path, e)
                if os.path.exists(LF_SLICE + audio_id):
                    os.rmdir(LF_SLICE + audio_id)
        try:
            MediaHandler.audio_meta_list.remove(audio_id)
        except:
            pass
        # youtube-dl의 archive file reformat
        read = TxtReader().read(LP_MEDIA + "archive.txt")
        try:
            read.remove("youtube {}\n".format(audio_id))
        except:
            pass
        TxtWriter().write(LP_MEDIA + "archive.txt", read)
        # self.audio_meta_list.remove(audio_id)
        # print(self.audio_meta_list)


if __name__ == '__main__':
    MediaHandler().initialize()
    # Initializer().drop("h5jz8xdpR0M")
