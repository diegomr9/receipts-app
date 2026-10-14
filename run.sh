#!/bin/sh
cd "$(dirname "$0")"
pgrep -f keepalive.sh >/dev/null || nohup ./keepalive.sh >/dev/null 2>&1 &
sleep 15; cat PUBLIC_URL.txt
