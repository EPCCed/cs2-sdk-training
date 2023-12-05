#!/usr/bin/env bash

set -e

# Delete old simulation
rm -rf out

# Compile
cslc ./layout.csl --fabric-dims=8,3 \
--fabric-offsets=4,1 -o out --memcpy --channels 1

# Run Simulation
cs_python run.py --name out