FROM python:3.10-slim

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt
RUN apt-get -y update
RUN apt-get install -y ffmpeg

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
