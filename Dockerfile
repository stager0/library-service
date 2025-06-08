FROM python:3.13.3-slim
LABEL maintainer="andriishather@gmail.com"

RUN apt-get update && apt-get install -y wget unzip

ENV PYTHONBUFFERED=1

RUN wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip && \
    unzip ngrok-v3-stable-linux-amd64.zip && \
    mv ngrok /usr/local/bin/ngrok && \
    rm ngrok-v3-stable-linux-amd64.zip

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

