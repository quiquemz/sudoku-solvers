Sudoku Solvers
=========

**Naive Constraint Solver**

- Implemented using the Backtracking Search algorithm for Constraint Satisfaction Problems (CSP) with little pruning.

The naive algorithm should solve easy puzzles quickly. It can take several minutes to solve the hard ones this way.

**Pro Constraint SolverUse More Pruning**

- Extended the algorithm created by [Peter Norvig](http://norvig.com/sudoku.html). This code uses the idea of set-based pruning that allow to reduce the amount of

This algorithm should solve the hard puzzles in a few seconds.

**SAT Solver**

- Implemented an algorithm to encode the sudoku problem as propositional logic formulas in conjunctive normal forms to finally use a state-of-the-art [PicoSAT](http://fmv.jku.at/picosat/) solver to solve.

- Note: this solver only works on linux/mac machines.

Sudoku Benchmark
=========
- Plot producer that shows the the performance difference of the different approaches (with a timeout of 5 minutes or something on the naive algorithm).
