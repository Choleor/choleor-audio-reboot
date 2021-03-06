from __future__ import absolute_import, unicode_literals

from audio.models import *
from pydub import AudioSegment
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
        self.beat_track = None
        self.raw_tracked = None
        self.point_idx = None
        self.remainder = 0
        self._audio_slice_duration = None

    def dynamic_track(self):
        self.remainder = 0
        self.raw_tracked = [0.00] + [float(val.strip("\t")) for idx, val in enumerate(ut.get_console_output(
            'aubio beat "{}{}.wav"'.format(LF_WAV, self._audio_id)).splitlines())]
        # [0.00, 0.014, 1.41, 2.56, 3.67, 5.41, 7.13, 8.1, 9.23]
        self.remainder = AudioPreprocessor.get_nearest_elements(self.raw_tracked, self.usr_ssec)[1] % 8
        self.point_idx = [i for i in range(len(self.raw_tracked)) if i % 8 == self.remainder]
        if self.point_idx[0] != 0:
            self.point_idx = [0] + self.point_idx

        self.beat_track = [self.raw_tracked[x] for x in self.point_idx]
        self.beat_track.append(self._duration)

        self.usr_ssec, self.usr_sidx = AudioPreprocessor.get_nearest_elements(self.beat_track, self.usr_ssec)
        self.usr_eidx = AudioPreprocessor.get_nearest_elements(self.beat_track, self.usr_esec)[1] - 1
        self.usr_esec = self.beat_track[self.usr_eidx + 1]  # TODO changed

    @staticmethod
    def get_nearest_elements(_li, _input):
        return min(_li, key=lambda x: abs(x - _input)), _li.index(min(_li, key=lambda x: abs(x - _input)))

    def dynamic_slice(self, idx):
        wav_src = AudioSegment.from_wav(f"{LF_WAV}/{self._audio_id}.wav")
        slice_path = f"{LF_SLICE}{self.remainder}/{self._audio_id}/{self._audio_id}ㅡ{str(idx)}.wav"
        if not os.path.exists(slice_path):
            wav_src[1000 * self.beat_track[idx]:1000 * self.beat_track[idx + 1]].export(slice_path)

    def insert_to_audio(self):
        if self.bpm == 0.00:
            self.bpm = 60.00 / ((self.beat_track[int(len(self.beat_track) / 2) + 1] - self.beat_track[
                int(len(self.beat_track) / 2)]) / 8)
        aud = Audio.objects.filter(audio_id=self._audio_id)

        if bool(aud[0]) and aud[0].duration == 0.00:
            aud[0].duration = self._duration
            aud[0].bpm = self.bpm
        else:
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

        single_process_to_multi_process(len(self.beat_track) - 1, 4, _inner_beat_slice)

        self.insert_to_audio()
        self.insert_to_audio_slice()

        print("==============remainder=============")
        print(self.remainder)
        print()
        print("=============raw tracked============")
        print(self.raw_tracked)
        print("=============beat track=============")
        print(self.beat_track)
        print(len(self.beat_track))
        print()
        print("=============duration===============")
        print(self._duration)
        print("=============user's idx info ========")
        print(self.usr_sidx, self.usr_eidx)
        print("=============user's sec info==========")
        print(self.usr_ssec, self.usr_esec)
        return self.usr_sidx, self.usr_eidx
