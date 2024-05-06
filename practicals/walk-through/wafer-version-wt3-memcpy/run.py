import numpy as np
import json

from cerebras_appliance.pb.sdk.sdk_common_pb2 import MemcpyDataType, MemcpyOrder
from cerebras_appliance.sdk import SdkRuntime


# Array size
N = 3

# Read the artifact_path from the JSON file
with open("artifact_id.json", "r", encoding="utf8") as f:
    data = json.load(f)
    artifact_path = data["artifact_id"]


# Instantiate a runner object using a context manager.
# Set simulator=False if running on CS system within appliance.
with SdkRuntime(artifact_path, simulator=False) as runner:
    # Get symbol for copying x, y onto and off device
    x_symbol = runner.get_id('x')
    y_symbol = runner.get_id('y')

    # Copy x and y to device
    # Arguments to memcpy_h2d:
    # - x_symbol is symbol of device tensor to receive
    # - x is the array on host to be sent to device
    # - 0, 0, 1, 1 are (starting x-coord, starting y-coord, width, height)
    #   of rectangle of PEs whose data is to be copied
    # - N is number of elements to be copied from each PE
    y = np.full(shape=N, fill_value=1.0, dtype=np.float32)
    x = np.full(shape=N, fill_value=1.0, dtype=np.float32)
    runner.memcpy_h2d(x_symbol, x, 0, 0, 1, 1, N, streaming=False,
      order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
    runner.memcpy_h2d(y_symbol, y, 0, 0, 1, 1, N, streaming=False,
      order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)

    # Launch the compute function on device
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

# Calculate expected result
expected_y = y + 2.0*x

# Ensure that the result matches our expectation
np.testing.assert_allclose(y_result, expected_y, atol=0.01, rtol=0)
print("SUCCESS!")
