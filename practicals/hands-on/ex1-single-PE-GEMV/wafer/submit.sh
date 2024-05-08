#!/bin/bash
#SBATCH --cpus-per-task=1         # Request 1 core
#SBATCH --time=00:30:00           # Set time limit for this job to 30 minutes
#SBATCH --gres=cs:1               # Request CS-2 system
#SBATCH --signal=TERM@30

./commands.sh
