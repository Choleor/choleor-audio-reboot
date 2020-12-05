from configuration import config
import youtube_dlc
from youtube_search import YoutubeSearch
from audio.celery_tas import app


def write_from_meta(info):
    try:
        return write_from_link(search_url_from_meta(info))
    except Exception as e:
        print('error', e)


def search_url_from_meta(info):
    try:
        url = "https://www.youtube.com/watch?v=" + \
              YoutubeSearch("{} audio Lyrics".format(info), max_results=1).search()[0]["id"]
        return url
    except Exception as e:
        print('error', e)


def write_from_link(download_url):
    try:
        with youtube_dlc.YoutubeDL(config.ydl_options) as ydl:
            meta = ydl.extract_info(download_url, download=True)
            if meta['formats'][0]['filesize'] > config.max_file_size:
                raise Exception("File too large")
            return meta['id'], meta['title'], meta['duration']
            # return {"audio_id": meta['id'], "title": meta['title'], "duration": meta['duration']}
    except Exception as e:
        print('error', e)


def get_video_id(download_url):
    try:
        with youtube_dlc.YoutubeDL(config.ydl_options) as ydl:
            return ydl.extract_info(download_url, download=False)['id']

    except Exception as e:
        print('error', e)


def get_video_title(download_url):
    try:
        with youtube_dlc.YoutubeDL(config.ydl_options) as ydl:
            return ydl.extract_info(download_url, download=False)['title']

    except Exception as e:
        print('error', e)


def get_video_duration(download_url):
    try:
        with youtube_dlc.YoutubeDL(config.ydl_options) as ydl:
            return ydl.extract_info(download_url, download=False)['duration']
    except Exception as e:
        print('error', e)


if __name__ == '__main__':
    print(write_from_link("https://www.youtube.com/watch?v=NNM2kEBGiRs"))
