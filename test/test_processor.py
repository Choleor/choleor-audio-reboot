from django.test.testcases import TestCase
from audio.services.smlr_processor import *
from audio.services.ampl_processor import *


class AmplProcessorTest(TestCase):
    def test_get_ampl(self):
        self.assertEquals("", get_amplitude())


class SmlrProcessorTest(TestCase):
    def test_get_smlr(self):
        self.assertEquals("", "")
