#!/usr/bin/env bash

set -e
source ../../general/setup_env_epcc.sh

# Delete old simulation
rm -rf out

# Compile
cslc ./layout.csl --fabric-dims=8,3 \
--fabric-offsets=4,1 -o out --params=N:3 --memcpy --channels 1

# Run Simulation
cs_python run.py --name out
