import json
import sys
from cerebras_appliance.sdk import SdkCompiler

# Instantiate copmiler
compiler = SdkCompiler()

# The full fabric dim is required when compiling for the wafer
ARGS = "--fabric-dims=757,996 --fabric-offsets=4,1 -o out --memcpy --channels 1"

# Use these for a simulator run 
#ARGS = "--fabric-dims=8,3 --fabric-offsets=4,1 -o out --memcpy --channels 1"

# Launch compile job
artifact_id = compiler.compile(
  app_path=".",
  csl_main="layout.csl",
  options=ARGS,
  out_path="."
)

# Write the artifact_id to a JSON file
with open("artifact_id.json", "w", encoding="utf8") as f:
  json.dump({"artifact_id": artifact_id,}, f)
