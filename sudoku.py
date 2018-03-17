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
        # Assigning given information (grids) to sigma
        # self.add_to_sigma(self.sigma, {}, {})

        result = self.search(self.sigma)
        return result

    def add_to_sigma(self, sigma, assignments, removed_vals):
        for s in self.grid.spots:
            if len(self.grid.domains[s]) == 1:
                if not self.sigma.get(s):
                    self.sigma[s] = self.grid.domains[s][0]
                    self.add_to(assignments, s, self.grid.domains[s][0])
                    self.remove_from_peers(
                        self.grid.domains[s][0], self.grid.peers[s], removed_vals)

    def remove_from_peers(self, d, peers, removed_vals):
        for peer in peers:
            if d in self.grid.domains[peer]:
                self.grid.domains[peer].remove(d)
                self.add_to(removed_vals, peer, d)

    def assign(self, sigma, s, d, assignments, removed_vals):
        other_values = [x for x in self.grid.domains[s] if x != d]
        if all(self.eliminate(sigma, s, d2, assignments, removed_vals) for d2 in other_values):
            self.add_to_sigma(sigma, assignments, removed_vals)
            return True
        else:
            return False

    def eliminate(self, sigma, s, d, assignments, removed_vals):
        if d not in self.grid.domains[s]:
            return True

        self.grid.domains[s].remove(d)
        self.add_to(removed_vals, s, d)

        if len(self.grid.domains[s]) == 0:
            return False  # Contradiction: removed last d
        elif len(self.grid.domains[s]) == 1:
            d2 = self.grid.domains[s][0]
            if not all(self.eliminate(sigma, peer, d2, assignments, removed_vals) for peer in self.grid.peers[s]):

                return False

        for u in self.grid.units[s]:
            value_spots = [s for s in u if d in self.grid.domains[s]]
            if len(value_spots) == 0:
                return False
            elif len(value_spots) == 1:
                if not self.assign(sigma, value_spots[0], d, assignments, removed_vals):
                    return False

        return True

    def rollback(self, sigma, assignments, removed_vals):
        for s, d in assignments.iteritems():
            del sigma[s]

        for s, values in removed_vals.iteritems():
            for d in values:
                assert d not in self.grid.domains[s]
                self.grid.domains[s].append(d)

    def search(self, sigma):
        if len(sigma) == len(self.grid.spots):
            return True

        s = self.select_unassigned_spot()
        for d in self.grid.domains[s]:
            assignments = {}
            removed_vals = {}
            if self.consistent(sigma, s, d):
                if self.assign(sigma, s, d, assignments, removed_vals):
                    # If not, check if needed to add mannually
                    assert all([sigma.get(s) for s in assignments])
                    if self.search(sigma):
                        return True
                self.rollback(sigma, assignments, removed_vals)

        return False

    ##### OTHERS #####
    def add_to(self, dictionary, s, d):
        if dictionary.get(s):
            dictionary[s].add(d)
        else:
            dictionary[s] = set([d])

    def consistent(self, sigma, spot, value):
        for peer in self.grid.peers[spot]:
            if sigma.get(peer) == value:
                return False
        return True

    def select_unassigned_spot(self):
        # return min([s for s in self.grid.spots if len(self.grid.domains[s]) > 1])

        for spot in self.grid.spots:
            if not self.sigma.get(spot):
                return spot

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
g = Grid(hard[0])
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
