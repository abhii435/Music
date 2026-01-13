FROM python:3.10-slim-buster

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y ffmpeg opus-tools python3-pip

WORKDIR /app
COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "bot.py"]
