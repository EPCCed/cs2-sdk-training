# Walk-through 4: Memory DSDs and Builtins

A central concept in CSL is memory Data Structure Descriptors (DSDs). Memory DSDs provide an efficient mechanism for performing operations on entire tensors.

## Defining memory DSDs

First, let’s take a look at the DSDs we define for accessing b and y:

```
var x_dsd = @get_dsd(mem1d_dsd, .{ .tensor_access = |i|{N} -> x[i] });
var y_dsd = @get_dsd(mem1d_dsd, .{ .tensor_access = |i|{N} -> y[i] });
```

`x_dsd` and `y_dsd` are the memory DSDs for accessing x and y, respectively.

The tensor_access field defines the access pattern of these DSDs. `|i|` specifies the induction variable, and `{N}` specifies the loop bound; i.e., these DSDs will access M elements. After `->`, an expression is given for accessing a memory location using the induction variable. This expression must be affine, or linear plus a constant.

The access pattern for these DSDs is straightforward: these DSDs loop over all N elements, in order, of their respective tensors.

Now let’s take a look at a different DSD for accessing a matrix A:

```
var A_dsd = @get_dsd(mem1d_dsd, .{ .tensor_access = |i|{M} -> A[i*N] });
```

This DSD accesses `M` elements of `A`, but strided by `N` elements; i.e., `A_dsd` accesses elements `0, N, 2*N, ... (M-1)*N`. Because `A` is stored in row major format, this means that `A_dsd` as defined here accesses the 0th column of `A`.

These memory DSDs are of type mem1d_dsd, which are one-dimensional memory DSDs. CSL also provides mem4d_dsd, multidimensional memory DSDs for up to four dimensions.

## Using DSDs via Builtins

Previously we had:

```
for (@range(i16, N)) |idx| {
      y_ptr.*[idx] += value * x_ptr.*[idx];
  }
```

Now we can use the DSDs with 
```
@fmacs(y_dsd, y_dsd, x_dsd, a)
```

Notice we no longer need to use a loop. The `@fmacs` operation performs a multiply-add `y = y + a*x` for the entire vector.