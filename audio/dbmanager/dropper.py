from audio.dbmanager.initializer import *
from audio.utils.writer import TxtWriter
from audio.utils.reader import TxtReader
from audio.models import Audio, AudioSlice
import glob, os


class Dropper:
    @staticmethod
    def drop(audio_id):
        # remove volume data
        if os.path.exists(LF_WAV + audio_id + ".wav"):
            os.remove(LF_WAV + audio_id + ".wav")

        for folder_path in [LF_SLICE, LF_CH_BPM]:
            for file_path in glob.glob('{}{}/{}ㅡ*.wav'.format(folder_path, audio_id, audio_id)):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print("Error while deleting file : ", file_path, e)
            if os.path.exists(folder_path + audio_id):
                os.rmdir(folder_path + audio_id)

        # delete data on Database(mysql)
        Audio.objects.filter(audio_id=audio_id).delete()
        AudioSlice.objects.filter(audio_id=audio_id).delete()

        # youtube-dl의 archive file reformat
        read = TxtReader().read(LP_MEDIA + "archive.txt")
        try:
            read.remove("youtube {}\n".format(audio_id))
        except:
            pass
        TxtWriter().write(LP_MEDIA + "archive.txt", read)
        # self.audio_meta_list.remove(audio_id)
        # print(self.audio_meta_list)

# if __name__ == '__main__':
#     Dropper().drop("h5jz8xdpR0M")
