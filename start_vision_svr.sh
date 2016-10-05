#!/bin/bash

ENABLE_ANNOTATION=0
if [ $# -gt 0 ]; then
  ENABLE_ANNOTATION=$1
fi

## Vision server communication ##
VISION_HOST_IP=127.0.0.1
VISION_HOST_PORT=8888

## Robot communication ##
ROBOT_COM_IP=172.20.10.3
ROBOT_COM_PORT=5002

## AWS Server communication ##
AWS_COM_SVR_IP=52.220.132.34
AWS_COM_SVR_PORT=443

SERVER_LOG='vision_svr.log'

printf "Server starting... [ENABLE_ANNOTATION=%s]\n\n" $ENABLE_ANNOTATION
printf "Server logging to '%s'\n\n" $SERVER_LOG

python vision_main.py -vision_host_ip $VISION_HOST_IP -vision_host_port $VISION_HOST_PORT -robot_com_ip $ROBOT_COM_IP -robot_com_port $ROBOT_COM_PORT -aws_com_ip $AWS_COM_SVR_IP -aws_com_port $AWS_COM_SVR_PORT --enable-annotation $ENABLE_ANNOTATION  2>&1 | tee  $SERVER_LOG &

wait
