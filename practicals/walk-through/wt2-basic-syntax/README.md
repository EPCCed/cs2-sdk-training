# Walk Through 2: Basic Syntax

The aim of this walk-through is to introduce some basic syntax of the CSL language.

CSL is a language for writing programs that run on the Cerebras Wafer Scale Engine (WSE). 

## Types: variables, pointers, arrays, functions

## Comptime block

## Functions vs Tasks
Each task is bound to a task ID, which serves as a handle for identifying the task.

The term “task identifier” or “task ID” is used to refer to a numerical value that can be associated with a task. A task ID is a number from 0 to 63. Within this range there are two properties that further distinguish a task ID: routable and activatable.

There exist three types of tasks, each with an associated task ID handle type:

    The first are data tasks. These are associated with a data_task_id, which on the wse2 architecture is created from a routable identifier associated with a color.

    The second are local tasks. These are associated with a local_task_id, which is created from an activatable identifier.

    The third are control tasks. These are associated with a control_task_id, which can be created from any identifier, including those that are neither routable nor activatable.

Both data tasks and control tasks are a type of wavelet-triggered task, or WTT: their activation is triggerd by the arrival of a wavelet. In this introduction, we will explore what it means for a task ID to be routable or activatable, and the usage of data tasks and local tasks.

## Task Activation, Control Flow, Blocking and Unblocking


Other important properties, including DSD, DSR, libraries will be covered in a later tutorial.
For a more comprehensive reference of the CSL language, see [documentation](https://sdk.cerebras.net/csl/language_index).
