# Hands-on 1: GEMV on a single PE

The aim of this hands-on is to create an application that performs a matrix-vector multiplication on a single PE.

Matrix `A` of size `M`x`N` (`M` rows and `N` columns), a vector `x` of size `N`, and vectors `b` and `y` of size `M`:

`y = b + A@x`

Use the content up to Walk-through 4. Techniques include: 

* memcpy (H2D and D2H)
* memory DSD for multiplication

The parameters `M` and `N` should be set during compile time.

## To do's:
To complete this hands-on, the following sections need to be filled in:
* 2 sections in [run.py](run.py)
* 2 sections in [pe_program.csl](layout.csl) 
* 1 section in [layout.csl](layout.csl)

## Solutions
Two solutions are provided, the first one (solution A) uses loops and the other (solution B) uses DSDs to perform the matrix vector multiplication.