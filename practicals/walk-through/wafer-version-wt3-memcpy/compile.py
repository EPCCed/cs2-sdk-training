import json
import sys
from cerebras_appliance.sdk import SdkCompiler

# Instantiate copmiler
compiler = SdkCompiler()

# Same arguments as for cslc before
ARGS = "--fabric-dims=8,3 --fabric-offsets=4,1 -o out --memcpy --channels 1"

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
