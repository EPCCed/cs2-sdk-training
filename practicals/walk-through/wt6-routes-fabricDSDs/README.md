# Walk through 6: Routes & Fabric DSDs

In this walk-through we will split our AXPY operation into two parts:

* `v = a*x` will be performed on the left PE, and this result `v` will be transfered to the right PE, then
* `y = y + v` will be summed on the right PE

This requires communicating the intermediate vector.

## Routes and Fabric DSDs (fabout_dsd and fabin_dsd)

In `layout.csl`, we have introduced a color to send/receive data between the PEs, and a task_id used to trigger the exit task.

```
// Colors
const send_color: color = @get_color(0); // Color used to send/recv data 
// Task IDs
const exit_task_id: local_task_id = @get_local_task_id(9); // Task ID used by local task

```
These are passed to `pe_program.csl` tile code in 
```
   // Left PE (0, 0)
  @set_tile_code(0, 0, "pe_program.csl", .{
    .memcpy_params = memcpy.get_params(0),
    .N = N,
    .pe_id = 0,
    .send_color = send_color,
    .exit_task_id = exit_task_id
  });

  // Left PE sends its result to the right
  @set_color_config(0, 0, send_color, .{.routes = .{ .rx = .{RAMP}, .tx = .{EAST} }});

  // Right PE (1, 0)
  @set_tile_code(1, 0, "pe_program.csl", .{
    .memcpy_params = memcpy.get_params(1),
    .N = N,
    .pe_id = 1,
    .send_color = send_color,
    .exit_task_id = exit_task_id
  });  
```

In the two `@set_tile_code` calls, one for the left PE (0, 0), and one for the right PE (1, 0), they now receive as a parameter a pe_id: the left PE has pe_id 0, and the right PE has pe_id 1. We’ll see in pe_program.csl how we use pe_id to parameterize the behavior of the program.

The router of each PE has five directions: `RAMP`, `NORTH`, `SOUTH`, `EAST`, `WEST`. (For a good conceptual view, see https://sdk.cerebras.net/computing-with-cerebras) The cardinal directions refer to the routers of neighboring PEs: `NORTH` is the PE directly above our PE, and so on. `RAMP` refers to the connection between our PE’s router and its compute element (CE). When setting a route for a color on a given PE, the receive `rx` and transmit `tx` fields are from the perspective of the router. Thus, receiving form the RAMP means that our compute element is sending data up to the fabric, where it can then be transmitted across the fabric.

For the left PE (0, 0), send_color will send up the PE’s RAMP to the fabric, and then transmit data to the EAST. For the right PE (1, 0), send_color will receive data from the WEST on the fabric (i.e., from the left PE), and then transmit it down the RAMP to its compute element.

As for `pe_program.csl`, we use the `pe_id` to determine the behaviour:

```
fn compute() void {
  if (pe_id == 0) {
    const a: f32 = 2.0;
    @fmuls(x_dsd, a, x_dsd);
    send_right();
  } else {
    y[0] = 1.0;
    y[1] = 1.0;
    y[2] = 1.0;
    recv_left();
  }
}
```

The `compute` function on the left PE first computes the multiplication `a*x`, and calls `send_right` to transfer the result to the left. On the right PE, it initializes `y`, then receives the results from the left, then computes the sum (see below)

```
fn send_right() void {
  const out_dsd = @get_dsd(fabout_dsd, .{.fabric_color = send_color, .extend = N, .output_queue = @get_output_queue(1)});
  @fmovs(out_dsd, x_dsd, .{ .async = true, .activate = exit_task_id });
}

fn recv_left() void{
  const in_dsd = @get_dsd(fabin_dsd, .{fabric_color = send_color, .extent = N, .input_queue = @get_input_queue(1)});
  @fadds(y_dsd, y_dsd, in_dsd, .{ .async = true, .activate = exit_task_id});
}
```

`send_left` defines a `fabout_dsd`, which is used to send wavelets to the fabric along the color `send_color`. Note that we give this `fabout_dsd` the extent `N`, since we intend to send the `N` elements of `a*x` along the fabric. The `@fmovs` operation copies the `N` elements accessed by `x_dsd` into `out_dsd`. The `.async = true` field makes this operation asynchronous. The `.activate` field specifies a `local_task_id` to activate when this operation completes. When this operation completes, `exit_task_id` will be activated.

`recv_right` defines a `fabin_dsd` to receive the wavelets sent along `send_color`. The `@fadds` operation here increments the right PE’s y_dsd by the elements received in `in_dsd`. Thus, after this operation, `y_dsd` contains our final AXPY result. This builtin also executes asynchronously, and actives `exit_task_id` when complete. 

Whenever using fabric DSDs in builtin operations, always make these operations execute asynchronously. Using fabric DSDs synchronously can result in poor performance or deadlocks.

## Tasks and activatable task IDs

Now what does activating `exit_task_id` do? In `pe_program.csl`, we also added

```

task exit_task() void {
  sys_mod.unblock_cmd_stream();
}

comptime {
  @bind_local_task(exit_task, exit_task_id);
}

```

In the comptime block, the `@bind_local_task` builtin binds `exit_task_id` to the task `exit_task`. When `exit_task_id` is activated, `exit_task`, which unblocks the memcpy command stream. This task must execute on both PEs before control is returned to the host.
