FROM python:3.13.3-alpine3.21
LABEL maintainer="andriishather@gmail.com"

RUN apt-get update && apt-get install -y wget unzip

ENV PYTHONBUFFERED=1

RUN wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
RUN unzip ngrok-stable-linux-amd64.zip
RUN mv ngrok /usr/local/bin

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .
