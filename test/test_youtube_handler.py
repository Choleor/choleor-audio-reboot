from django.test.testcases import TestCase
from audio.services.youtube_handler import *


class YoutubeHandlerTest(TestCase):
    def test_write_from_meta(self):
        self.assertEquals(("5-_Uv8ggjk8", "DJ Snake - Taki Taki (Lyrics) ft. Selena Gomez, Ozuna, Cardi B", 218),
                          write_from_meta("Taki Taki", "CardiB"))

    def test_write_from_link(self):
        self.assertEquals(("JZ9pHBEUWPo", "The Greatest Showman - Never Enough (Vídeo con letra)", 199),
                          write_from_link("https://www.youtube.com/watch?v=JZ9pHBEUWPo"))

    def test_get_video_id(self):
        self.assertEquals("pSQk-4fddDI", get_video_id("https://www.youtube.com/watch?v=pSQk-4fddDI"))

    def test_get_video_title(self):
        self.assertEquals("The Greatest Showman Cast - A Million Dreams (Official Audio)",
                          get_video_title("https://www.youtube.com/watch?v=pSQk-4fddDI"))

    def test_get_video_duration(self):
        self.assertEquals(270, get_video_duration("https://www.youtube.com/watch?v=pSQk-4fddDI"))
