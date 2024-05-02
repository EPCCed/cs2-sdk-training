#!/usr/bin/env bash

set -e
source ../../general/setup_env_epcc.sh

rm -rf out

cslc layout.csl --fabric-dims=11,3 --fabric-offsets=4,1 --params=N:3,width:2 --memcpy --channels=1 -o out
cs_python run.py --name out
