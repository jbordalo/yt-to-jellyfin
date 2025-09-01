from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename
import os
from nfo.NFO import VideoNFOWriter
from config import *
from datetime import datetime
import hashlib
from tqdm import tqdm

DEBUG = False
METADATA_ONLY=False

# from gpt
pbar = None
def progress_hook(d):
    global pbar
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        if pbar is None:
            pbar = tqdm(total=total, unit='B', unit_scale=True, desc=d.get('filename'))
        downloaded = d.get('downloaded_bytes', 0)
        pbar.n = downloaded
        pbar.refresh()
    elif d['status'] == 'finished':
        if pbar is not None:
            pbar.close()
            print(f"✅ Finished {d['filename']}")
            pbar = None


def download_playlist(url):
    archive_name = str(hashlib.sha256(url.encode()).hexdigest()[:16]) + ".txt"

    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        'merge_output_format': 'mp4',
		'progress_hooks': [progress_hook],
		'verbose': DEBUG, 
        'outtmpl': f"{DOWNLOAD_DIR or '.'}/%(playlist_title)s/dload-%(autonumber)03d.%(ext)s",
        #'extractor_args': {
        #    'youtube': {
        #        'player_client': ['web']
        #    }
        #},
        'continue_dl': True,
        'nooverwrites': True,
        'ignoreerrors': 'only_downloads',
        'download_archive': archive_name,
        'writethumbnail': True,
        'restrictfilenames': True,
        #'quiet': not DEBUG,
        #'playlist_items': '1-2',
        # try to improve robustness (gpt suggestion)
        'retries': 5,
        'fragment_retries': 5,
        'skip_unavailable_fragments': True,
        'concurrent_fragment_downloads': 5,
        'cookies': 'cookies.txt',
        #'http_headers': {
        #    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        #    },
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            # extract metadata
            info = ydl.extract_info(url, download=not METADATA_ONLY)

            title = info.get('title')

            nfo_writer = VideoNFOWriter(title, base_path=DOWNLOAD_DIR)

            for video in info.get('entries', []):
                # yt-dlp adds None entries for unavailable videos :)
                if not video: continue

                video_title = video.get('title')
                video_description = video.get('description')
                upload_date = video.get('upload_date')
                upload_date = datetime.strptime(upload_date, "%Y%m%d").strftime("%Y-%m-%d")

                nfo_writer.add_episode(video_title, video_description, upload_date)

            nfo_writer.write()

            try:
                os.remove(archive_name)
            except FileNotFoundError:
                print("No archive file to delete.")

            os.rename(os.path.join(DOWNLOAD_DIR, sanitize_filename(title, restricted=True), "dload-000.jpg"), os.path.join(DOWNLOAD_DIR, sanitize_filename(title, restricted=True), "poster.jpg"))
        except Exception as e:
            print("Something unexpected went wrong")
            print(e)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("No URL provided")
        exit(1)

    url = sys.argv[1]

    if len(sys.argv) > 2:
        METADATA_ONLY = True

    print(f"Downloading {url}")
    print(f"Metadata only: {METADATA_ONLY}")

    download_playlist(url)
