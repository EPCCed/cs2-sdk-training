#!/usr/bin/env bash

set -e

# Delete old simulation
rm -rf out


cslc layout.csl --fabric-dims=9,3 --fabric-offsets=4,1 --params=M:4,N:6,width:2 --memcpy --channels=1 -o out
cs_python run.py --name out