from __future__ import absolute_import, unicode_literals

from audio.dbmanager.dropper import *
from audio.models import *
from pydub import AudioSegment
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter
from audio.utils import utils as ut
from audio.utils.optimization import single_process_to_multi_process
from configuration.config import *


class AudioPreprocessor:
    def __init__(self, audio_id, audio_title, duration):
        self._audio_id, self._title, self._duration = audio_id, audio_title, duration
        self.beat_track = None
        self._audio_slice_duration = None

    def get_slice_id(self, start_sec):  # 나중에 없애기
        return self._audio_id + "ㅡ" + str(self.beat_track.index(start_sec))

    def track_beat(self):
        print(self._audio_id)  # TODO idx 0으로 변환
        self.beat_track = []
        init_beat_arr = enumerate(
                ut.get_console_output('aubio beat "{}/{}.wav"'.format(LF_WAV, self._audio_id)).splitlines())
        # for idx, val in enumerate(init_beat_arr):
        #     if idx % 8 == 2:
        #         self.beat_track.append(float(val.strip("\t")))

        self.beat_track = [float(val.strip("\t"))-0.07 for idx, val in
                           enumerate(ut.get_console_output(
                               'aubio beat "{}/{}.wav"'.format(LF_WAV, self._audio_id)).splitlines())
                           if idx % 8 == 7]
        return self.beat_track

    def get_bar_duration(self):
        if self.beat_track is None:
            raise Exception("Did not initialize the beat track information")
        return [self.beat_track[i] - self.beat_track[i - 1] for i in range(1, len(self.beat_track))]

    def slice_by_beat(self, start=0, end=None):
        _end = end if not None else self._duration
        ms__beat_track = [1000 * i for i in self.beat_track]
        audio_source = AudioSegment.from_wav(LF_WAV + self._audio_id + ".wav")

        if not os.path.isdir(LF_SLICE + self._audio_id):
            os.mkdir(LF_SLICE + self._audio_id)

        for i in range(0, len(ms__beat_track) - 1):
            audio_slice_id = self._audio_id + "ㅡ" + str(i)
            if os.path.isfile("{}{}/{}.wav".format(LF_SLICE, self._audio_id, audio_slice_id)):
                continue
            audio_source[ms__beat_track[i]:ms__beat_track[i + 1]].export(
                "{}{}/{}.wav".format(LF_SLICE, self._audio_id, audio_slice_id), format("wav"))
            # self.change_bar_speed(audio_slice_id)

    def change_bar_speed(self, audio_slice_id, target_bpm=120.0):
        if not os.path.isdir(LF_CH_BPM + self._audio_id):
            try:
                os.mkdir(LF_CH_BPM + self._audio_id)
            except FileExistsError:
                pass
        else:
            if os.path.isfile(LF_CH_BPM + self._audio_id + "/" + audio_slice_id + ".wav"):
                return 0

        bar_bpm = 60.00 / (
                (self.beat_track[int(audio_slice_id.split("ㅡ")[1]) + 1] - self.beat_track[
                    int(audio_slice_id.split("ㅡ")[1])]) / 8)
        with WavReader("{}{}/{}.wav".format(LF_SLICE, self._audio_id, audio_slice_id)) as r:
            with WavWriter("{}{}/{}.wav".format(LF_CH_BPM, self._audio_id, audio_slice_id),
                           r.channels, r.samplerate) as w:
                phasevocoder(r.channels, speed=target_bpm / bar_bpm).run(r, w)

        print("only came " + audio_slice_id)

    def insert_on_db(self, idx_n):
        if not Audio.objects.filter(audio_id=self._audio_id).exists():
            Audio.save(Audio(audio_id=self._audio_id, title=self._title, duration=self._duration,
                             download_url="https://www.youtube.com/watch?v=" + self._audio_id))
        AudioSlice.save(
            AudioSlice(audio_slice_id=self._audio_id + "ㅡ" + str(idx_n),
                       duration=self.beat_track[idx_n + 1] - self.beat_track[idx_n],
                       start_sec=self.beat_track[idx_n], audio_id_id=self._audio_id))

    def preprocess(self):
        self.track_beat()
        self.slice_by_beat()

        # change_bar_speed를 for문으로 묶어주는 로컬함수 -> w
        # within_iteration
        def __change_bars_speed(x, y):
            for i in range(x, y):
                self.change_bar_speed(audio_slice_id=self._audio_id + "ㅡ" + str(i))

        single_process_to_multi_process(len(self.beat_track), 4, __change_bars_speed)

        for i in range(len(self.beat_track) - 1):
            self.change_bar_speed(audio_slice_id=self._audio_id + "ㅡ" + str(i))

        if not Audio.objects.filter(audio_id=self._audio_id).exists():
            Audio.save(Audio(audio_id=self._audio_id, title=self._title, duration=self._duration,
                             download_url="https://www.youtube.com/watch?v=" + self._audio_id))
        for i in range(len(self.beat_track) - 1):
            self.insert_on_db(i)
            # print("insert" + str(i))
        return self.beat_track


if __name__ == '__main__':
    # Dropper.drop("GNGbmg_pVlQ")
    # print((write_from_meta("Selena Gomez - Back to You (Lyrics)")))
    aud_proc = AudioPreprocessor('GNGbmg_pVlQ', 'Selena Gomez - Back to You (Lyrics)', 208).preprocess()
    print(aud_proc)
