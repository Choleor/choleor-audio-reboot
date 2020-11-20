from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework.response import Response
from .models import *
from .serializers import AudioSerializer
from rest_framework.decorators import api_view
from rest_framework import status
from audio.dbmanager.redis_dao import *
from audio.utils.audio import *
from audio.tasks import *


@api_view(['GET'])
def url(request):
    """
    :param request: data 내_url 값
    :return:
    """
    url = request.GET.get("url")
    audio = None
    try:
        audio = Audio.objects.get(download_url=url)
        check_preprocessed_record(audio)
    except ObjectDoesNotExist:  # 처음 들어온 경우
        try:
            _id, _title, _duration = write_from_link(url)
            audio = Audio(audio_id=_id, title=_title, download_url=url, duration=_duration)
            Audio.save(audio)
            AudioPreprocessor(**AudioSerializer(audio).data).preprocess(). \
                apply_async(task_id=_id, expires=datetime.now() + timedelta(days=1))
        except Exception as e:
            print(e)
            return Response("cannot open file.", status=400)
    finally:
        return set_audio_response(config.LF_WAV + audio.audio_id + ".wav", audio.audio_id, "wav", audio.duration)


@api_view(['POST'])
def file(request):
    """
    :param request:
    :return:
    """
    audio_id = uuid.uuid1()
    ext = request.headers.get('extension')
    # Task chaining : 업로드 된 파일을 write --> 전처리 시행 [task chaining], DB에 별도로
    handle_uploaded_file(request.FILES, audio_id) if ext == "wav" else handle_uploaded_file(request.FILES, audio_id,
                                                                                            ext, LF_ORG).apply_async()
    duration = to_console(
        "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {path}.{ext}".format(
            path=LF_WAV + audio_id + ext if ext == "wav" else LF_ORG + audio_id + ext, ext=ext))
    return set_audio_response(request.FILES, audio_id, ext, duration)


@api_view(['GET'])
def meta(request):
    """
    :param request:
    :return:
    """
    audio_info = request.GET.get('title' + "-" + request.GET.get('artist'))
    audio = Audio.objects.filter(download_url=search_url_from_meta(audio_info))

    if bool(audio):  # 이미 데이터베이스에 있는 경우
        check_preprocessed_record(audio)
        return set_audio_response(LF_WAV + audio.audio_id + ".wav", audio.audio_id, "wav", audio.duration)
    else:
        _id, _title, _duration = write_from_meta(audio_info)
        audio = Audio(audio_id=_id, title=_title, download_url=url, duration=_duration)
        Audio.save(audio)
        AudioPreprocessor(**AudioSerializer(audio).data).preprocess(). \
            apply_async(task_id=_id, expires=datetime.now() + timedelta(hours=15))
        return set_audio_response(LF_WAV + audio.audio_id + ".wav", audio.audio_id, "wav", audio.duration)


@api_view(['GET'])
def interval_choice(request):
    """
    :param request: audio_id, start_sec, end_sec
    :return: user_id, interval(number)

    1. Check the preprocess redis whether the task is completed
    2. record on user_redis
    3. Give tasks to celery worker for processing similarity and amplitude (not recorded in cache)
    4. Give response to client
    """

    # get information from request
    audio_id, start_sec, end_sec = request.GET.get('audio_id'), request.GET.get('start_sec'), request.GET.get('end_sec')

    try:
        # 1. Check the preprocess redis whether the task is completed with audio_id (task_id)
        beat_track_list = PreprocessRedisHandler.get_preprocess_result(audio_id)

        # 2. Record on user redis
        start_sid = convert_sec_to_sid(audio_id, start_sec, beat_track_list)
        end_sid = convert_sec_to_sid(audio_id, end_sec, beat_track_list, option="end")
        user_id = uuid.uuid4()  # make user's id in this step
        interval_n = int(end_sid.split("ㅡ")[1]) - int(start_sid.split("ㅡ")[1])
        user_data = {"user_id": user_id,
                     "start_sid": start_sid, "end_sid": end_sid, "counter": 0,
                     "interval_n": interval_n}
        UserRedisHandler.set_user_info(**user_data)

        # 3. Process data for unrecorded audio slices with celery worker (background tasks)
        for i in range(int(start_sid.split("ㅡ")[1]), int(end_sid.split("ㅡ"))):
            _aud_sid = audio_id + "ㅡ" + str(i)
            # check if there's already processed data in cache
            if SimilarityRedisHandler.check_similarity_exists(_aud_sid):  # ALREADY processed in CACHE
                SimilarityRedisHandler.update_expire_date(_aud_sid)  # prevent to expiration --> update expire date
            else:  # PROCESS NEEDED --> CACHE INSERT
                # give processing tasks to celery worker
                process_similarity_d(_aud_sid).apply_async(_aud_sid, task_id="similarity" + _aud_sid)
                process_amplitude_d(_aud_sid).apply_async(_aud_sid, task_id="similarity" + _aud_sid)

        # 4. Respond to client
        response = HttpResponse({"user_id": user_id, "interval": interval_n})
        return response
    except Exception as e:
        print(e)
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def check_preprocessed_record(audio_object):
    # To prevent partially preprocessed data, process unsplitted src or insert info which is not recorded
    # check whether there's record in audio slice db, and compare with folder elements
    in_volume = set(
        [wav.split(".")[0] for wav in os.listdir(LF_SLICE + audio_object.audio_id) if wav.split(".")[1] == "wav"])
    in_db = set(AudioSlice.objects.filter(
        audio_id_id=audio_object.audio_id).values_list('audio_slice_id', flat=True))

    only_in_volume = in_volume - in_db
    only_in_db = in_db - in_volume

    for aud_sid in only_in_volume:  # DB에 insert
        AudioSlice.save(AudioSlice(aud_sid, calculate_duration_with_file(filepath=LF_WAV + aud_sid, ext="wav"),
                                   audio_id_id=aud_sid.split("ㅡ")[0]))
    for j in only_in_db:  # TODO volume 에 받기, 부분 전처리 다시..
        print(j)


def set_audio_response(audio_src, audio_id, ext, duration):
    response = HttpResponse(open(audio_src, "rb"))
    response['Content-Type'] = "application/octet-stream"
    response['Content-Disposition'] = f'attachment; filename="{audio_id}.{ext}"'  # wav만 보내지 않아도 되도록
    response['audio_id'] = audio_id
    response['duration'] = duration
    return response


def convert_sec_to_sid(audio_id, sec, beat_list, option="start"):
    # 2.6 3.8 10.3 <--- 5.9가 들어오면 start일 경우 1(3,8), 2(10.3)
    audio_sid_list = AudioSlice.objects.filter(audio_id_id=audio_id).values_list('audio_slice_id', flat=True)
    if len(audio_sid_list) != len(beat_list):
        beat_list = AudioSlice.objects.filter(audio_id_id=audio_id).values_list('start_sec', flat=True)
    for idx, val in enumerate(beat_list):
        if idx == len(beat_list) - 1:
            return audio_id + audio_sid_list[idx]
        if val < sec < beat_list[idx + 1]:
            return audio_id + audio_sid_list[idx] if option == "start" else audio_id + audio_sid_list[idx + 1]
