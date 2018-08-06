from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np
from sudoku import *


class Benchmark:
    def __init__(self):
        self.easy9_solver1_times = []
        self.easy9_solver2_times = []
        self.easy9_solver3_times = []

        self.hard9_solver1_times = []
        self.hard9_solver2_times = []
        self.hard9_solver3_times = []

        self.easy16_solver1_times = []
        self.easy16_solver2_times = []
        self.easy16_solver3_times = []

        self.hard16_solver1_times = []
        self.hard16_solver2_times = []
        self.hard16_solver3_times = []

        self.times = {
            'easy91': self.easy9_solver1_times,
            'easy92': self.easy9_solver2_times,
            'easy93': self.easy9_solver3_times,

            'hard91': self.hard9_solver1_times,
            'hard92': self.hard9_solver2_times,
            'hard93': self.hard9_solver3_times,

            'easy161': self.easy16_solver1_times,
            'easy162': self.easy16_solver2_times,
            'easy163': self.easy16_solver3_times,

            'hard161': self.hard16_solver1_times,
            'hard162': self.hard16_solver2_times,
            'hard163': self.hard16_solver3_times
        }

    def time(self, dif='hard', size=9):
        sudoku = Sudoku(size)

        problem_set = sudoku.easy if dif != 'hard' else sudoku.hard

        for i, p in enumerate(problem_set):
            g = Grid(p, size)
            naive_solver = NaiveSolver(g, size, '')
            pro_solver = ProSolver(g, size, '')
            sat_solver = SATSolver(
                g, size, '{}{}_{}.cnf'.format(dif, str(size), str(i)))

            t1, _ = naive_solver.solve()
            t2, _ = pro_solver.solve()
            t3, _ = sat_solver.solve()

            self.times[dif + str(size) + str(1)].append(int(t1 * 1000))
            self.times[dif + str(size) + str(2)].append(int(t2 * 1000))
            self.times[dif + str(size) + str(3)].append(int(t3 * 1000))

    def plot(self, dif='hard', size=9):
        self.time(dif, size)

        t1 = self.times[dif + str(size) + '1']
        t2 = self.times[dif + str(size) + '2']
        t3 = self.times[dif + str(size) + '3']

        ind = np.arange(len(t2))  # the x locations for the groups
        width = 0.2  # the width of the bars

        fig, ax = plt.subplots()

        rects1 = ax.bar(ind - width, t1, width,
                        color='b', label='Naive Solver')
        rects2 = ax.bar(ind, t2, width,
                        color='r', label='Pro Solver')
        rects3 = ax.bar(ind + width, t3, width,
                        color='g', label='SAT Solver')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Time (miliseconds)')
        ax.set_title('{} Problems {}'.format(
            dif.upper(), '{}X{}'.format(str(size), str(size))))
        ax.legend()

        plt.show()

    def plot_all(self):
        self.plot('easy', 9)
        self.plot('hard', 9)

        self.plot('easy', 16)
        self.plot('hard', 16)
