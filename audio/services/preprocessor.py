from __future__ import absolute_import, unicode_literals

import os
from pydub import AudioSegment
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter
from configuration import config as c
from audio.utils import utils as ut
from audio.utils.optimization import single_process_to_multi_process
# from celery.decorators import task
from celery.task import task
from configuration.config import *


class AudioPreprocessor:
    def __init__(self, *args):
        self._audio_id, self._audio_title, self._audio_duration = args
        self._beat_track = None
        self._audio_slice_duration = None

    def get_slice_id(self, start_sec):  # 나중에 없애기
        return self._audio_id + "_" + str(self._beat_track.index(start_sec))

    def track_beat(self):
        self._beat_track = [float(val.strip("\t")) for idx, val in
                            enumerate(ut.get_console_output(
                                'aubio beat "{}/{}.wav"'.format(LF_WAV, self._audio_id)).splitlines())
                            if idx % 8 == 0]
        return self._beat_track

    def get_bar_duration(self):
        if self._beat_track is None:
            raise Exception("Did not initialize the beat track information")
        return [self._beat_track[i] - self._beat_track[i - 1] for i in range(1, len(self._beat_track))]

    def slice_by_beat(self, start=0, end=None):
        _end = end if not None else self._audio_duration
        ms__beat_track = [1000 * i for i in self._beat_track]
        audio_source = AudioSegment.from_wav(c.LF_WAV + self._audio_id + ".wav")

        if not os.path.isdir(c.LF_SLICE + self._audio_id):
            os.mkdir(c.LF_SLICE + self._audio_id)

        for i in range(0, len(ms__beat_track) - 1):
            audio_slice_id = self._audio_id + "_" + str(i)
            if os.path.isfile("{}{}/{}.wav".format(c.LF_SLICE, self._audio_id, audio_slice_id)):
                continue
            audio_source[ms__beat_track[i]:ms__beat_track[i + 1]].export(
                "{}{}/{}.wav".format(c.LF_SLICE, self._audio_id, audio_slice_id), format("wav"))
            # self.change_bar_speed(audio_slice_id)

    def change_bar_speed(self, audio_slice_id, target_bpm=120.0):
        if not os.path.isdir(c.LF_CH_BPM + self._audio_id):
            try:
                os.mkdir(c.LF_CH_BPM + self._audio_id)
            except FileExistsError:
                pass
        else:
            if os.path.isfile(c.LF_CH_BPM + self._audio_id + "/" + audio_slice_id + ".wav"):
                return 0

        bar_bpm = 60.00 / (
                (self._beat_track[int(audio_slice_id.split("_")[1]) + 1] - self._beat_track[
                    int(audio_slice_id.split("_")[1])]) / 8)
        with WavReader("{}{}/{}.wav".format(c.LF_SLICE, self._audio_id, audio_slice_id)) as r:
            with WavWriter("{}{}/{}.wav".format(c.LF_CH_BPM, self._audio_id, audio_slice_id),
                           r.channels, r.samplerate) as w:
                phasevocoder(r.channels, speed=target_bpm / bar_bpm).run(r, w)
        print("only came " + audio_slice_id)

    # @task(name='preprocess')
    def preprocess(self):
        self.track_beat()
        self.slice_by_beat()

        # change_bar_speed를 for문으로 묶어주는 로컬함수 -> within_iteration
        def __change_bars_speed(x, y):
            for i in range(x, y):
                self.change_bar_speed(audio_slice_id=self._audio_id + "_" + str(i))

        single_process_to_multi_process(len(self._beat_track), 4, __change_bars_speed)
