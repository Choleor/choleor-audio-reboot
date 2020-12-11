from __future__ import absolute_import, unicode_literals

# from audio.dbmanager.dropper import *
from audio.models import *
from pydub import AudioSegment
# from audiotsm import phasevocoder
# from audiotsm.io.wav import WavReader, WavWriter
from audio.utils import utils as ut
from audio.utils.optimization import single_process_to_multi_process
from configuration.config import *
import pickle
from audio.dbmanager.redis_dao import UserRedisHandler, AmplitudeRedisHandler, SimilarityRedisHandler


class AudioPreprocessor:
    def __init__(self, audio_id, audio_title, duration, **kwargs):
        self._audio_id, self._title, self._duration = audio_id, audio_title, duration
        self.bpm = 0.00 if "bpm" not in kwargs else kwargs.get("bpm")
        self.usr_ssec = 0.00 if "user_start" not in kwargs else kwargs.get("user_start")
        self.usr_esec = -1.00 if "user_end" not in kwargs else kwargs.get("user_end")
        self.usr_sidx = None
        self.usr_eidx = None
        print(self.usr_esec)
        self.beat_track = None
        self.raw_tracked = None
        self.remainder = 0
        self._audio_slice_duration = None

    def dynamic_track(self):
        self.remainder = 0
        self.raw_tracked = [float(val.strip("\t")) - 0.07 for idx, val in enumerate(ut.get_console_output(
            'aubio beat "{}{}.wav"'.format(LF_WAV, self._audio_id)).splitlines())]
        self.usr_ssec, self.usr_sidx = AudioPreprocessor.get_nearest(self.raw_tracked, self.usr_ssec)
        self.remainder = self.usr_sidx % 8
        print(self.usr_ssec)
        print(self.usr_sidx)
        print(self.remainder)
        self.beat_track = [v for i, v in enumerate(self.raw_tracked) if i % 8 == self.remainder]

        self.usr_esec = AudioPreprocessor.get_nearest(self.beat_track, self.usr_esec)[0]
        print("esec" + str(self.usr_esec))
        self.usr_sidx = self.beat_track.index(self.usr_ssec)
        self.usr_eidx = self.beat_track.index(self.usr_esec)

    @staticmethod
    def get_nearest_idx(_li, _input):
        print(_input)
        for idx, val in enumerate(_li):
            if idx == 0:
                if _li[0] > _input:
                    print("here")
                    return 0, _li[0]
            elif _li[idx] - _input >= _input - _li[idx - 1] >= 0:
                print("Bb")
                return idx, _li[idx]

    @staticmethod
    def get_nearest(_li, _input):
        return min(_li, key=lambda x: abs(x - _input)), _li.index(min(_li, key=lambda x: abs(x - _input)))

    def dynamic_slice(self, idx):
        wav_src = AudioSegment.from_wav(f"{LF_WAV}/{self._audio_id}.wav")
        slice_path = f"{LF_SLICE}{self.remainder}/{self._audio_id}/{self._audio_id}ㅡ{str(idx)}.wav"
        if not os.path.exists(slice_path):
            wav_src[1000 * self.beat_track[idx]:1000 * self.beat_track[idx + 1]].export(slice_path)
        # print(f"[COMPLETED SLICING] {slice_path}")

        # for i in range(0, len(self.beat_track) - 2):
        #     if not os.path.exists(slice_path):
        #         wav_src[1000*self.beat_track[i]:1000*self.beat_track[i + 1]].export(slice_path)

    def insert_to_audio(self):
        if self.bpm == 0.00:
            self.bpm = 60.00 / ((self.beat_track[int(len(self.beat_track) / 2) + 1] - self.beat_track[
                int(len(self.beat_track) / 2)]) / 8)
        if not Audio.objects.filter(audio_id=self._audio_id).exists():
            aud = Audio(audio_id=self._audio_id, title=self._title,
                        download_url="http://www.youtube.com/watch?v=" + self._audio_id, duration=self._duration,
                        bpm=self.bpm)
            aud.save()

    def insert_to_audio_slice(self):
        for i in range(len(self.beat_track) - 2):
            AudioSlice(audio_slice_id=self._audio_id + "ㅡ" + str(i),
                       duration=self.beat_track[i + 1] - self.beat_track[i],
                       start_sec=self.beat_track[i], audio_id_id=self._audio_id).save()

    def preprocess(self):
        self.dynamic_track()
        f = f"{LF_SLICE}{self.remainder}/{self._audio_id}/"
        if not os.path.exists(f):
            os.mkdir(f)

        def _inner_beat_slice(x, y):
            for i in range(x, y):
                self.dynamic_slice(i)

        single_process_to_multi_process(len(self.beat_track) - 2, 4, _inner_beat_slice)
        self.insert_to_audio()
        self.insert_to_audio_slice()
        print(self.beat_track)
        print(self.usr_sidx, self.usr_eidx)
        print(self.usr_ssec, self.usr_esec)
        return self.usr_sidx, self.usr_eidx


if __name__ == '__main__':
    print(pickle.loads(AmplitudeRedisHandler.dao.get("0:HNN9Uh1NzOoㅡ4")))
    print(pickle.loads(SimilarityRedisHandler.dao.get("0:HNN9Uh1NzOoㅡ11")))
# if __name__ == '__main__':
#     # AudioPreprocessor('DKpfWL0THsg', 'ChungHa PLAY Lyrics (청하 플레이 가사) | Color Coded | Han/Rom/Eng sub',
#     #                   203).preprocess()
#     a = AudioPreprocessor.get_nearest([3.02, 3, 5.6, 5.12, 6.23, 7.56], 6)
#     print(a[0])
#     print(a[1])
