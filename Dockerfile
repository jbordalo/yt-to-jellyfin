FROM python:3.11-slim

RUN apt update && apt install -y ffmpeg

RUN pip install yt-dlp flask

COPY . .

CMD ["python", "app.py"]
