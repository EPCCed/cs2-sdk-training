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
M = 4
N = 6

# Construct A, x, b
A = np.arange(M*N, dtype=np.float32)
x = np.full(shape=N, fill_value=1.0, dtype=np.float32)
b = np.full(shape=M, fill_value=2.0, dtype=np.float32)

# Calculate expected y
y_expected = A.reshape(M,N)@x + b

# Construct a runner using SdkRuntime
runner = SdkRuntime(args.name, cmaddr=args.cmaddr)

# Get symbols for A, b, x, y on device
A_symbol = runner.get_id('A')
x_symbol = runner.get_id('x')
b_symbol = runner.get_id('b')
y_symbol = runner.get_id('y')

# Load and run the program
runner.load()
runner.run()

runner.memcpy_h2d(A_symbol, A, 0, 0, 1, 1, M*N, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
###### TO DO 1: ######
# Copy x and b symbols to the device
# x is of size N and b is of size M
# Hint: Use runner.memcpy_h2d(...)

# Launch the init_and_compute function on device
runner.launch('init_and_compute', nonblock=False)

y_result = np.zeros([M], dtype=np.float32)

###### TO DO 2: ######
# Copy y back from device to y_result
# Hint: Use runner.memcpy_d2h(...) such as
# runner.memcpy_d2h(VARIABLE, SYMBOL, 0, 0, 1, 1, SIZE, streaming=False,
#   order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
# Where VARIABLE is the python variable, SYMBOL is the symbol on the CS-2 and 
# SIZE is the size of the data (number of elements)

# Stop the program
runner.stop()

# Ensure that the result matches our expectation
np.testing.assert_allclose(y_result, y_expected, atol=0.01, rtol=0)
print("SUCCESS!")
