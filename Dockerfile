FROM python:3.10-bullseye

WORKDIR /tmp
RUN wget https://github.com/hivemq/mqtt-cli/releases/download/v4.15.0/mqtt-cli-4.15.0.deb
RUN apt-get update && apt-get install -y /tmp/mqtt-cli-4.15.0.deb


WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt