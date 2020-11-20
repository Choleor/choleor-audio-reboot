from django.db import models
from django.core.cache import cache
from configuration.config import *
from audio.utils.utils import find_nearest


# """
# Activate configuration code below only when not running server
# """
# import os
# import django
# os.environ['DJANGO_SETTINGS_MODULE'] = 'choleor_audio.settings'
# django.setup()


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        pass

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        # self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()

    @classmethod
    def load(cls):
        if cache.get(cls.__class__.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
            print(obj.__str__())
            return cache.get(cls.__class__.__name__)


class Audio(SingletonModel):
    audio_id = models.CharField(primary_key=True, max_length=30)
    title = models.CharField(max_length=100)
    duration = models.FloatField(default=0.00)
    download_url = models.URLField(max_length=150)


class AudioSlice(SingletonModel):
    audio_slice_id = models.CharField(primary_key=True, max_length=35)
    duration = models.FloatField(default=-1.00)
    start_sec = models.FloatField(default=-1.00)  # TODO -> deprecate
    audio_id = models.ForeignKey(Audio, on_delete=models.CASCADE)

    def __str__(self):
        return self.audio_slice_id
