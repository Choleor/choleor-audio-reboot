from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from django.http import FileResponse, StreamingHttpResponse
from rest_framework.response import Response
from .models import AudioSlice, Audio
from .serializers import AudioSerializer, AudioSliceSerializer
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser, JSONParser
from utils import utils as ut
from .services.audio_handler import AudioHandler
from .services.youtube_info import *
import asyncio
import time
file_count = 0


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
        #
        return Response(AudioSerializer(Audio.objects.get(download_url=download_url)).data)
    except ObjectDoesNotExist:
        try:
            print(f"started at {time.strftime('%X')}")
            _id, _title, _duration = await write_from_link(download_url)
            audio = Audio(audio_id=_id, title=_title, download_url=download_url, duration=_duration)
            audio.save()
            serializer = AudioSerializer(audio)
            # 이게 tasks에 해당됨
            AudioHandler(audio=audio).preprocess()
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
    audio_id = request.data.get('audio_id')
    user_start_sec = request.data['start_sec']
    user_end_sec = request.data['end_sec']

    if bool(AudioSlice.objects.filter(audio_slice_id__contains=audio_id)):
        start_arr = AudioSlice.objects.values_list('start_sec', flat=True)
        start_audio_slice_id = AudioSlice.objects.get(
            start_sec=ut.find_nearest(start_arr, user_start_sec)).only('audio_slice_id')
        end_audio_slice_id = request.data.get('audio_id') + AudioSlice.objects.get(
            start_sec=ut.find_nearest(start_arr, user_end_sec)).only('audio_slice_id').split("_")[1]

    else:
        audio_handler = AudioHandler(Audio.objects.get(audio_id=audio_id))
        audio_handler.preprocess()
        start_audio_slice_id = audio_handler.get_slice_id(ut.find_nearest(audio_handler.beat_track, user_start_sec))
        end_audio_slice_id = audio_handler.get_slice_id(ut.find_nearest(audio_handler.beat_track, user_end_sec))

    interval_number = int(end_audio_slice_id.split("_")[1]) - int(start_audio_slice_id.split("_")[1])
    return Response(
        AudioSliceSerializer(start_audio_slice_id=start_audio_slice_id, end_audio_slice_id=end_audio_slice_id,
                             interval_number=interval_number).data)
