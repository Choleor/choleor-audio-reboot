from rest_framework import serializers
from .models import Audio


class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = ['audio_id', 'title', 'download_url', 'duration']


class AudioSliceSerializer(serializers.Serializer):
    start_audio_slice_id = serializers.CharField()
    end_audio_slice_id = serializers.CharField()
    interval_number = serializers.IntegerField()

# class UploadSerializer(serializers.Serializer):
#     audio_file = serializers.FileField()
#     ext = serializers.CharField(max_length=5)

# def __init__(self, audio_file, extension):
#     self.audio_file = audio_file
#     self.ext = extension
