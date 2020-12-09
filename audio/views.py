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
    try:
        audio = Audio.objects.get(download_url=_url)
        _id = audio.audio_id
    except ObjectDoesNotExist:  # 처음 들어온 경우
        try:
            _id, _title, _duration = write_from_link(_url)
            AudioPreprocessor(_id, _title, _duration).insert_to_audio()
            # AudioPreprocessor(**AudioSerializer(audio).data).preprocess(). \
            #     apply_async(task_id=_id, expires=datetime.now() + timedelta(days=1))
        except Exception as e:
            print(e)
            return Response("cannot open file.", status=400)
    finally:
        return set_audio_response(f"{LF_WAV}{_id}.wav", audio.audio_id, audio.duration)


@api_view(['GET'])
def meta(request):
    """
    :param request:
    :return:
    """
    audio_info = request.GET.get('title' + "-" + request.GET.get('artist'))
    audio = Audio.objects.filter(download_url=search_url_from_meta(audio_info))

    if bool(audio):  # 이미 데이터베이스에 있는 경우
        return set_audio_response(f"{LF_WAV}{audio.audio_id}.wav", audio.audio_id, audio.duration)
    else:
        _id, _title, _duration = write_from_meta(audio_info)
        AudioPreprocessor(_id, _title, _duration).insert_to_audio()
        # AudioPreprocessor(**AudioSerializer(audio).data).preprocess(). \
        #     apply_async(task_id=_id, expires=datetime.now() + timedelta(hours=15))
        return set_audio_response(f"{LF_WAV}{_id}.wav", audio.audio_id, audio.duration)


@api_view(['POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def file(request):
    """
    :param request:audio_file, extension
    :return:
    """
    audio_id = str(uuid.uuid4())
    destination = open(f"{LF_WAV}{audio_id}.wav", 'wb+')
    for chunk in request.FILES.get('file').chunks():
        destination.write(chunk)
    destination.close()
    duration = to_console(
        "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {path}.wav".format(
            path=LF_WAV + audio_id))
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
    aud = Audio.objects.filter(audio_id=audio_id)[0]
    user_id = str(uuid.uuid4())
    preproc = AudioPreprocessor(audio_id, aud.title, aud.duration, bpm=aud.bpm, user_start=start_sec)
    start_idx, end_idx = preproc.preprocess()
    partition = preproc.remainder
    interval_n = end_idx - start_idx + 1
    UserRedisHandler.set_user_info(user_id, partition, audio_id, start_idx, end_idx, 0, interval_n)

    usr_dir = f"/home/jihee/choleor_media/product/{user_id}/"

    if not os.path.exists(usr_dir):
        os.mkdir(usr_dir)
        os.mkdir(usr_dir + "100%/")

    wav_src = AudioSegment.from_wav(f"{LF_WAV}/{audio_id}.wav")
    wav_src[1000 * preproc.usr_ssec:1000 * preproc.usr_esec].export(f"{usr_dir}100%/FINDIO.wav")

    # Job 1. process amplitude  --> store in redis
    for i in range(start_idx, end_idx):
        _aud_sid = audio_id + "ㅡ" + str(i)
        # check if there's already processed data in cache
        if SimilarityRedisHandler.check_similarity_exists(partition + ">" + _aud_sid):  # ALREADY processed in CACHE
            SimilarityRedisHandler.update_expire_date(
                partition + ">" + _aud_sid)  # prevent to expiration-> update expire date
            continue
        else:  # PROCESS NEEDED --> CACHE INSERT
            smlr_dlist = SimilarityProcessor(5, f"{LF_SLICE}/{partition}/{audio_id}/{_aud_sid}.wav", f"{_aud_sid}.wav",
                                             200).process()
            smlr_pk = pickle.dumps(smlr_dlist)
            SimilarityRedisHandler.dao.set(f"{partition}>{_aud_sid}", smlr_pk)
            ampl_list = AmplitudeProcessor.process(f"{_aud_sid}.wav")
            ampl_pk = pickle.dumps(ampl_list)
            AmplitudeRedisHandler.dao.set(f"{partition}>{_aud_sid}", ampl_pk)

            # optimization 1. multi-processing 적용
            # optimization 2. celery + redis
            # process_similarity_d(_aud_sid).apply_async(_aud_sid, task_id="similarity" + _aud_sid)
            # process_amplitude_d(_aud_sid).apply_async(_aud_sid, task_id="similarity" + _aud_sid)
            # optimization 3. kubernetes job 실행

            # TODO 이후 job 이름으로 바꾸기, 네트워크 연결?
            ampl_job = "/home/jihee/choleor/dev_space/PycharmProjects/choleor_kube/audio/choleor-audio-job.yaml"
            smlr_job = ""
            os.system(f"microk8s kubectl apply -f {smlr_job}")  # 나중에 async로 바꾸던지
            os.system(f"microk8s kubectl apply -f {ampl_job}")

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
