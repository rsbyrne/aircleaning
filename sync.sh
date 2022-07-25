#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
./pull.sh
./push.sh
cd $currentDir
