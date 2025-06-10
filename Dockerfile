FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends curl jq wget unzip && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip -O ngrok.zip && \
    unzip ngrok.zip && \
    mv ngrok /usr/local/bin/ngrok && \
    rm ngrok.zip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start-ngrok.sh
RUN chmod +x entrypoint.sh

CMD ["python", "/app/telegram_bot/set_webhook.py"]