#!/bin/bash

while :; do
    inotifywait -e modify ./pybot.py &>/dev/null
    ps -o pid,command -ax | grep '[p]ybot.py' | awk '$0=$1' | xargs kill
    echo "Stopped"
done
