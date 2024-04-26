# Walk through 7: Collective Communications (Advanced)

The aim of this walk-through is to demonstrate some functionalities in the `collective_2d` library, which provides (mpi-like) collective communication directives between PEs. Documentation can be found https://sdk.cerebras.net/csl/language/libraries#collectives-2d. 

The library consists of two modules:
1. `<collectives_2d/params>`: Imported once to parameterize each PE in the layout block.
1. `<collectives_2d/pe>`: Imported once per dimension per PE. Contains collective communication directives for a single axis.

## `<collectives_2d/params>`
In `layout.csl`, the `get_params` function (from `<collectives_2d/params>`) is used to configure the PE's communication:

```
const c2d = @import_module("<collectives_2d/params>");
...
const params = c2d.get_params(Px, Py, .{
        .x_colors      = .{ c2d_x_color_0,   c2d_x_color_1 },
        .x_entrypoints = .{ c2d_x_entrypt_0, c2d_x_entrypt_1 },
        .y_colors      = .{ c2d_y_color_0,   c2d_y_color_1 },
        .y_entrypoints = .{ c2d_y_entrypt_0, c2d_y_entrypt_1 },
      });
```

Here `Px` and `Py` are the PE's x- and y- coordinates, and the `comptime_struct` following contains the required colors and local task IDs required to set up the communication.


## `<collectives_2d/pe>`

Within the `pe_program.csl`, the user can configure the resources of `collectives_2d`. Each imported module must be assigned queue IDs (queues) and DSR IDs (dest_dsr_ids, src0_dsr_ids, src1_dsr_ids). If the user does not specify these parameters explicitly, the default values apply. 

```
const mpi_x = @import_module("<collectives_2d/pe>", .{
    .dim_params = c2d_params.x,
    .queues = [2]u16{2,4},
    .dest_dsr_ids = [1]u16{1},
    .src0_dsr_ids = [1]u16{1},
    .src1_dsr_ids = [1]u16{1}
    });
const mpi_y = @import_module("<collectives_2d/pe>", .{
    .dim_params = c2d_params.y,
    .queues = [2]u16{3,5},
    .dest_dsr_ids = [1]u16{2},
    .src0_dsr_ids = [1]u16{2},
    .src1_dsr_ids = [1]u16{2}
    });
```

Before any collective directives are called, the `init()` function must first be called once (for each axis).

Four directives are currently supported:
```
fn init() void
fn broadcast(root: u16, buf: [*]u32, count: u16, callback: local_task_id) void
fn scatter(root: u16, send_buf: [*]u32, recv_buf: [*]u32, count: u16, callback: local_task_id) void
fn gather(root: u16, send_buf: [*]u32, recv_buf: [*]u32, count: u16, callback: local_task_id) void
fn reduce_fadds(root: u16, send_buf: [*]f32, recv_buf: [*]f32, count: u16, callback: local_task_id) void
```
See documentation https://sdk.cerebras.net/csl/language/libraries#collectives-2d for more details. 

This example showcases each of the currently available communication primitives while using the library across two indepedent dimensions. The communication tasks are executed asynchronously.

`task_x` uses the `broadcast` primitive to transmit data from the first PE in every row to every other PE in the same row. After the data is received, `reduce_fadds` computes the vector sum of the `broadcast_recv`. The result is transmitted back to the first PE in every row.

`task_y` operates concurrently along every column of PEs. The task first uses `scatter` to distribute `chunk_size` slices of `scatter_data` across every other PE in the same column. The task uses `gather` to collect `chunk_size` slices of data distributed by `scatter`. Because `scatter` is the inversion of `gather`, we have used collective communications to transmit the data from `scatter_data` to `gather_recv`.