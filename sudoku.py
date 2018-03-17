'''
The code for Solver2 was highly inspired by Peter Norvig's implementation:
http://norvig.com/sudoku.html
'''

from __future__ import print_function
import random
import copy
import time


def time_deco(f):
    def decorated(*args):
        t = time.time()
        result = f(*args)
        print('\n***** Execution time: %s seconds *****\n' % str(time.time() - t))
        return result
    return decorated


class Grid:
    def __init__(self, problem):
        self.spots = [(i, j) for i in range(1, 10) for j in range(1, 10)]
        self.domains = {}
        # Need a dictionary that maps each spot to its related spots
        self.peers = {}
        self.units = {}

        self.parse(problem)
        self.set_peers()
        self.set_units()

    def parse(self, problem):
        for i in range(0, 9):
            for j in range(0, 9):
                c = problem[i * 9 + j]
                if c == '.':
                    self.domains[(i + 1, j + 1)] = range(1, 10)
                else:
                    self.domains[(i + 1, j + 1)] = [ord(c) - 48]

    def set_peers(self):
        for i in range(0, 9):
            for j in range(0, 9):
                row = [(i + 1, k + 1) for k in range(0, 9) if k != j]
                col = [(k + 1, j + 1) for k in range(0, 9) if k != i]
                sqr = [(k + 1, l + 1) for k in range(i // 3 * 3, i // 3 * 3 + 3)
                       for l in range(j // 3 * 3, j // 3 * 3 + 3) if (i, j) != (k, l)]

                self.peers[(i + 1, j + 1)] = set(row + col + sqr)

    def set_units(self):
        for i in range(0, 9):
            for j in range(0, 9):
                row = [(i + 1, k + 1) for k in range(0, 9)]
                col = [(k + 1, j + 1) for k in range(0, 9)]
                sqr = [(k + 1, l + 1) for k in range(i // 3 * 3, i // 3 * 3 + 3)
                       for l in range(j // 3 * 3, j // 3 * 3 + 3)]

                self.units[(i + 1, j + 1)] = [row, col, sqr]

    def display(self):
        for i in range(0, 9):
            for j in range(0, 9):
                d = self.domains[(i + 1, j + 1)]
                if len(d) == 1:
                    print(d[0], end='')
                else:
                    print('.', end='')
                if j == 2 or j == 5:
                    print(" | ", end='')
            print()
            if i == 2 or i == 5:
                print("---------------")


class Solver:
    def __init__(self, grid):
        self.grid = grid
        self.sigma = {}

    @time_deco
    def solve(self):
        # Filling given information (grids)
        for spot in self.grid.spots:
            if len(self.grid.domains[spot]) == 1:
                self.sigma[spot] = self.grid.domains[spot][0]

        result = self.backtrack(self.sigma)
        return result

    def backtrack(self, sigma):
        if len(sigma) == len(self.grid.spots):
            return True

        spot = self.select_unassigned_spot()
        for value in self.grid.domains[spot]:
            if self.consistent(sigma, spot, value):
                sigma[spot] = value
                if self.backtrack(sigma):
                    return True

            if sigma.get(spot):
                del sigma[spot]

        return False

    # ---------- HELPERS ---------- #
    def consistent(self, sigma, spot, value):
        for peer in self.grid.peers[spot]:
            if sigma.get(peer) == value:
                return False

        return True

    def select_unassigned_spot(self):
        for spot in self.grid.spots:
            if not self.sigma.get(spot):
                return spot


class Solver2:
    def __init__(self, grid):
        self.grid = grid
        self.sigma = {}

    @time_deco
    def solve(self):
        domains = self.initial_assignment()
        if not domains:
            return False

        return self.assign_to_sigma(self.sigma, self.search(domains))

    def search(self, values):
        if values is False:
            return False

        if all([len(values[s]) == 1 for s in self.grid.spots]):
            return values

        _, s = min((len(values[s]), s) for s in self.grid.spots if len(values[s]) > 1)
        return self.some(self.search(self.assign(copy.deepcopy(values), s, d))
                         for d in values[s])

    def some(self, seq):
        "Return some element of seq that is true."
        for e in seq:
            if e:
                return e
        return False

    def assign(self, values, s, d):
        """Eliminate all the other values (except d) from values[s] and propagate.
        Return values, except return False if a contradiction is detected."""

        other_values = [v for v in values[s] if v != d]

        if all(self.eliminate(values, s, d2) for d2 in other_values):
            return values
        else:
            return False

    def eliminate(self, values, s, d):
        # print('Eliminating {} from {}'.format(d, values[s]))
        """Eliminate d from values[s]; propagate when values or places <= 2.
        Return values, except return False if a contradiction is detected."""
        if d not in values[s]:
            return values  # Already eliminated

        values[s].remove(d)

        # (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
        if len(values[s]) == 0:
            return False  # Contradiction: removed last value
        elif len(values[s]) == 1:
            d2 = values[s][0]
            if not all(self.eliminate(values, s2, d2) for s2 in self.grid.peers[s]):
                return False

        # (2) If a unit u is reduced to only one place for a value d, then put it there.
        for u in self.grid.units[s]:
            dplaces = [s for s in u if d in values[s]]
            if len(dplaces) == 0:
                return False  # Contradiction: no place for this value
            elif len(dplaces) == 1:
                if not self.assign(values, dplaces[0], d):
                    return False

        return values

    def assign_to_sigma(self, sigma, domains):
        if not domains:
            return False

        for spot in self.grid.spots:
            sigma[spot] = domains[spot][0]

        return sigma

    def initial_assignment(self):
        for s in self.grid.spots:
            if len(self.grid.domains[s]) == 1:
                d = self.grid.domains[s][0]
                self.grid.domains[s] = range(1, 10)
                if not self.assign(self.grid.domains, s, d):
                    return False
        return self.grid.domains

    def consistent(self, sigma, spot, value):
        for peer in self.grid.peers[spot]:
            if sigma.get(peer) == value:
                return False
        return True


###### ---------- MAIN ---------- ######


def display_solution(d):
    for i in range(0, 9):
        for j in range(0, 9):
            print(d[(i + 1, j + 1)], end='')
            if j == 2 or j == 5:
                print(" | ", end='')
        print()
        if i == 2 or i == 5:
            print("---------------")


easy = ["..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..",
        "2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3",
        '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..']

hard = ["4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......",
        "52...6.........7.13...........4..8..6......5...........418.........3..2...87....."]

print("====Problem====")
g = Grid(hard[1])
# Display the original problem
g.display()
s = Solver2(g)
if s.solve():
    print("====Solution===")
    # Display the solution
    # Feel free to call other functions to display
    assert all(s.consistent(s.sigma, spot, s.sigma[spot]) for spot in s.sigma)
    display_solution(s.sigma)
else:
    print("==No solution==")
