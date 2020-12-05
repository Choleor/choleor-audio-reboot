from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser, MultiPartParser, FileUploadParser
from pydub import AudioSegment
from .serializers import AudioSerializer
from rest_framework.decorators import api_view, parser_classes
from rest_framework import status
from audio.dbmanager.redis_dao import *
from audio.utils.audio import *
from audio.tasks import *
from rest_framework.response import Response
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser


@api_view(['POST'])
def y_url(request):
    """
    :param request: data 내_url 값
    :return:
    """
    _url = request.data.get("url")
    audio = None
    try:
        audio = Audio.objects.get(download_url=_url)
        print(audio)
        check_preprocessed_record(audio)
    except ObjectDoesNotExist:  # 처음 들어온 경우
        try:
            _id, _title, _duration = write_from_link(_url)
            audio = Audio(audio_id=_id, title=_title, download_url=_url, duration=_duration)
            Audio.save(audio)
            AudioPreprocessor(**AudioSerializer(audio).data).preprocess(). \
                apply_async(task_id=_id, expires=datetime.now() + timedelta(days=1))
        except Exception as e:
            print(e)
            return Response("cannot open file.", status=400)
    finally:
        return set_audio_response(config.LF_WAV + audio.audio_id + ".wav", audio.audio_id, "wav", audio.duration)


@api_view(['POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def file(request):
    """
    :param request:audio_file, extension
    :return:
    """
    audio_id = str(uuid.uuid4())

    # f = open(request.FILES.get('file'), "rb")
    destination = open(f"/home/jihee/choleor_media/audio/WAV/{audio_id}.wav", 'wb+')

    for chunk in request.FILES.get('file').chunks():
        destination.write(chunk)
    destination.close()

    # Task chaining : 업로드 된 파일을 write --> 전처리 시행 [task chaining], DB에 별도로
    # handle_uploaded_file(request.FILES, audio_id).apply_async()

    duration = to_console(
        "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {path}.wav".format(
            path=LF_WAV + audio_id))
    return set_audio_response(f"/home/jihee/choleor_media/audio/WAV/{audio_id}.wav", audio_id, "wav", duration)


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
        audio = Audio(audio_id=_id, title=_title, download_url="http://www.youtube.com/watch?v=" + _id,
                      duration=_duration)
        Audio.save(audio)
        AudioPreprocessor(**AudioSerializer(audio).data).preprocess(). \
            apply_async(task_id=_id, expires=datetime.now() + timedelta(hours=15))
        return set_audio_response(LF_WAV + audio.audio_id + ".wav", audio.audio_id, "wav", audio.duration)


@api_view(['POST'])
def interval(request):
    """
    :param request: audio_id, start_sec, end_sec
    :return: user_id, interval(number)

    1. Check the preprocess redis whether the task is completed
    2. record on user_redis
    3. Give tasks to celery worker for processing similarity and amplitude (not recorded in cache)
    4. Give response to client
    """

    # get information from request
    audio_id, start_sec, end_sec = request.data.get('audio_id'), request.data.get('start_sec'), request.data.get(
        'end_sec')
    user_id = str(uuid.uuid4())
    print(user_id)
    start_idx = 9
    end_idx = 14
    interval_n = end_idx - start_idx + 1
    UserRedisHandler.set_user_info(user_id, audio_id, start_idx, end_idx, 0, interval_n)

    audio_source = AudioSegment.from_wav(LF_WAV + audio_id + ".wav")
    user_root_dir = "/home/jihee/choleor_media/product/"+user_id + "/"

    if not os.path.exists(user_root_dir):
        os.mkdir(user_root_dir)
        os.mkdir(user_root_dir+"100%/")

    audio_source[37500:75700].export(user_root_dir+"100%/fin_aud.wav")

    # 4. Respond to client
    return JsonResponse({"user_id": user_id, "interval_number": interval_n})

    # try:
    # 1. Check the preprocess redis whether the task is completed with audio_id (task_id)
    # beat_track_list = PreprocessRedisHandler.get_preprocess_result(audio_id)

    # 2. Record on user redis
    # start_sid = convert_sec_to_sid(audio_id, start_sec, beat_track_list) # idx
    # end_sid = convert_sec_to_sid(audio_id, end_sec, beat_track_list, option="end") # end idx
    # user_id = str(uuid.uuid4())  # make user's id in this step
    # interval_n = int(end_sid.split("ㅡ")[1]) - int(start_sid.split("ㅡ")[1]) + 1
    # UserRedisHandler.set_user_info(user_id, start_sid, end_sid, 0, interval_n)

    # 3. Process data for unrecorded audio slices with celery worker (background tasks)
    # for i in range(int(start_sid.split("ㅡ")[1]), int(end_sid.split("ㅡ"))):
    #     _aud_sid = audio_id + "ㅡ" + str(i)
    #     # check if there's already processed data in cache
    #     if SimilarityRedisHandler.check_similarity_exists(_aud_sid):  # ALREADY processed in CACHE
    #         SimilarityRedisHandler.update_expire_date(_aud_sid)  # prevent to expiration --> update expire date
    #     else:  # PROCESS NEEDED --> CACHE INSERT
    #         # give processing tasks to celery worker
    #         process_similarity_d(_aud_sid).apply_async(_aud_sid, task_id="similarity" + _aud_sid)
    #         process_amplitude_d(_aud_sid).apply_async(_aud_sid, task_id="similarity" + _aud_sid)

    # user_id = str(uuid.uuid4())
    # start_idx = 9
    # end_idx = 16
    # interval_n = end_idx - start_idx
    # UserRedisHandler.set_user_info(user_id, audio_id, start_idx, end_idx, 0, interval_n)
    # # 4. Respond to client
    # return JsonResponse({"user_id": "34", "interval_number": interval_n})


# except Exception as e:
#     print(e)
#     return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def check_preprocessed_record(audio_object):
    # To prevent partially preprocessed data, process unsplitted src or insert info which is not recorded
    # check whether there's record in audio slice db, and compare with folder elements

    print("=================check if it is processed====================")
    #
    # # check data if all is in media folder
    # in_volume = set(
    #     [wav.split(".")[0] for wav in os.listdir(LF_SLICE + audio_object.audio_id) if wav.split(".")[1] == "wav"])
    # # check if all audio slice information are in database
    # in_db = set(AudioSlice.objects.filter(
    #     audio_id_id=audio_object.audio_id).values_list('audio_slice_id', flat=True))
    #
    # only_in_volume = in_volume - in_db
    # only_in_db = in_db - in_volume
    #
    # print(only_in_volume)
    # print(only_in_db)
    #
    # for aud_sid in only_in_volume:  # DB에 insert
    #     AudioSlice.save(AudioSlice(aud_sid, calculate_duration_with_file(filepath=LF_WAV + aud_sid, ext="wav"), -1.00,
    #                                aud_sid.split("ㅡ")[0]))
    #
    # for j in only_in_db:  # TODO volume 에 받기, 부분 전처리 다시..
    #     print(j)


def set_audio_response(audio_src, audio_id, ext, duration):
    response = HttpResponse(open(audio_src, "rb"))
    response["Access-Control-Allow-Origin"] = "*"
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
