import glob

from django.test import TestCase
from audio.services.preprocessor import *
from audio.services.youtube_handler import *


class PreprocessorTest(TestCase):
    preprocessor = None
    _beat_track_res = None
    _bar_duration_list = None

    def setUp(self) -> None:
        PreprocessorTest.preprocessor = AudioPreprocessor(*write_from_meta("Ariana Grande"))

    def test_track_beat(self):
        PreprocessorTest._beat_track_res = [2.990813, 6.310333, 9.825313, 13.138042, 16.491521, 19.816833, 23.151042,
                                            26.46975, 29.599542,
                                            32.728917, 36.07275, 39.403542, 42.740354, 46.045229, 49.416583, 53.379708,
                                            58.375354,
                                            63.384104, 68.384729, 73.387812, 77.752083, 81.058333, 84.190813, 87.751104,
                                            91.068229,
                                            94.389708, 97.9505, 101.076042, 104.415708, 107.762104, 111.102208,
                                            114.370625, 117.738062,
                                            121.067875, 124.389646, 128.036333, 131.511354, 134.816062, 138.142188,
                                            141.461563, 144.827771,
                                            148.154021, 151.476229, 154.804021, 157.938333, 161.058792, 164.411458,
                                            167.708854, 171.431563]
        self.assertEquals(PreprocessorTest._beat_track_res, PreprocessorTest.preprocessor.track_beat())

    def test_get_slice_id(self):
        if PreprocessorTest._beat_track_res is None:
            self.test_track_beat()
        PreprocessorTest.preprocessor._beat_track = PreprocessorTest._beat_track_res
        _executed_res = PreprocessorTest.preprocessor.get_slice_id(6.310333)
        self.assertEquals("Xsb9flAEymA_1", _executed_res)

    def test_get_bar_duration(self):
        _expected_res = [3.31952, 3.5149799999999995, 3.312729000000001, 3.3534789999999983, 3.3253120000000003,
                         3.3342090000000013, 3.318708000000001, 3.1297919999999984, 3.129375000000003,
                         3.3438329999999965, 3.3307920000000024, 3.336812000000002, 3.3048749999999956,
                         3.3713540000000037, 3.963124999999998, 4.995646000000001, 5.008749999999999, 5.000624999999992,
                         5.003083000000004, 4.364271000000002, 3.3062500000000057, 3.132480000000001,
                         3.5602909999999923, 3.3171250000000043, 3.3214789999999965, 3.5607920000000064,
                         3.125541999999996, 3.339665999999994, 3.3463959999999986, 3.340104000000011,
                         3.2684169999999995, 3.3674369999999954, 3.3298130000000015, 3.3217709999999983,
                         3.6466870000000142, 3.475020999999998, 3.3047079999999767, 3.3261260000000163,
                         3.319375000000008, 3.3662080000000003, 3.3262499999999875, 3.322207999999989,
                         3.3277920000000165, 3.134311999999994, 3.120459000000011, 3.3526659999999993,
                         3.297395999999992, 3.722709000000009]
        if PreprocessorTest._beat_track_res is None:
            self.test_track_beat()
        PreprocessorTest.preprocessor._beat_track = PreprocessorTest._beat_track_res
        PreprocessorTest.preprocessor._bar_duration_list = PreprocessorTest.preprocessor.get_bar_duration()
        self.assertEquals(_expected_res, PreprocessorTest.preprocessor._bar_duration_list)

    def test_slice_by_beat(self):
        if PreprocessorTest._beat_track_res is None:
            self.test_track_beat()  # beat tracking 정보를 초기화
        PreprocessorTest.preprocessor._beat_track = PreprocessorTest._beat_track_res
        PreprocessorTest.preprocessor.slice_by_beat()
        self.assertEquals(48, len(
            glob.glob(c.LF_SLICE + "Xsb9flAEymA/Xsb9flAEymA_*.wav")))  # slice마다의 품질을 확인할 길이 없으므로 잘라진 파일 개수로 비교

    def test_change_bar_speed(self):
        if PreprocessorTest._beat_track_res is None:
            self.test_track_beat()  # beat tracking 정보를 초기화
        PreprocessorTest.preprocessor._beat_track = PreprocessorTest._beat_track_res
        for i in range(0, len(PreprocessorTest._beat_track_res) - 1):
            PreprocessorTest.preprocessor.change_bar_speed("Xsb9flAEymA_" + str(i))
        self.assertEquals(48, len(glob.glob(c.LF_SLICE + "Xsb9flAEymA/Xsb9flAEymA_*.wav")))

    def test_preprocess(self):
        PreprocessorTest.preprocessor.preprocess()
        sliced_file_n = len(glob.glob(c.LF_SLICE + "Xsb9flAEymA/Xsb9flAEymA_*.wav"))
        bpm_changed_file_n = len(glob.glob(c.LF_CH_BPM + "Xsb9flAEymA/Xsb9flAEymA_*.wav"))
        self.assertEquals(48, sliced_file_n)
        self.assertEquals(48, bpm_changed_file_n)
