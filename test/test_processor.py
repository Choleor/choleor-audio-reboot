from django.test.testcases import TestCase
from audio.tasks import *


class AmplProcessorTest(TestCase):
    def test_get_ampl(self):
        self.assertEquals("", process_amplitude_d())


class SmlrProcessorTest(TestCase):
    def test_get_smlr(self):
        self.assertEquals("", process_similarity_d())
