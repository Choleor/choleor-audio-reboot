from django.test import TestCase
from audio.services.initializer import *


class InitializerTest(TestCase):
    def test_initialize(self):
        _expected_res = ""
        self.assertEquals(_expected_res, Initializer.initialize())
