# Walk Through 2: Basic Syntax

The aim of this walk-through is to introduce some basic syntax of the CSL language.

CSL is a language for writing programs that run on the Cerebras Wafer Scale Engine (WSE). The syntax of CSL is similar to Zig.

This program performs a very simple AXPY operation, for two vectors `x` and `y` and a scalar `a`, we compute `y = y + a*x`. 

## Types:

CSL basic types:

* `bool` for boolean values
* `i8`, `i16` and `i32` for 8-, 16- and 32-bit signed integers
* `u8`, `u16` and `u32` for 8-, 16- and 32-bit unsigned integers
* `f16` and `f32` for 16- and 32-bit IEEE-754 floating point numbers

Array types: `[num_elements] base_type (optional: {literals})`, e.g.:
* `1d_array = [3]i16 {1, 2, 3}`

Multi-dimensional array, e.g.:
* `2d_array = [10, 10]u16`

Pointers:
* `ptr = &1d_array`
* `ptr.*[0] = 2`

## Variables:

* `const` cannot change value after initialized, mandatory initializer
* `param` cannot change value after initialized
* `var` can change value

## functions
Function definitions require a fn or task keyword, a name, an optional sequence of parameters, a return type and a function body:

``` bash
fn foo(arg : i16) i32 { ... }
task my_task(arg : i16) void { ... }
```

## Comptime block
In CSL, it is possible to ensure that code is executed at compile-time by using the `comptime` keyword, which guarantees that the code will have no run-time footprint. An error is emitted if compile-time evaluation is not possible.

Typical use case of `comptime`: comptime variables and operations enable powerful operations such as non-trivial memory initialization or routing rules, without paying a performance penalty at run-time. For instance, the following code initializes a global array as an identity matrix at compile time.

```
param size: u16;

// global initializers are implicitly comptime
const identity = createIdentityMatrix();

fn createIdentityMatrix() [size, size]f16 {
  var result = @zeros([size, size]f16);

  var i: u16 = 0;
  while (i < size) : (i += 1) {
    result[i,i] = 1.0;
  }

  return result;
}
```

## Tasks
Each task is bound to a task ID, which serves as a handle for identifying the task.

The term “task identifier” or “task ID” is used to refer to a numerical value that can be associated with a task. A task ID is a number from 0 to 63. Within this range there are two properties that further distinguish a task ID: routable and activatable.

There exist three types of tasks, each with an associated task ID handle type:

* The first are data tasks. These are associated with a data_task_id, which on the wse2 architecture is created from a routable identifier associated with a color.
* The second are local tasks. These are associated with a local_task_id, which is created from an activatable identifier.
* The third are control tasks. These are associated with a control_task_id, which can be created from any identifier, including those that are neither routable nor activatable.

Routable IDs are also referred to as colors.

Both data tasks and control tasks are a type of wavelet-triggered task, or WTT: their activation is triggerd by the arrival of a wavelet. 

In this code, `LAUNCH` is a routable color/data task with ID `8`. Here the color `LAUNCH` is used for memcpy for the Remote Procedure Calls (RPC) mechanism (memcpy and RPC will be covered in more detail in the next walk-through). In a later walk through (6), we will also demonstrate using a local task (exit_task) and binding it to a local_task_id (exit_task_id).

## Task Activation and Control Flow

A task will become available for selection by the task picker when its associated task ID is activated.

The task in the above block was a data task bound to a data_task_id, associated with a color which defines a route taken by wavelets tagged with that color.

Additionally, we can create tasks which do not take wavelets as arguments, and instead are explicitly activated by other tasks or functions. We call these tasks local tasks, and the associated task ID type is local_task_ID.

On wse2, we can create a local_task_ID from the range of task IDs 0 to 30. These IDs are the activatable IDs.

In the below example, main_task activates the task ID foo_task_id. This task ID is bound to foo_task, and so activating foo_task_id will cause foo_task to execute next.

```
const red: color = @get_color(7);
const red_task_id: data_task_id = @get_data_task_id(red);
const foo_task_id: local_task_id = @get_local_task_id(8);

var result: f32 = 0.0;
var sum: f32 = 0.0;

task main_task(wavelet_data: f32) {
    result = wavelet_data;
    @activate(foo_task_id);
}

task foo_task() {
    sum += result;
}

comptime {
    @bind_data_task(main_task, red_task_id);
    @bind_local_task(foo_task, foo_task_id);
}
```

## Blocking and Unblocking

We can additionally block a task ID to provide further control over task execution. A task must be unblocked and activated for it be scheduled by the task picker. If a task is activated while blocked, it will only run once it has become unblocked. By default, all IDs are unblocked and inactive.

In the below example, we introduce one additional task, bar_task. We block the ID of this task at compile time, with @block(bar_task_id).

When main_task executes, it activates both foo_task_id and bar_task_id. However, because bar_task_id is blocked, we guarantee that foo_task executes first. When foo_task executes, in unblocks bar_task_id, allowing bar_task to begin execution once foo_task finishes.

If bar_task_id were not blocked at compile time, then the execution of foo_task and bar_task could occur in any order.

```
const red: color = @get_color(7);
const red_task_id: data_task_id = @get_data_task_id(red);
const foo_task_id: local_task_id = @get_local_task_id(8);
const bar_task_id: local_task_id = @get_local_task_id(9);

var result: f32 = 0.0;
var sum: f32 = 0.0;

task main_task(wavelet_data: f32) {
    result = wavelet_data;

    @activate(foo_task_id);
    @activate(bar_task_id);
}

task foo_task() {
    sum += result;
    @unblock(bar_task_id);
}

task bar_task() {
    sum *= 2.0;
}

comptime {
    @block(bar_task_id);
    @bind_data_task(main_task, red_task_id);
    @bind_local_task(foo_task, foo_task_id);
    @bind_local_task(bar_task, bar_task_id);
}
```

Other important properties, including DSD, DSR, libraries will be covered in a later tutorial.
For a more comprehensive reference of the CSL language, see [documentation](https://sdk.cerebras.net/csl/language_index).
