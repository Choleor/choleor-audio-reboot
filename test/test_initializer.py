from django.test import TestCase
from audio.dbmanager.initializer import *
import glob


class InitializerTest(TestCase):
    def test_initialize(self):
        _expected_res = ""
        self.assertEquals(_expected_res, Initializer.initialize())

    def test_delete(self):
        glob.glob()
        self.assertEquals()
