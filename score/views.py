from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
# from .models import AudioSlice, Audio
# from .serializers import AudioSerializer
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser, MultiPartParser



@api_view(['POST'])
def avg_amplitude_list(request):
    request.data.get("start_audio_slice_id"), request.data.get("end_audio_slice_id")
    ""
    # 프로세싱
    # song = Audio.objects.all()
    # serializer = AudioSerializer(song, many=True)
    # return Response(serializer.data)
    #레디스에 삽입하렴
    return Response(0)


@api_view(['GET', 'POST'])
def similarity_score(request):
    if request.method == 'POST':
        return Response(0)
