from sudoku import *
from benchmark import Benchmark

''' Use Sudoku().solve_all() to solve all problems using a specific solver'''
# Sudoku(9).solve_all(NaiveSolver)  # You wouldn't want to do this!!
# Sudoku(9).solve_all(NaiveSolver)  # It would take FOREVER

# Sudoku(9).solve_all(ProSolver)
# Sudoku(16).solve_all(ProSolver)

Sudoku(9).solve_all(SATSolver)
Sudoku(16).solve_all(SATSolver)

''' Use Sudoku().solve([solver], [problem], [filename]) to solve one problem.'''
# Sudoku(9).solve(NaiveSolver, Sudoku(9).easy[1], 'test')
# Sudoku(9).solve(ProSolver, Sudoku(9).easy[1], 'test')
# Sudoku(9).solve(SATSolver, Sudoku(9).easy[1], 'test')

''' Use Benchamrk().plot_all() to see all the graphs.'''
# Benchmark().plot_all()

''' Use Benchamrk().plot([dificulty], [size]) to see specific graph.'''
Benchmark().plot('easy', 16)
