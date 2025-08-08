from flask import Flask, request, render_template
import threading
import queue
import time
from config import THREAD_POOL_SIZE

from playlist_downloader import download_playlist

app = Flask(__name__)
download_queue = queue.Queue()


def worker():
    while True:
        url = download_queue.get()
        if url is None:
            break
        try:
            download_playlist(url)
        finally:
            download_queue.task_done()

# Start thread pool
threads = []
for _ in range(THREAD_POOL_SIZE):
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    threads.append(t)

@app.route('/', methods=['GET', 'POST'])
def index():
    msg = ''
    if request.method == 'POST':
        url = request.form['url']
        download_queue.put(url)
        msg = f"Added to queue: {url}"
    return render_template('index.html', result=msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)

