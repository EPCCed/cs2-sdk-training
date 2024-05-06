#!/usr/bin/env bash

set -e

# activate python venv created as described here:
# https://epcced.github.io/eidf-docs/services/cs2/run/
source /home/eidf132/eidf132/shared/cs2_tutorial/venv_cerebras_pt/bin/activate

python compile.py

python run.py
