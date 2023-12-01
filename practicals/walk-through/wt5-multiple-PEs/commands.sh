#!/usr/bin/env bash

set -e

rm -rf out

# Fabric-dims now 9,3 for 2 PE application, rather than 8,3 for 1 PE application 
cslc layout.csl --fabric-dims=9,3 --fabric-offsets=4,1 --params=N:3,width:2 --memcpy --channels=1 -o out
cs_python run.py --name out