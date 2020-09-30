import os
from utils.utils import get_console_output


def get_duration(filename, ext, in_path):
    return float(get_console_output(
        "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {}/{}.{}".format(
            in_path, filename, ext)))


if __name__ == '__main__':
    print(get_duration("J3d5OkPxER4", "wav", "../../media"))
    # print(get_console_output("youtube-dl --audio-format wav"))                  #error
