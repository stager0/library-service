#!/bin/sh
set -e

ngrok http library_service:8100 --log=stdout &
NGROK_PID=$!

echo "ngrok script: Waiting for start of the tunnel..."

NGROK_URL=""
while [ -z "$NGROK_URL" ] || [ "$NGROK_URL" = "null" ]; do
  sleep 1
  NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
done

WEBHOOK_URL="${NGROK_URL}/api/webhook/"

mkdir -p /ngrok-data
echo "${WEBHOOK_URL}" > /ngrok-data/webhook_url.txt

echo "---"
echo "ngrok script: URL (${WEBHOOK_URL}) wrote in common volume."
echo "ngrok script: The service is available at the address: ${NGROK_URL}"
echo "---"

wait $NGROK_PID