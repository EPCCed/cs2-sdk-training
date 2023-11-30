#!/usr/bin/env cs_python
# pylint: disable=line-too-long,too-many-function-args

import argparse
import math
import json
import numpy as np

from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime # pylint: disable=no-name-in-module
from cerebras.sdk.runtime.sdkruntimepybind import MemcpyDataType, MemcpyOrder # pylint: disable=no-name-in-module

def parse_args():
  """ parse the command line """

  parser = argparse.ArgumentParser(description="single tile matvec run parameters")
  parser.add_argument("--name", required=False, default="out",
                      help="prefix of ELF files")
  parser.add_argument("--cmaddr", required=False, default="",
                      help="IP:port for CS system")
  args = parser.parse_args()
  return args


def main():
  """Main method to run the example code."""

  args = parse_args()

  name = args.name
  cmaddr = args.cmaddr

  # Parse the compile metadata
  with open(f"{name}/out.json", encoding="utf-8") as json_file:
    compile_data = json.load(json_file)

  nb = int(compile_data["params"]["tile_size"])
  width = int(compile_data["params"]["width"])
  height = int(compile_data["params"]["height"])
  iters = int(compile_data["params"]["iters"])


  # Calculate alignment and padding to avoid bank conflicts
  align = 16
  multiple = int(align/4)
  padded_nb = math.ceil(nb/multiple)*multiple


  #############
  # Run
  #############

  # Instantiate runner
  runner = SdkRuntime(name, cmaddr=cmaddr)

  # Device symbols for memcpy
  A_symbol = runner.get_id("A")
  x_symbol = runner.get_id("x")
  y_symbol = runner.get_id("y")
  # Load and begin run
  runner.load()
  runner.run()

  # Construct A data and copy random A matrix PE (0,0) for verification
  A_mat = np.random.rand(nb, nb)
  A_data = np.zeros(width*height*(nb*padded_nb+1), dtype=np.float32)

  for w in range(width):
    for h in range(height):
      for i in range(nb):
        for j in range(nb):
          A_data[(h*width + w)*(nb*padded_nb+1) + j*padded_nb + i + 1] = A_mat[i, j]

  print()
  print("Beginning run.")
  print("Copy A matrices to device...")
  runner.memcpy_h2d(A_symbol, A_data, 0, 0, width, height, nb*padded_nb+1,
    streaming=False, data_type=MemcpyDataType.MEMCPY_32BIT, order=MemcpyOrder.ROW_MAJOR, nonblock=False)

  # Construct x data and copy random x vector to PE (0,0) for verification
  x_vec = np.random.rand(nb)
  x_data = np.zeros(width*height*nb, dtype=np.float32)
  for w in range(width):
    for h in range(height):
      x_data[(h*width + w)*nb:(h*width + w)*nb+nb] = x_vec


  print("Copy x vectors to device...")
  runner.memcpy_h2d(x_symbol, x_data, 0, 0, width, height, nb,
    streaming=False, data_type=MemcpyDataType.MEMCPY_32BIT, order=MemcpyOrder.ROW_MAJOR, nonblock=False)

  # Launch the compute kernel
  print("Launch kernel...")
  runner.call("compute", [], nonblock=False)


  print("Done.")





if __name__ == "__main__":
  main()