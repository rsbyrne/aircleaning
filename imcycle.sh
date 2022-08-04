#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
echo "imcycle start"
bash ./pull.sh
bash ./preconfig.sh
# sudo bash everestupdate.sh
python3 update.py
bash ./push.sh
echo "imcycle done"
cd $currentDir
