#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
echo "imcycle start"
# bash ./pull.sh
# bash ./preconfig.sh
abort()
{
    echo >&2 '
***************
*** ABORTED ***
***************
'
    git reset --hard
    echo "An error occurred. Exiting..." >&2
    exit 1
}
trap 'abort' 0
set -e
# sudo bash everestupdate.sh
python3 -m aircleaning
trap : 0

echo >&2 '
************
*** DONE *** 
************
'
# bash ./push.sh
echo "imcycle done"
cd $currentDir
