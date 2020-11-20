from rest_framework import serializers
from audio.models import Audio, AudioSlice
from configuration.config import *


class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = '__all__'


class AudioSliceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioSlice
        fields = '__all__'


# class UploadSerializer(serializers.Serializer):
#     audio_file = serializers.FileField()
#     ext = serializers.CharField(max_length=5)

# def __init__(self, audio_file, extension):
#     self.audio_file = audio_file
#     self.ext = extension

if __name__ == '__main__':
    aud = Audio(audio_id="GNGbmg_pVlQ", title='Selena Gomez - Back to You (Lyrics)',
                duration=207.06, download_url="http://www.youtube.com/watch?v=GNGbmg_pVlQ")
    aud.save()
    result = AudioSerializer(aud).data
    print(result)
