#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
MOUNTFROM=$PWD
MOUNTTO='/home/morpheus/workspace/mount'
IMAGE='rsbyrne/aircleaning'
SOCK='/var/run/docker.sock'
echo "starting imdo"
docker run -v $MOUNTFROM:$MOUNTTO -v $SOCK:$SOCK -i --shm-size 2g $IMAGE $* &>> cron.log
echo "finished imdo"
docker container prune -f
#rm $(docker ps -a -q)
cd $currentDir
