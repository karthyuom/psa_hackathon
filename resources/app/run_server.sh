#!/bin/bash

set -e -u

function die { echo $1; exit 42; }

VIDEO_STREAM_PORT=5001
MOTOR_CTRL_PORT=5002

cd $(dirname $0)
trap 'kill $(jobs -p)' EXIT

SERVERL_LOG='incubator.server.log'
printf "Server: Logging to '%s'\n\n" $SERVERL_LOG

#python2 -m SimpleHTTPServer $VIDEO_STREAM_PORT &> /dev/null &
# python video_server.py --port $VIDEO_STREAM_PORT  &> /dev/null &
python control_server.py --port $MOTOR_CTRL_PORT  2>&1 | tee  $SERVERL_LOG &
# cd ../../ # Root OpenFace directory.
# ./demos/web/websocket-server.py --port $MOTOR_CTRL_PORT 2>&1 | tee $SERVERL_LOG &

wait
