from django.core.exceptions import ObjectDoesNotExist
from django.http import StreamingHttpResponse, FileResponse, HttpResponse, JsonResponse
from rest_framework.response import Response
from .models import AudioSlice, Audio
from .serializers import AudioSerializer, AudioSliceSerializer
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FileUploadParser
from .utils import utils as ut
from audio.dbmanager.redis_dao import *
from audio.dbmanager.preprocessor import AudioPreprocessor
from audio.dbmanager.youtube_handler import *
import re
import time

range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
file_count = 0

"""
timeline
t0 : page 1에서 사용자가 오디오 요청을 보낼 때
t1 : page 2에서 사용자가 오디오의 구간을 선택할 때
"""

"""
t0 > CELERY RESULT BACKEND
사용자의 오디오 요청에 대한 전처리 실행 후 기록 --> view 함수에
"""
# preprocessor = AudioPreprocessor()
# # task_id는 audio의 id
# # audio_id = uuid.uuid4()  # 처음 들어오는 경우, 그게 아니면 database에서 꺼내오기
# AudioPreprocessor().preprocess.apply_async((3, 56), task_id="hiek", expires=datetime.now() + timedelta(days=1))


"""
t1 > USER INFO RECORD : (audio <----> choreo <----> product) Inter-server communication
KEY "a30gk3" <-- uuid.uuid4()
VAL (HSET)
{ audio_id : e317fce <-- 클라이언트에게 받을 것
start : 13  <-- audio_handler가 계산하도록
end : 31 <-- audio_handler가 계산하도록
progress : 0.0 }  <-- 어느정도 진행되었는지 percentage
"""

"""
t1 > SIMILARITY : (audio <----> choreo) Inter-server communication
KEY e317fce-14 <-- 노래 구간 id
VAL [ "af3g0s39_13 : 89", "ldf9a8i_4 : 90", "fk02j3bu_9 : 99", ... ] <-- 노래구간 id 와 점수가 매핑된 요소들로 구성된 list
"""

"""
t1 > AMPLITUDE : (audio <----> choreo) Inter-server communication
KEY e317fce-14 <-- 노래 구간 id
VAL [ 7 2 9 8 6 ] <-- 점수 list
"""

"""
===================================================================================================================
"""

# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             instance = ModelWithFileField(file_field=request.FILES['file'])
#             instance.save()
#             return HttpResponseRedirect('/success/url/')
#     else:
#         form = UploadFileForm()
#     return render(request, 'upload.html', {'form': form})

@api_view(['POST'])
@parser_classes([MultiPartParser])
def meta(request):
    data = MultiPartParser.parse(request)
    print(data)
    res = write_from_meta()
    return Response(AudioSerializer(Audio.objects.all(), many=True).data)


@api_view(['POST'])
async def youtube_url(request):
    download_url = request.data.get("download_url")
    try:
        # 이미 있는 경우

        return Response(AudioSerializer(Audio.objects.get(download_url=download_url)).data)
    except ObjectDoesNotExist:
        try:
            print(f"started at {time.strftime('%X')}")
            _id, _title, _duration = await write_from_link(download_url)
            audio = Audio(audio_id=_id, title=_title, download_url=download_url, duration=_duration)
            audio.save()
            serializer = AudioSerializer(audio)
            # 이게 tasks에 해당됨
            AudioPreprocessor(audio=audio).preprocess()
            # 파일 찾아서 정보와 함께 보내주기
            return Response(serializer.data)
        except:
            print("===========download failure=============")
            return Response("cannot open file.", status=400)

    # response = StreamingHttpResponse(streaming_content=request.FILES["audio_file"])
    # response['Content-Disposition'] = f'attachment; filename="{request.data["audio_file"]}"'
    # return response


@api_view(['POST'])
@parser_classes([MultiPartParser])
# @renderer_classes([MultiPartRenderer])
def file(request):
    """
    :param request:
    :return: audio_id 와 file을 streaming 형태로
    """
    ext = request.data.get("ext")
    global file_count
    filename = "up" + str(file_count)
    if ext != "wav":
        ut.get_console_output(
            'ffmpeg -n -i "{}/{}.{}" "{}/{}.wav"'.format("../../media/ORG", filename, ext, "../../media/WAV",
                                                         filename))

    # 바로 파일 저장 - store in the volume
    file_count += 1

    response = StreamingHttpResponse(streaming_content=request.data["audio_file"])
    response['Content-Disposition'] = f'attachment; filename="{request.data["audio_file"]}"'
    return response


@api_view(['POST'])
def skeletal_after_interval(request):
    """
    :param request: audio_id, start_sec, end_sec
    :return:
    """
    audio_id = request.data.get('audio_id')
    user_start_sec = request.data['start_sec']
    user_end_sec = request.data['end_sec']

    UserRedisHandler.set_user_info(audio_id, user_start_sec, user_end_sec)

    if bool(AudioSlice.objects.filter(audio_slice_id__contains=audio_id)):
        start_arr = AudioSlice.objects.values_list('start_sec', flat=True)
        start_audio_slice_id = AudioSlice.objects.get(
            start_sec=ut.find_nearest(start_arr, user_start_sec)).only('audio_slice_id')
        end_audio_slice_id = request.data.get('audio_id') + AudioSlice.objects.get(
            start_sec=ut.find_nearest(start_arr, user_end_sec)).only('audio_slice_id').split("_")[1]

    else:
        audio_handler = AudioPreprocessor(Audio.objects.get(audio_id=audio_id))
        audio_handler.preprocess()
        start_audio_slice_id = audio_handler.get_slice_id(ut.find_nearest(audio_handler.beat_track, user_start_sec))
        end_audio_slice_id = audio_handler.get_slice_id(ut.find_nearest(audio_handler.beat_track, user_end_sec))

    interval_number = int(end_audio_slice_id.split("ㅡ")[1]) - int(start_audio_slice_id.split("ㅡ")[1])

    # Task 1. Similarity process & get into redis
    # smlr_app = Celery('redis_dao', backend=cc.result_smlr_backend, broker=cc.broker_smlr_url)
    # smlr_app.config_from_object('celery_config') --꼭 안해도 될 듯
    # 여기에 혜린이가 한 부분을 어떻게 어떻게 만들어서..
    # cluster_smlr.apply_async(filter_kmeans_labels, filter_feat, 0, 6))

    # Task 2. Amplitude process & get into redis
    # ampl_app = Celery(backend=cc.result_ampl_backend, broker=cc.broker_ampl_url)
    # get_amplitude.apply_async((3, 56), task_id=audio_id, expires=datetime.now() + timedelta(days=1))

    return Response(
        AudioSliceSerializer(start_audio_slice_id=start_audio_slice_id, end_audio_slice_id=end_audio_slice_id,
                             interval_number=interval_number).data)


# app = Celery('redis_dao', backend=cc.result_backend, broker=cc.broker_url)
# app.config_from_object('celery_config')


# def youtube(request):
#     # task_id는 audio의 id
#     audio_id = uuid.uuid4()  # 처음 들어오는 경우, 그게 아니면 database에서 꺼내오기
#     preprocess.apply_async((3, 56), task_id=audio_id, expires=datetime.now() + timedelta(days=1))

# def serve(request):
#     return FileResponse(open(request.data.get('music'), 'rb'))


@api_view(['POST'])
def get_music(request):
    with open(request.data.get('music'), 'rb') as f:
        response = HttpResponse(f, content_type='application/octet-stream')
        # 필요한 응답헤더 세팅
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(request.data.get('music'))
        return response

    # data = {
    #     "audio_id": "dfsdff",
    #     "interval_number": 14,
    #     "music": open(request.data.get('music'), 'rb')
    # }
    # return HttpResponse(data)
    # response = HttpResponse(content=open(request.data.get('music'), 'rb'))
    # response['Content-Type'] = 'application/json'
    # return FileResponse(open(request.data.get('music'), 'rb'))
