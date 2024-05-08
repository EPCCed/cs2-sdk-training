import numpy as np
import json

from cerebras_appliance.pb.sdk.sdk_common_pb2 import MemcpyDataType, MemcpyOrder
from cerebras_appliance.sdk import SdkRuntime

# Matrix dimensions
M = 4
N = 6

# Construct A, x, b
A = np.arange(M*N, dtype=np.float32)
x = np.full(shape=N, fill_value=1.0, dtype=np.float32)
b = np.full(shape=M, fill_value=2.0, dtype=np.float32)

# Calculate expected y
y_expected = A.reshape(M,N)@x + b

# Read the artifact_path from the JSON file
with open("artifact_id.json", "r", encoding="utf8") as f:
    data = json.load(f)
    artifact_path = data["artifact_id"]


# Instantiate a runner object using a context manager.
# Set simulator=False if running on CS system within appliance.
with SdkRuntime(artifact_path, simulator=False) as runner:
    # Get symbols for A, b, x, y on device
    A_symbol = runner.get_id('A')
    x_symbol = runner.get_id('x')
    b_symbol = runner.get_id('b')
    y_symbol = runner.get_id('y')

    # Copy A, x, b to device
    runner.memcpy_h2d(A_symbol, A, 0, 0, 1, 1, M*N, streaming=False,
      order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
    runner.memcpy_h2d(x_symbol, x, 0, 0, 1, 1, N, streaming=False,
      order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
    runner.memcpy_h2d(b_symbol, b, 0, 0, 1, 1, M, streaming=False,
      order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)

    # Launch the compute function on device
    runner.launch('init_and_compute', nonblock=False)

   # Copy y back from device
   y_result = np.zeros([M], dtype=np.float32)
  runner.memcpy_d2h(y_result, y_symbol, 0, 0, 1, 1, M, streaming=False,
    order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)

# Calculate expected result
expected_y = y + 2.0*x

print(y_expected)
# Ensure that the result matches our expectation
np.testing.assert_allclose(y_result, y_expected, atol=0.01, rtol=0)
print("SUCCESS!")
