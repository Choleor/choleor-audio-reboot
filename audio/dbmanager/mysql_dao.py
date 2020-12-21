# import os
#
# os.environ['DJANGO_SETTINGS_MODULE'] = 'choleor_audio.settings'
#
# import django
#
# django.setup()
from audio.models import *


class AudioHandler:
    @staticmethod
    def get_end_pose_type(_choreo_slice_id):
        return AudioSlice.objects.get(choreo_slice_id=_choreo_slice_id).end_pose_type.decode('UTF-8')

    @staticmethod
    def get_movement_list():
        return [int(i) for i in AudioSlice.objects.values_list('movement', flat=True)[0].split(",")]

    @staticmethod
    def get_movement_score(_choreo_slice_id):
        return [int(i) for i in AudioSlice.objects.get(choreo_slice_id=_choreo_slice_id).movement.split(",")]

    @staticmethod
    def insert_all(*args):
        Audio.save(
            Audio(choreo_id=args[8], download_url="http://www.youtube.com/v?" + args[8], start_sec=0.00,
                  end_sec=0.00))


class AudioSliceHandler:
    def __init__(self):
        print()


if __name__ == '__main__':
    AudioHandler.insert_all("ymZGEY0OAzkㅡ4", "3,4,6,7,9", 3.28, False, False, b"010101001010010",
                            b"10000100000010", "EZk1HsQvi5Q", "ymZGEY0OAzk")
