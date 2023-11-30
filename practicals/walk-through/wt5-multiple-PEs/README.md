# Walk through 5: Multiple PEs

For this walk through we go from using a single PE to using 2 PE to perform our AXPY operation. For this application, no communication is required between the PEs. 

The operation performed on each PE remains unchanged, so `pe_program.csl` need not be changed. However, for `layout.csl`, we updated:

```
const memcpy = @import_module("<memcpy/get_params>", .{
  .width = width,
  .height = 1,
  .LAUNCH = LAUNCH
});

layout {

  @set_rectangle(width, 1);
  for (@range(i16, width)) |x| {
    @set_tile_code(x, 0, "pe_program.csl", .{
      .memcpy_params = memcpy.get_params(x),
      .N = N
    });
```

This assigns the program `pe_program.csl` to the two PEs. 

Here in `layout.csl` we also added two `param`:

```
param N: i16;
param width: i16;
```

For `commands.sh`, we also need to update the `--fabric-dims`:

```
cslc layout.csl --fabric-dims=11,3 --fabric-offsets=4,1 --params=N:3,width:2 --memcpy --channels=1 -o out
```

We see that we used the same `--fabric-offset` of `4,1`, but increased the fabric dimension. Note that if compiling for a simulate dfabric, the fabric dimension must be at least `width+7,height+1`, where `width` and `height` are the dimensions of the program. These additional PEs are used by memcpy to route data on and off the wafer.

Also note that we have used `--params=N:3,width:2` to pass the parameters to `layout.csl`.
