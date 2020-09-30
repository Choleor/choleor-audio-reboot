import config
import youtube_dl


def write_from_meta(title, artist):
    try:
        with youtube_dl.YoutubeDL(config.ydl_options) as ydl:
            search_info = ydl.extract_info("ytsearch1:{} - {} Official audio Lyrics".format(title, artist))
            return write_from_link(search_info['entries'][0]['webpage_url'])
            # return search_info['entries'][0]['id'], search_info['entries'][0]['title'], search_info['entries'][0][
            #     'webpage_url']
    except Exception as e:
        print('error', e)


def write_from_link(download_url):
    try:
        with youtube_dl.YoutubeDL(config.ydl_options) as ydl:
            meta = ydl.extract_info(download_url, download=True)
            if meta['formats'][0]['filesize'] > config.max_file_size:
                # print(meta['formats'][0]['filesize'])
                raise Exception("File too large")
            return meta['id'], meta['title'], meta['duration']
    except Exception as e:
        print('error', e)


def get_video_id(download_url):
    try:
        with youtube_dl.YoutubeDL(config.ydl_options) as ydl:
            return ydl.extract_info(download_url, download=False)['id']

    except Exception as e:
        print('error', e)


def get_video_title(download_url):
    try:
        with youtube_dl.YoutubeDL(config.ydl_options) as ydl:
            return ydl.extract_info(download_url, download=False)['title']

    except Exception as e:
        print('error', e)


def get_duration(download_url):
    try:
        with youtube_dl.YoutubeDL(config.ydl_options) as ydl:
            return ydl.extract_info(download_url, download=False)['duration']

    except Exception as e:
        print('error', e)


if __name__ == '__main__':
    # id, title, duration = write_from_link("https://www.youtube.com/watch?v=8WOawEvEGWc")
    # print(id, title, duration)
    id, title, duration = write_from_meta("NASA", "Ariana Grande")
    print(id, title, duration)
    # print(get_video_id("https://www.youtube.com/watch?v=pSQk-4fddDI"))
    # print(get_video_title("https://www.youtube.com/watch?v=pSQk-4fddDI"))
    # print(get_duration("https://www.youtube.com/watch?v=pSQk-4fddDI"))
    # print(write_from_link("https://www.youtube.com/watch?v=EyLf7XuwpFw"))
