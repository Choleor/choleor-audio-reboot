from __future__ import absolute_import, unicode_literals
from celery import task

import os
from pydub import AudioSegment
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter
import config as c
import utils.utils as ut
import asyncio
from threading import Thread
from multiprocessing import Process
from utils.optimization import single_process_to_multi_process
from utils.utils import within_iteration as it
from celery import Celery
from celery.decorators import task


# audio 객체에 대한 has-a relationship으로 AudioHandler class에서 제어하는 게 맞나?
# 아니면 Audio 객체의 프로퍼티 메소드로 두는것이 나을까?

class AudioHandler:
    def __init__(self, audio, beat_track=None):
        self._audio = audio
        self._audio_id = audio.audio_id
        self._audio_duration = audio.duration

        self.beat_track = beat_track  # beat_track과 audio_slice_id는 1:1 대응됨
        self._audio_slice_duration = None

    def get_slice_id(self, start_sec):  # 나중에 없애기
        return self._audio_id + "_" + str(self.beat_track.index(start_sec))

    def track_beat(self):
        self.beat_track = [float(val.strip("\t")) for idx, val in
                           enumerate(ut.get_console_output('aubio beat "{}.wav"'.format(self._audio_id)).splitlines())
                           if idx % 8 == 0]
        return self.beat_track

    def get_bar_duration(self):
        if self.beat_track is None:
            raise Exception("Did not initialize the beat track information")
        return [self.beat_track[i] - self.beat_track[i - 1] for i in range(1, len(self.beat_track) - 1)]

    def slice_by_beat(self, start=0, end=None):
        _end = end if not None else self._audio_duration
        ms_beat_track = [1000 * i for i in self.beat_track]
        audio_source = AudioSegment.from_wav(c.LF_WAV + self._audio_id + ".wav")

        if not os.path.isdir(c.LF_SLICE + self._audio_id):
            os.mkdir(c.LF_SLICE + self._audio_id)

        for i in range(0, len(ms_beat_track) - 1):
            audio_slice_id = self._audio_id + "_" + str(i)
            if os.path.isfile("{}{}/{}.wav".format(c.LF_SLICE, self._audio_id, audio_slice_id)):
                continue
            audio_source[ms_beat_track[i]:ms_beat_track[i + 1]].export(
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
                (self.beat_track[int(audio_slice_id.split("_")[1]) + 1] - self.beat_track[
                    int(audio_slice_id.split("_")[1])]) / 8)
        with WavReader("{}{}/{}.wav".format(c.LF_SLICE, self._audio_id, audio_slice_id)) as r:
            with WavWriter("{}{}/{}.wav".format(c.LF_CH_BPM, self._audio_id, audio_slice_id),
                           r.channels, r.samplerate) as w:
                phasevocoder(r.channels, speed=target_bpm / bar_bpm).run(r, w)
        print("only came " + audio_slice_id)

    @task(name="Preprocess, beat track, change bpm")
    def preprocess(self):
        # self.track_beat()
        self.slice_by_beat()

        # change_bar_speed를 for문으로 묶어주는 로컬함수 -> within_iteration
        def __change_bars_speed(x, y):
            for i in range(x, y):
                self.change_bar_speed(audio_slice_id=self._audio_id + "_" + str(i))

        single_process_to_multi_process(len(self.beat_track), 4, __change_bars_speed)


# TODO Audio Model 객체로 바꾸기
class Audio:
    def __init__(self, audio_id, title, duration):
        self.audio_id = audio_id
        self.title = title
        self.duration = duration


if __name__ == '__main__':
    aud = Audio(audio_id="QpeGKsi2Jac", title="Ariana Grande - NASA (Lyrics)", duration=179)
    beat_track = [2.830125, 6.708229, 10.701583, 14.416125, 18.125167, 22.281562, 27.238146, 32.054875,
                  36.679187, 41.327458, 46.265792, 50.519458, 53.672438, 56.84975, 60.045375,
                  62.895229, 66.076375, 69.266479, 72.458354, 75.653646, 78.791104, 82.061896,
                  85.263646, 88.270104, 91.466271, 94.847542, 98.039354, 101.272813, 105.069729,
                  109.695, 114.439021, 117.681187, 120.867729, 124.084896, 127.250292, 130.441438,
                  133.632125, 136.875958, 140.085917, 143.234333, 146.652562, 149.893, 153.277479,
                  156.47725, 159.661292, 162.831583, 166.047958, 169.122813, 172.187479, 175.305667,
                  178.484438]
    handler = AudioHandler(aud, beat_track=beat_track)
    print(AudioHandler(aud, beat_track=beat_track).get_bar_duration())
    handler.slice_by_beat()
    handler.preprocess()
