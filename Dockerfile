FROM python:3.10-slim-buster

[span_1](start_span)RUN apt-get update && apt-get install -y ffmpeg opus-tools python3-pip[span_1](end_span)
WORKDIR /app
COPY . .
[span_2](start_span)RUN pip3 install --no-cache-dir -r requirements.txt[span_2](end_span)

CMD ["python3", "bot.py"]
