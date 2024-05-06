# RUNNING

Launch by doing `sbatch submit.sh`. Do not run `./commands.sh` directly.

# Walk through 3: Memcpy on Wafer


How do we copy data in and out of the WSE from our host?

* We need our layout file (`layout.csl`)to export the symbol names for x and y.
* We need our PE program (`pe_program.csl`)to export pointers to x and y. 

The PE program no longer needs to initialize these tensors.

In `layout.csl`:
```
// Import memcpy layout module for 1 x 1 grid of PEs
// This module defines parameters passed to program on the single PE
const memcpy = @import_module("<memcpy/get_params>", .{
  .width = 1,
  .height = 1,
  .LAUNCH = LAUNCH
});

// Export device symbol for array "x", "y"
// Last argument is mutability: host can read and write x, y
@export_name("x", [*]f32, true);
@export_name("y", [*]f32, true);
```
At the very top of this file is an `@import_module` call, which imports the top-level memcpy infrastructure. This module import requires width and height parameters which correspond to the dimensions of the program rectangle. This program only uses a single PE, so width and height are both 1. Additionally, this module import takes all colors used by the memcpy infrastructure on all PEs. In particular, we declare a color named `LAUNCH`, and pass it as a parameter to memcpy. We do not directly use this color or assign any routing to it. Instead, it is used by memcpy to route and launch our device kernel.

Module imports in CSL act like unique struct types. Thus, the code in the CSL standard library file `memcpy/get_params` can be used like a struct named `memcpy`.

`@export_name` makes symbol names visible to the host program.

In `pe_program.csl`:
```
comptime {
  // Export symbol pointing to y so it is host-readable
  @export_symbol(x_ptr, "x");
  @export_symbol(y_ptr, "y");

  // Export function so it is host-callable by RPC mechanism
  @export_symbol(compute);

  // Create RPC server using color LAUNCH
  @rpc(@get_data_task_id(sys_mod.LAUNCH));
}
```
The pointers `x_ptr` and `y_ptr` to `x` and `y` are exported with `@export_symbol`, so that they will be visible to the host.

In `run.py`, we can use the `runner.memcpy_h2d` and `runner.memcpy_d2h` calls to copy data to and from the device:
``` Python
runner.memcpy_h2d(x_symbol, x, 0, 0, 1, 1, N, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
runner.memcpy_h2d(y_symbol, y, 0, 0, 1, 1, N, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
  ...
runner.memcpy_d2h(y_result, y_symbol, 0, 0, 1, 1, N, streaming=False,
  order=MemcpyOrder.ROW_MAJOR, data_type=MemcpyDataType.MEMCPY_32BIT, nonblock=False)
```

Last, note that flag specifying memcpy and channels. Every program using memcpy must include the --memcpy flag. The channels flag determines the max throughput for transferring data on and off the wafer. Its value can be no larger than the width of the program rectangle, and maxes out at 16. Typically, performance improvements are minimal past 8 channels.

In `commands.sh`:

```
cslc ./layout.csl --fabric-dims=8,3 \
--fabric-offsets=4,1 -o out --memcpy --channels 1
cs_python run.py --name out
```

## Remote Procedure Calls (RPC)

So far we have been launching the device kernel using the Remote Procedure Calls mechanism:

```  Python
# Launch the init_and_compute function on device
runner.launch('compute', nonblock=False)
```

