#!/usr/bin/env cs_python

import argparse
import numpy as np

from cerebras.sdk.runtime.sdkruntimepybind import SdkRuntime, MemcpyDataType, MemcpyOrder # pylint: disable=no-name-in-module

# Read arguments
parser = argparse.ArgumentParser()
parser.add_argument('--name', help="the test compile output dir")
parser.add_argument('--cmaddr', help="IP:port for CS system")
args = parser.parse_args()

# Matrix dimensions
N = 3


# Construct a runner using SdkRuntime
runner = SdkRuntime(args.name, cmaddr=args.cmaddr)

# Get symbol for copying y result off device
x_symbol = runner.get_id('x')
y_symbol = runner.get_id('y')

# Load and run the program
runner.load()
runner.run()


# Copy y to device
y = np.full(shape=N, fill_value=1.0, dtype=np.float32)
x = np.full(shape=N, fill_value=1.0, dtype=np.float32)
runner.memcpy_h2d(x_symbol, x, 0, 0, 1, 1, N, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
runner.memcpy_h2d(y_symbol, y, 0, 0, 1, 1, N, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)


# Launch the init_and_compute function on device
runner.launch('compute', nonblock=False)

# Copy y back from device
# Arguments to memcpy_d2h:
# - y_result is array on host which will story copied-back array
# - y_symbol is symbol of device tensor to be copied
# - 0, 0, 1, 1 are (starting x-coord, starting y-coord, width, height)
#   of rectangle of PEs whose data is to be copied
# - N is number of elements to be copied from each PE
y_result = np.zeros([N], dtype=np.float32)
runner.memcpy_d2h(y_result, y_symbol, 0, 0, 1, 1, N, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)

# Stop the program
runner.stop()

expected_y = y + 2*x

# Ensure that the result matches our expectation
np.testing.assert_allclose(y_result, expected_y, atol=0.01, rtol=0)
print("SUCCESS!")
