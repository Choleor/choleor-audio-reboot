from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# ISSUE
# celery.py라고 할 시에 reference 인식 못해 순환 참조 에러 발생, 일부러 파일명 바꿈

""" choleor_audio.settings 파일을 사용하도록 설정 """
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'choleor_audio.settings')

""" audio를 사용하도록 설정 """
app = Celery('audio')  # celery를 적용하고자 하는 Application
app.config_from_object('audio.celeryconfig', namespace='PREPROCESS')
# app.config_from_object('audio.celeryconfig', namespace='AMPLITUDE')
# app.config_from_object('audio.celeryconfig', namespace='SIMILARITY') # celery -A 다시 실행시키고 넣을 것
app.autodiscover_tasks()


# DOESN'T WORK NOW --> muti task needed
# app1 = Celery('audio')
# app1.config_from_object('audio.celeryconfig', namespace='AMPLITUDE')
# app1.autodiscover_tasks()
#
# app2 = Celery('audio')
# app2.config_from_object('audio.celeryconfig', namespace='SIMILARITY')


# @app1.task(bind=True)
# @app2.task(bind=True)
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


if __name__ == '__main__':
    app.start()
