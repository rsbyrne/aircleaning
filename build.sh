#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
#sh push.sh
docker build -t rsbyrne/aircleaning:latest .
docker push rsbyrne/aircleaning:latest
cd $currentDir
