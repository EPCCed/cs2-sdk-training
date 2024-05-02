#!/usr/bin/env bash

set -e
source ../../general/setup_env_epcc.sh

# Delete old simulation
rm -rf out


cslc layout.csl --fabric-dims=9,3 --fabric-offsets=4,1 --params=M:4,N:6 --memcpy --channels=1 -o out
cs_python run.py --name out
