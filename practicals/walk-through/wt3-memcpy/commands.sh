#!/usr/bin/env bash

set -e

rm -r out

cslc ./layout.csl --fabric-dims=8,3 \
--fabric-offsets=4,1 -o out --memcpy --channels 1
cs_python run.py --name out