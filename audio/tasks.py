from __future__ import absolute_import, unicode_literals
from audio.dbmanager.preprocessor import AudioPreprocessor
from configuration.config import LF_WAV
from audio.utils.utils import get_console_output as to_console
from audio.celery_tas import app
from audio.services.smlr_processor import *
from audio.services.ampl_processor import *
from audio.dbmanager.youtube_handler import *
from audio.dbmanager.dropper import *
from celery import shared_task


# from celery import Celery
# from celery import shared_task, task
# from audio.celery_tas import app1, app2


@app.task(name="preprocess", ignore_result=True)
def preprocess_d(a, b, c):
    return AudioPreprocessor(a, b, c).preprocess()


@app.task(name="uploaded_file_handling", ignore_result=True)
def handle_uploaded_file(file, file_name, extension="wav", path=LF_WAV):
    with open('{}{}.{}'.format(path, file_name, extension), 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    if extension != "wav":  # convert to wav
        to_console("ffmpeg -i {}{}.{} -o {}{}.wav".format(path, file_name, extension, LF_WAV, file_name))
    return "completed"


@app.task(name="amplitude_process", ignore_result=True)
def process_amplitude_d(_audio_slice_id):
    return AmplitudeProcessor.process_amplitude(_audio_slice_id)


@app.task(name="similarity_process", ignore_result=True)
def process_similarity_d(_audio_slice_id):
    #  군집 개수, 음악 파일의 경로, 음악 파일 이름, 유사한 노래 상위 몇개까지 출력할지
    return SimilarityProcessor(5, LF_WAV + _audio_slice_id + "/", _audio_slice_id + ".wav", 40).process_similarity()


@app.task(name="add", ignore_result=True)
def add(a, b):  # health check
    return [a, b, a + b]


@app.task(name="kwarg_add", ignore_result=True)
def kwargs_temp(**kwargs):
    return sum(kwargs.values())


if __name__ == '__main__':
    # ex1 = kwargs_temp.apply_async(kwargs={"kwarg1": 1, "kwarg2": 3}, task_id="kwargtest")  # celery-task-meta-example1
    ex2 = add.apply_async(args=[23, 20], task_id="nnnnnnnnnnnnn")  # celery-task-meta-example2
    # print(SimilarityRedisHandler.get_similarity_list("other1"))
    # print(SimilarityRedisHandler.get_similarity_list("other2"))
    Dropper.drop("cnyCcF20pRo")
    write_from_link("https://www.youtube.com/watch?v=cnyCcF20pRo")
    res = preprocess_d.apply_async(args=['cnyCcF20pRo', 'Ariana Grande - 34+35 (lyric video)', 174], task_id="nnnnnhdddddd")
    print(ex2.state, ex2.get())
    print(res.state, res.get())

    # audio_slice_id = "sdkfjird_3"
    # similarity = process_similarity.apply_async(args=[audio_slice_id], task_id="similarity-" + audio_slice_id)
    # amplitude = process_amplitude.apply_async(args=[audio_slice_id], task_id="amplitude-" + audio_slice_id)

    # usage of deprecated module
    # res = (preprocess_wraapper.s('cnyCcF20pRo', 'Ariana Grande - 34+35 (lyric video)',
    #                              174) | preprocess.s()).apply_async(task_id="other..")
