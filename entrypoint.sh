#!/bin/sh
set -e

echo "Entrypoint: Waiting for the URL from ngrok..."
while [ ! -f /ngrok-data/webhook_url.txt ]; do
  sleep 2
done

export WEBHOOK_URL=$(cat /ngrok-data/webhook_url.txt)
TEMP_URL=${WEBHOOK_URL#https://}
export WEBHOOK_WITHOUT_PROTOCOL_AND_PATH=${TEMP_URL%/api/webhook/}

echo "--- Entrypoint: Checking variables ---"
echo "WEBHOOK_URL is: $WEBHOOK_URL"
echo "WEBHOOK_HOST is: $WEBHOOK_WITHOUT_PROTOCOL_AND_PATH"
echo "--- The end of the checking ---"

if [ "$1" = "python" ] && [ "$2" = "manage.py" ] && [ "$3" = "runserver" ]; then
    echo "Execution of migration..."
    python manage.py migrate
    python /app/telegram_bot/set_webhook.py

fi

exec "$@"