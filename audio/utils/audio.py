from configuration.config import LF_ORG, LF_WAV
from audio.utils.utils import get_console_output as to_console


def calculate_duration_with_file(filepath, ext="wav"):
    to_console(
        "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {}.{}".format(filepath,
                                                                                                             ext))

# def handle_uploaded_file(file, file_name, extension="wav", path=LF_WAV):
#     with open('{}{}.{}'.format(path, file_name, extension), 'wb+') as destination:
#         for chunk in file.chunks():
#             destination.write(chunk)
#     if extension != "wav":
#         to_console("ffmpeg -i {}{}.{} -o {}{}.wav".format(path, file_name, extension, LF_WAV, file_name))
#
#
