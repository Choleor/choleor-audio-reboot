from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, parser_classes
from audio.dbmanager.redis_dao import *
from audio.tasks import *
from audio.utils.audio import *
from pydub import AudioSegment
from .models import *
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
# from audio.services.job import job_handler
from .tasks import process_similarity_d, process_amplitude_d


@api_view(['POST'])
def check(request):
    return JsonResponse("audio_server checked")


@api_view(['POST'])
def y_url(request):
    """
    :param request: data 내_url 값
    :return:
    """

    _url = request.data.get("url")
    _id = None
    _duration = None
    try:
        print("request comes!")
        audio = Audio.objects.get(download_url=_url)
        _id = audio.audio_id
        _duration = audio.duration
        print("existed " + _id)
    except ObjectDoesNotExist:  # 처음 들어온 경우
        try:
            print("before calling link")
            _id, _title, _duration = write_from_link(_url)
            print(_id, _title, _duration)
            Audio(_id, _title, _duration, download_url="http://www.youtube.com/watch?v=" + _id).save()
        except Exception as e:
            print(e)
            return Response("cannot open file.", status=400)
    finally:
        # return JsonResponse({"audio_id": _id, "duration": _duration})
        return set_audio_response(f"{LF_WAV}{_id}.wav", _id, _duration)


@api_view(['POST'])
def meta(request):
    """
    :param request:
    :return:
    """
    audio_info = request.data.get('title' + "-" + request.GET.get('artist'))
    audio = Audio.objects.filter(download_url=search_url_from_meta(audio_info))
    if not bool(audio):
        _id, _title, _duration = write_from_meta(audio_info)
        audio = AudioPreprocessor(_id, _title, _duration).insert_to_audio()
    # return JsonResponse({"audio_id": audio.audio_id,"duration": audio.duration})

    if bool(audio):  # 이미 데이터베이스에 있는 경우
        return JsonResponse({"audio_id": audio.audio_id, "duration": audio.duration})
    #     # TODO return set_audio_response(f"{LF_WAV}{audio.audio_id}.wav", audio.audio_id, audio.duration)
    else:
        _id, _title, _duration = write_from_meta(audio_info)
        audio = AudioPreprocessor(_id, _title, _duration).insert_to_audio()
        return JsonResponse(audio.audio_id, audio.duration)
        # TODO return set_audio_response(f"{LF_WAV}{_id}.wav", audio.audio_id, audio.duration)


@api_view(['POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def file(request):
    """
    :param request:audio_file, extension
    :return:
    """
    audio_id = str(uuid.uuid4())
    destination = open(f"{LF_WAV}{audio_id}.wav", 'wb+')
    print(request.FILES.get('file'))
    for chunk in request.FILES.get('file').chunks():
        destination.write(chunk)
    destination.close()
    duration = to_console(
        "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {path}.wav".format(
            path=LF_WAV + audio_id))
    Audio(audio_id=audio_id, duration=duration).save()
    # AudioPreprocessor(audio_id, "", duration).insert_to_audio()
    # T return JsonResponse({"audio_id" : audio_id, "duration": duration})
    return set_audio_response(f"{LF_WAV}{audio_id}.wav", audio_id, duration)


@api_view(['POST'])
def interval(request):
    """
    :param request: audio_id, start_sec, end_sec
    :return: user_id, interval(number)

    DEPRECATED Check the preprocess redis whether the task is completed
    2. record on user_redis
    3. Give tasks to celery worker for processing similarity and amplitude (not recorded in cache)
    4. Give response to client
    """

    # Preprocess execution first
    audio_id, start_sec, end_sec = request.data.get('audio_id'), request.data.get('start_sec'), request.data.get(
        'end_sec')
    print(audio_id, start_sec, end_sec)
    print(type(audio_id), type(start_sec), type(end_sec))
    aud = Audio.objects.filter(audio_id=audio_id)[0]
    print(aud)
    user_id = str(uuid.uuid4())
    print(user_id)
    preproc = AudioPreprocessor(audio_id, aud.title, aud.duration, bpm=aud.bpm, user_start=start_sec, user_end=end_sec)
    start_idx, end_idx = preproc.preprocess()
    print(start_idx, end_idx)
    partition = preproc.remainder
    interval_n = end_idx - start_idx + 1

    UserRedisHandler.set_user_info(user_id, partition, audio_id, preproc.bpm, start_idx, end_idx, 0, interval_n)
    print("<======================= bpm =======================>")
    print(preproc.bpm)
    print("<======================= user redis =======================>")

    usr_dir = f"/home/jihee/choleor_media/product/{user_id}/"

    if not os.path.exists(usr_dir):
        os.mkdir(usr_dir)
        os.mkdir(usr_dir + "100%/")

    # ========================== Job =============================
    wav_src = AudioSegment.from_wav(f"{LF_WAV}/{audio_id}.wav")
    wav_src[1000 * preproc.usr_ssec:1000 * preproc.usr_esec].export(f"{usr_dir}100%/FINDIO.wav")

    print("<======================= audio segmentation fin =======================>")
    # Job 1. process amplitude  --> store in redis
    for i in range(start_idx, end_idx):
        _aud_sid = audio_id + "ㅡ" + str(i)

        # check if there's already processed data in cache
        if SimilarityRedisHandler.check_similarity_exists(
                str(partition) + ":" + _aud_sid):  # ALREADY processed in CACHE
            SimilarityRedisHandler.update_expire_date(
                str(partition) + ":" + _aud_sid)  # prevent to expiration-> update expire date
        else:
            path = f"/home/jihee/choleor_media/audio/SLICE/{partition}/{audio_id}/{_aud_sid}.wav"
            SimilarityProcessor.process_for_user(audio_id, partition, start_idx, end_idx)

            # get_redis_connection("similarity-wq").dao.rpush(str(partition) + ":" + _aud_sid,
            #                                                 ">".join([path, audio_id, partition, start_idx, end_idx]))
        if AmplitudeRedisHandler.check_amplitude_exists(str(partition) + ":" + _aud_sid):  # ALREADY processed in CACHE
            AmplitudeRedisHandler.update_expire_date(
                str(partition) + ":" + _aud_sid)  # prevent to expiration-> update expire date
        else:  # PROCESS NEEDED --> CACHE INSERT
            # get_redis_connection("amplitude-wq").dao.rpush(str(partition) + ":" + _aud_sid,
            #                                                ">".join([audio_id, partition, start_idx, end_idx]))
            # job_handler.ampl_job_main()
            AmplitudeProcessor.process_for_user(audio_id, partition, start_idx, end_idx)
            # process_amplitude_d.apply_async(args= (audio_id, str(partition), start_idx, end_idx), task_id="amplitude" + _aud_sid)
    # Respond to client
    return JsonResponse({"user_id": user_id, "interval_number": interval_n})


def set_audio_response(audio_src, audio_id, duration):
    response = HttpResponse(open(audio_src, "rb"))
    response["Access-Control-Allow-Origin"] = "*"
    response['Content-Type'] = "application/octet-stream"
    response['Content-Disposition'] = f'attachment; filename="{audio_id}.wav'  # wav만 보내지 않아도 되도록
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
