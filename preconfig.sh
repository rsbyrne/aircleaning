#!/bin/bash
currentDir=$PWD
cd "$(dirname "$0")"
pip3 install adjustText
cd $currentDir
