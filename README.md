Assignment 5: Sudoku without and with SAT
=========

Important: Your commits should be using the Github Classroom link (in a private repository), not directly cloning from the open repositiory. 

Due date
-----
March 18 (Sunday) 11:59pm Pacific Time. Extra credits for earlier submission (see below). 

Tasks
-----
Regular Commits (1 point): At least one nontrivial commit by Feb-28 11:59pm. 

Documentation (1 point): Comment your code generously. 

Task 1 (8 points): Naive Constraint Solving

- Implement the naive constraint solving algorithm in the AIMA book (Chapter 6, Section 6.3, Page 215, Figure 6.5; it is the same as shown in slide 47 from class), by filling in the missing part of the given 'sudoku.py' file. Feel free make minor changes to the given code, but the data structure should be roughly the same. 

The naive algorithm should solve the easy puzzles quickly. It can take several minutes to solve the hard ones this way. 

Task 2 (6 points): Use More Pruning

- Extend the code with more advanced solving techniques as explained in [this post](http://norvig.com/sudoku.html). Note that the techniques are closer to the set-based pruning that we discussed in class, tailored to solving Sudoku. Clearly, you can not just copy paste their code, but need to understand it and then adapt it without changing the data structure from the first task. 

The advanced algorithm should now solve the hard puzzles quickly. 

Task 3 (8 points): Translate to SAT to Solve

- Implement an encoding of Sudoku as propositional logic formulas in conjunctive normal forms, and use a state-of-the-art SAT solver to solve. Read the `notes.pdf` file for more details. The `hard1.cnf` file in the `cnf` directory is the encoding of the first hard instance in the code. You need to generate the CNF files, pass them to a SAT solver (see below) to solve, and then parse the output from the SAT solver and plug them back into the original problem and display the solutions. 

SAT Solvers to Use
-----

I recommend [PicoSAT](http://fmv.jku.at/picosat/) as the default choice. Go to its webpage, download, and compile (simply do `./configure.sh` and then `make`). The binary `picosat` can then take the CNF files you produce (always use extension `.cnf`). 

I highly recommend that you find a linux/mac machine to use the solver. If you have to use windows, this [note](https://gist.github.com/ConstantineLignos/4601835) may be helpful but I haven't tried. If you have difficulty in getting PicoSAT to work, try [cryptominisat](https://github.com/msoos/cryptominisat) which has more instructions about making things work on windows. 

If you want to know about more solvers, check the [page](http://www.satcompetition.org/) for the annual SAT solver competition. 


Extra Credits
-----
If your last commit is pushed by March-14 11:59pm, with no significant bug, then you will earn 3 extra points. Note that you can decide to just finish one or two parts of the assignment (like just aiming for 8 or 16 points), and still get the extra points added if you finish them early.  

Extension Policy
-----
If you are too busy with many finals, you can submit by March-24 11:59pm and get 70% of the points. Message me directly if you choose to do this. 
