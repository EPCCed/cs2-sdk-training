# Hands-on 2: GEMV on a 2 PEs

The aim of this hands-on is to perform GEMV over 2 PEs.

On each PE, a local GEMV will be performed, then the result from the left will be transfered to the right, then summed.

This will use the techniques introduced in Walk-Throughs 5 and 6, including

* fabric DSDs
* setting tile code for multiple PEs
* setting color config routes for PEs

## To do's:
To complete this hands-on, the following sections need to be filled in:
* 3 sections in [pe_program.csl](layout.csl) 
* 2 section in [layout.csl](layout.csl)

## Solution
Solution is provided.