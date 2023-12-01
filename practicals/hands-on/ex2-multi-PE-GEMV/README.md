# Hands-on 2: GEMV on a 2 PEs

The aim of this hands-on is to perform GEMV over 2 PEs.

On each PE, a local GEMV will be performed, then the result from the left will be transfered to the right, then summed.

This will use the techniques introduced in wt4/5, including

* fabric DSDs
* setting tile code for multiple PEs
* setting color config routes for PEs

There are 3 to-do's in [pe_program.csl](pe_program.csl) and 2 in [layout.csl](layout.csl).