#! /bin/bash

HOST=`hostname -s`
DIRECTORY=`dirname $0`
cd ${DIRECTORY}
export PYTHONPATH=${DIRECTORY}

if [ $HOST = "raspberrypi" ]; then
  echo $HOST
  python3 ${DIRECTORY}/surveillance/SurveillanceService.py &
fi