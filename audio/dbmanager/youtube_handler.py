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
    search_res = YoutubeSearch(f"{info} lyrics audio" if "remix" not in info else info, max_results=3).search()
    for i in search_res:
        if "M/V" not in i["id"] or "Music Video" not in i["id"]:
            return "https://www.youtube.com/watch?v=" + i["id"]


def write_from_link(download_url):
    try:
        with youtube_dlc.YoutubeDL(config.ydl_options) as ydl:
            meta = ydl.extract_info(download_url, download=True)
            return meta['id'], meta['title'], meta['duration']
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
    # print(write_from_link("https://www.youtube.com/watch?v=DKpfWL0THsg&t=2s"))
    print(write_from_link("https://www.youtube.com/watch?v=A0vq3jLAoQg"))
    # print(search_url_from_meta("moves like jagger"))
    # print(search_url_from_meta("beyonce"))
    # print(search_url_from_meta("청하 - snapping"))
    # print("https://www.youtube.com/watch?v="+YoutubeSearch("Rain on me - Lady gaga", max_results=1).search()[0]["id"])
    # print(write_from_link("http://www.youtube.com/watch?v=M3ctXZBingM"))