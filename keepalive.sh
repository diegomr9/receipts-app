#!/bin/bash
# Keeps the app (port 8000) and the ngrok tunnel (https://frostlike-glutton-backer.ngrok-free.dev) running.
# ngrok auth comes from ~/.config/ngrok/ngrok.yml (configured from NGROK_AUTHTOKEN).
cd "$(dirname "$0")"
while true; do
  if ! curl -s -o /dev/null -m 5 http://localhost:8000/login; then
    pkill -f "venv/bin/python app.py"; sleep 1
    nohup venv/bin/python app.py >> app.log 2>&1 &
    echo "$(date) restarted app" >> keepalive.log; sleep 3
  fi
  if ! pgrep -f "ngrok http" >/dev/null || ! curl -s -m 5 localhost:4040/api/tunnels | grep -q "frostlike-glutton-backer.ngrok-free.dev"; then
    pkill -f "ngrok http"; sleep 1
    nohup ./ngrok http 8000 --url https://frostlike-glutton-backer.ngrok-free.dev --log stdout --log-format logfmt >> ngrok.log 2>&1 < /dev/null &
    echo "https://frostlike-glutton-backer.ngrok-free.dev" > PUBLIC_URL.txt; echo "$(date) restarted ngrok" >> keepalive.log; sleep 10
  fi
  sleep 20
done
