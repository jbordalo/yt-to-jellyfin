from yt_dlp import YoutubeDL
import os
from nfo.NFO import VideoNFOWriter
from config import *
from datetime import datetime
import hashlib

DEBUG = False


def download_playlist(url):
    archive_name = str(hashlib.sha256(url.encode()).hexdigest()[:16]) + ".txt"

    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'merge_output_format': 'mp4',
        'outtmpl': f"{DOWNLOAD_DIR or '.'}/%(playlist_title)s/%(title)s.%(ext)s",
        'continue_dl': True,
        'nooverwrites': True,
        'ignoreerrors': True,
        'download_archive': archive_name,
        'writethumbnail': True,
        'quiet': not DEBUG,
        #'playlist_items': '1-2',
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            # extract metadata
            info = ydl.extract_info(url, download=False)

            title = info.get('title')

            nfo_writer = VideoNFOWriter(title, base_path=DOWNLOAD_DIR)

            for video in info.get('entries', []):
                video_title = video.get('title')
                video_description = video.get('description')
                upload_date = video.get('upload_date')
                upload_date = datetime.strptime(upload_date, "%Y%m%d").strftime("%Y-%m-%d")

                nfo_writer.add_episode(video_title, video_description, upload_date)

            nfo_writer.write()
            os.remove(archive_name)
            os.rename(os.path.join(DOWNLOAD_DIR, title, f"{title}.jpg"), os.path.join(DOWNLOAD_DIR, title, "poster.jpg"))
        except FileNotFoundError:
            print("No archive file to delete")
        except Exception as e:
            print(e)

if __name__ == "__main__":
    URL = "https://www.youtube.com/watch?v=hdCBGWcd4qw&list=PL2FEB728FF960FBD9"

    download_playlist(URL)
