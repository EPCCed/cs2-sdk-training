# Hands-on 1: GEMV on a single PE

The aim of this hands-on is to create an application that performs a matrix-vector multiplication on a single PE.

Matrix A of size MxN (M rows and N columns), a vector x of size N, and vectors b and y of size M:

y = b + A@x

Use the content up to Walk-through 4. Techniques include: 

* memcpy (H2D and D2H)
* memory DSD for multiplication

The parameters M and N should be set during compile time.

There are 2 to-do's in [run.py](run.py), 2 in [pe_program.csl](layout.csl) and 1 in [layout.csl](layout.csl)