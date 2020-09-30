from django.db import models


class Audio(models.Model):
    audio_id = models.CharField(primary_key=True, max_length=30)
    title = models.CharField(max_length=100)
    download_url = models.URLField(max_length=150)
    duration = models.FloatField(default=0.00)

    def __str__(self):
        return self.audio_id


class AudioSlice(models.Model):
    audio_slice_id = models.CharField(primary_key=True, max_length=35)
    duration = models.FloatField(default=-1.00)
    start_sec = models.FloatField(default=-1.00)
    audio_id = models.ForeignKey(Audio, on_delete=models.CASCADE)

    def __str__(self):
        return self.audio_slice_id
