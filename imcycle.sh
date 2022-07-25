#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
echo "imcycle start"
# sudo bash everestupdate.sh
python3 update.py
bash ./push.sh
echo "imcycle done"
cd $currentDir
