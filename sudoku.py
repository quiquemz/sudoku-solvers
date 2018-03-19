'''
The code for Solver2 was highly inspired by Peter Norvig's implementation:
http://norvig.com/sudoku.html
'''

from __future__ import print_function
import random
import copy
import time
import pycosat
import signal
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
from subprocess import Popen, PIPE


MAP = {1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
       10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 16: 'G'}


class TimedOutExc(Exception):
    pass


def deadline(timeout, *args):
    def decorate(f):
        def handler(signum, frame):
            raise TimedOutExc()

        def new_f(*args):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            return f(*args)
            signa.alarm(0)
        new_f.__name__ = f.__name__
        return new_f
    return decorate


def time_deco(f):
    def decorated(*args):
        t = time.time()
        try:
            result = f(*args)
            print('test 2')
            t = time.time() - t
            print('\nExecution time: %s seconds\n' % str(t))
            return (t, result)

        except:
            print('\nEXCEEDED LIMIT: 5 MINS\n')
            return(5., False)
    return decorated


class Grid:
    def __init__(self, problem, size):
        self.size = size
        self.spots = [(i, j) for i in range(1, size + 1) for j in range(1, size + 1)]
        self.domains = {}
        # Need a dictionary that maps each spot to its related spots
        self.peers = {}
        self.units = {}

        self.parse(problem)
        self.set_peers()
        self.set_units()

    def parse(self, problem):
        for i in range(0, self.size):
            for j in range(0, self.size):
                problem[i * self.size + j]
                c = problem[i * self.size + j].upper()
                if c == '.':
                    self.domains[(i + 1, j + 1)] = range(1, self.size + 1)
                else:
                    self.domains[(i + 1, j + 1)] = [ord(c) - 48] if ord(c) <= 57 else [ord(c) - 55]

    def set_peers(self):
        x = int(sqrt(self.size))
        for i in range(0, self.size):
            for j in range(0, self.size):
                row = [(i + 1, k + 1) for k in range(0, self.size) if k != j]
                col = [(k + 1, j + 1) for k in range(0, self.size) if k != i]
                sqr = [(k + 1, l + 1) for k in range(i // x * x, i // x * x + x)
                       for l in range(j // x * x, j // x * x + x) if (i, j) != (k, l)]

                self.peers[(i + 1, j + 1)] = set(row + col + sqr)

    def set_units(self):
        x = int(sqrt(self.size))
        for i in range(0, self.size):
            for j in range(0, self.size):
                row = [(i + 1, k + 1) for k in range(0, self.size)]
                col = [(k + 1, j + 1) for k in range(0, self.size)]
                sqr = [(k + 1, l + 1) for k in range(i // x * x, i // x * x + x)
                       for l in range(j // x * x, j // x * x + x)]

                self.units[(i + 1, j + 1)] = [row, col, sqr]

    def display(self):
        for i in range(0, self.size):
            for j in range(0, self.size):
                d = self.domains[(i + 1, j + 1)]
                if len(d) == 1:
                    s = MAP[d[0]]
                    print(s, end='')
                else:
                    print('.', end='')

                if self.size == 9:
                    if j == 2 or j == 5:
                        print(" | ", end='')
                elif self.size == 16:
                    if j == 3 or j == 7 or j == 11:
                        print(" | ", end='')
            print()
            if self.size == 9:
                if i == 2 or i == 5:
                    print("---------------")
            elif self.size == 16:
                if i == 3 or i == 7 or i == 11:
                    print("-------------------------")


class Solver:
    def __init__(self, grid, size, filename):
        self.size = size
        self.grid = grid
        self.sigma = {}

    @deadline(300)
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
    def __init__(self, grid, size, filename):
        self.size = size
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
                self.grid.domains[s] = range(1, self.size + 1)
                if not self.assign(self.grid.domains, s, d):
                    return False
        return self.grid.domains

    def consistent(self, sigma, spot, value):
        for peer in self.grid.peers[spot]:
            if sigma.get(peer) == value:
                return False
        return True


class Solver3:
    def __init__(self, grid, size, filename):
        self.grid = grid
        self.cnf_file = 'cnf/' + filename
        self.command = './picosat/picosat'
        self.size = size
        self.sigma = {}

    @time_deco
    def solve(self):
        self.encode_problem()
        self.decode_cnf()
        return True

    def add_current(self, cnf):
        for i in range(self.size):
            for j in range(self.size):
                if len(self.grid.domains[(i + 1, j + 1)]) == 1:
                    spot = self.size * i + j
                    value = self.size * spot + self.grid.domains[(i + 1, j + 1)][0]
                    cnf.append([value])

    def add_domains(self, cnf):
        for i in range(self.size):
            for j in range(self.size):
                spot = self.size * i + j
                cnf.append([(self.size * spot) + k + 1 for k in range(self.size)])

    def add_row_constraint(self, cnf):
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    for m in range(self.size - j - 1):
                        spot = self.size * i + j

                        value1 = self.size * spot + k + 1
                        value2 = value1 + self.size * (m + 1)

                        cnf.append([-value1, -value2])

    def add_col_constraint(self, cnf):
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    for m in range(self.size - i - 1):
                        spot1 = self.size * i + j
                        spot2 = self.size * (i + m + 1) + j

                        value1 = self.size * spot1 + k + 1
                        value2 = self.size * spot2 + k + 1

                        cnf.append([-value1, -value2])

    def add_sqr_constraint(self, cnf):
        sq = int(sqrt(self.size))
        # Adding next spots (in same row)
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    for l in range(i // sq * sq, i // sq * sq + sq):
                        for m in range(j // sq * sq, j // sq * sq + sq):
                            spot1 = self.size * i + j
                            value1 = self.size * spot1 + k + 1
                            spot2 = self.size * l + m
                            value2 = self.size * spot2 + k + 1
                            if value1 != value2:
                                cnf.append([-value1, -value2])

    def encode_problem(self):
        cnf = []
        self.add_current(cnf)
        self.add_domains(cnf)
        self.add_row_constraint(cnf)
        self.add_col_constraint(cnf)
        self.add_sqr_constraint(cnf)

        with open(self.cnf_file, 'w') as f:
            f.write('p cnf {} {} \n'.format(str(self.size ** 3), str(len(cnf))))
            f.writelines(' '.join(str(e) for e in row) + ' 0\n' for row in cnf)

    def decode_cnf(self):
        process = Popen([self.command, self.cnf_file], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()

        output = self.clean_output(output)
        self.add_to_sigma(output)

    def add_to_sigma(self, output):
        for indx, d in enumerate(output):
            i = indx // self.size
            j = indx % self.size
            d = d % self.size if d % self.size != 0 else self.size
            self.sigma[(i + 1, j + 1)] = d

    def clean_output(self, output):
        output = output.split(' ')
        output = [s.strip('\nv') for s in output]
        output = [int(s) for s in output if s.isdigit() and int(s) > 0]

        assert len(output) == self.size ** 2

        return output

    def consistent(self, sigma, spot, value):
        for peer in self.grid.peers[spot]:
            if sigma.get(peer) == value:
                return False
        return True

    def check_int(self, s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()


class Sudoku:
    def __init__(self, size=9):
        if size == 9:
            self.easy = easy = ['..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..',
                                '2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3',
                                '......9.7...42.18....7.5.261..9.4....5.....4....5.7..992.1.8....34.59...5.7......',
                                '.3..5..4...8.1.5..46.....12.7.5.2.8....6.3....4.1.9.3.25.....98..1.2.6...8..6..2.',
                                '.2.81.74.7....31...9...28.5..9.4..874..2.8..316..3.2..3.27...6...56....8.76.51.9.',
                                '1..92....524.1...........7..5...81.2.........4.27...9..6...........3.945....71..6',
                                '.43.8.25.6.............1.949....4.7....6.8....1.2....382.5.............5.34.9.71.',
                                '48...69.2..2..8..19..37..6.84..1.2....37.41....1.6..49.2..85..77..9..6..6.92...18',
                                '...9....2.5.1234...3....16.9.8.......7.....9.......2.5.91....5...7439.2.4....7...',
                                '..19....39..7..16..3...5..7.5......9..43.26..2......7.6..1...3..42..7..65....68..',
                                '...1254....84.....42.8......3.....95.6.9.2.1.51.....6......3.49.....72....1298...',
                                '.6234.75.1....56..57.....4.....948..4.......6..583.....3.....91..64....7.59.8326.',
                                '3..........5..9...2..5.4....2....7..16.....587.431.6.....89.1......67.8......5437',
                                '63..........5....8..5674.......2......34.1.2.......345.....7..4.8.3..9.29471...8.',
                                '....2..4...8.35.......7.6.2.31.4697.2...........5.12.3.49...73........1.8....4...',
                                '361.259...8.96..1.4......57..8...471...6.3...259...8..74......5.2..18.6...547.329',
                                '.5.8.7.2.6...1..9.7.254...6.7..2.3.15.4...9.81.3.8..7.9...762.5.6..9...3.8.1.3.4.',
                                '.8...5........3457....7.8.9.6.4..9.3..7.1.5..4.8..7.2.9.1.2....8423........1...8.',
                                '..35.29......4....1.6...3.59..251..8.7.4.8.3.8..763..13.8...1.4....2......51.48..',
                                '...........98.51...519.742.29.4.1.65.........14.5.8.93.267.958...51.36...........',
                                '.2..3..9....9.7...9..2.8..5..48.65..6.7...2.8..31.29..8..6.5..7...3.9....3..2..5.',
                                '..5.....6.7...9.2....5..1.78.415.......8.3.......928.59.7..6....3.4...1.2.....6..',
                                '.4.....5...19436....9...3..6...5...21.3...5.68...2...7..5...2....24367...3.....4.',
                                '..4..........3...239.7...8.4....9..12.98.13.76..2....8.1...8.539...4..........8..',
                                '36..2..89...361............8.3...6.24..6.3..76.7...1.8............418...97..3..14',
                                '5..4...6...9...8..64..2.........1..82.8...5.17..5.........9..84..3...6...6...3..2',
                                '..72564..4.......5.1..3..6....5.8.....8.6.2.....1.7....3..7..9.2.......4..63127..',
                                '..........79.5.18.8.......7..73.68..45.7.8.96..35.27..7.......5.16.3.42..........',
                                '.3.....8...9...5....75.92..7..1.5..8.2..9..3.9..4.2..1..42.71....2...8...7.....9.',
                                '2..17.6.3.5....1.......6.79....4.7.....8.1.....9.5....31.4.......5....6.9.6.37..2',
                                '.......8.8..7.1.4..4..2..3.374...9......3......5...321.1..6..5..5.8.2..6.8.......',
                                '.......85...21...996..8.1..5..8...16.........89...6..7..9.7..523...54...48.......',
                                '6.8.7.5.2.5.6.8.7...2...3..5...9...6.4.3.2.5.8...5...3..5...2...1.7.4.9.4.9.6.7.1',
                                '.5..1..4.1.7...6.2...9.5...2.8.3.5.1.4..7..2.9.1.8.4.6...4.1...3.4...7.9.2..6..1.',
                                '.53...79...97534..1.......2.9..8..1....9.7....8..3..7.5.......3..76412...61...94.',
                                '..6.8.3...49.7.25....4.5...6..317..4..7...8..1..826..9...7.2....75.4.19...3.9.6..',
                                '..5.8.7..7..2.4..532.....84.6.1.5.4...8...5...7.8.3.1.45.....916..5.8..7..3.1.6..',
                                '...9..8..128..64...7.8...6.8..43...75.......96...79..8.9...4.1...36..284..1..7...',
                                '....8....27.....54.95...81...98.64...2.4.3.6...69.51...17...62.46.....38....9....',
                                '...6.2...4...5...1.85.1.62..382.671...........194.735..26.4.53.9...2...7...8.9...',
                                '...9....2.5.1234...3....16.9.8.......7.....9.......2.5.91....5...7439.2.4....7...',
                                '38..........4..785..9.2.3...6..9....8..3.2..9....4..7...1.7.5..495..6..........92',
                                '...158.....2.6.8...3.....4..27.3.51...........46.8.79..5.....8...4.7.1.....325...',
                                '.1.5..2..9....1.....2..8.3.5...3...7..8...5..6...8...4.4.1..7.....7....6..3..4.5.',
                                '.8.....4....469...4.......7..59.46...7.6.8.3...85.21..9.......5...781....6.....1.',
                                '9.42....7.1..........7.65.....8...9..2.9.4.6..4...2.....16.7..........3.3....57.2',
                                '...7..8....6....31.4...2....24.7.....1..3..8.....6.29....8...7.86....5....2..6...',
                                '..1..7.9.59..8...1.3.....8......58...5..6..2...41......8.....3.1...2..79.2.7..4..',
                                '.....3.17.15..9..8.6.......1....7.....9...2.....5....4.......2.5..6..34.34.2.....',
                                '3..2........1.7...7.6.3.5...7...9.8.9...2...4.1.8...5...9.4.3.1...7.2........8..6']
            self.hard = ['4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......',
                         '52...6.........7.13...........4..8..6......5...........418.........3..2...87.....',
                         '6.....8.3.4.7.................5.4.7.3..2.....1.6.......2.....5.....8.6......1....',
                         '48.3............71.2.......7.5....6....2..8.............1.76...3.....4......5....',
                         '....14....3....2...7..........9...3.6.1.............8.2.....1.4....5.6.....7.8...',
                         '......52..8.4......3...9...5.1...6..2..7........3.....6...1..........7.4.......3.',
                         '6.2.5.........3.4..........43...8....1....2........7..5..27...........81...6.....',
                         '.524.........7.1..............8.2...3.....6...9.5.....1.6.3...........897........',
                         '6.2.5.........4.3..........43...8....1....2........7..5..27...........81...6.....',
                         '.923.........8.1...........1.7.4...........658.........6.5.2...4.....7.....9.....',
                         '6..3.2....5.....1..........7.26............543.........8.15........4.2........7..',
                         '.6.5.1.9.1...9..539....7....4.8...7.......5.8.817.5.3.....5.2............76..8...',
                         '..5...987.4..5...1..7......2...48....9.1.....6..2.....3..6..2.......9.7.......5..',
                         '3.6.7...........518.........1.4.5...7.....6.....2......2.....4.....8.3.....5.....',
                         '1.....3.8.7.4..............2.3.1...........958.........5.6...7.....8.2...4.......',
                         '6..3.2....4.....1..........7.26............543.........8.15........4.2........7..',
                         '....3..9....2....1.5.9..............1.2.8.4.6.8.5...2..75......4.1..6..3.....4.6.',
                         '45.....3....8.1....9...........5..9.2..7.....8.........1..4..........7.2...6..8..',
                         '.237....68...6.59.9.....7......4.97.3.7.96..2.........5..47.........2....8.......',
                         '..84...3....3.....9....157479...8........7..514.....2...9.6...2.5....4......9..56',
                         '.98.1....2......6.............3.2.5..84.........6.........4.8.93..5...........1..',
                         '..247..58..............1.4.....2...9528.9.4....9...1.........3.3....75..685..2...',
                         '4.....8.5.3..........7......2.....6.....5.4......1.......6.3.7.5..2.....1.9......',
                         '.2.3......63.....58.......15....9.3....7........1....8.879..26......6.7...6..7..4',
                         '1.....7.9.4...72..8.........7..1..6.3.......5.6..4..2.........8..53...7.7.2....46',
                         '4.....3.....8.2......7........1...8734.......6........5...6........1.4...82......',
                         '.......71.2.8........4.3...7...6..5....2..3..9........6...7.....8....4......5....',
                         '6..3.2....4.....8..........7.26............543.........8.15........8.2........7..',
                         '.47.8...1............6..7..6....357......5....1..6....28..4.....9.1...4.....2.69.',
                         '......8.17..2........5.6......7...5..1....3...8.......5......2..4..8....6...3....',
                         '38.6.......9.......2..3.51......5....3..1..6....4......17.5..8.......9.......7.32',
                         '...5...........5.697.....2...48.2...25.1...3..8..3.........4.7..13.5..9..2...31..',
                         '.2.......3.5.62..9.68...3...5..........64.8.2..47..9....3.....1.....6...17.43....',
                         '.8..4....3......1........2...5...4.69..1..8..2...........3.9....6....5.....2.....',
                         '..8.9.1...6.5...2......6....3.1.7.5.........9..4...3...5....2...7...3.8.2..7....4',
                         '4.....5.8.3..........7......2.....6.....5.8......1.......6.3.7.5..2.....1.8......',
                         '1.....3.8.6.4..............2.3.1...........958.........5.6...7.....8.2...4.......',
                         '1....6.8..64..........4...7....9.6...7.4..5..5...7.1...5....32.3....8...4........',
                         '249.6...3.3....2..8.......5.....6......2......1..4.82..9.5..7....4.....1.7...3...',
                         '...8....9.873...4.6..7.......85..97...........43..75.......3....3...145.4....2..1',
                         '...5.1....9....8...6.......4.1..........7..9........3.8.....1.5...2..4.....36....',
                         '......8.16..2........7.5......6...2..1....3...8.......2......7..3..8....5...4....',
                         '.476...5.8.3.....2.....9......8.5..6...1.....6.24......78...51...6....4..9...4..7',
                         '.....7.95.....1...86..2.....2..73..85......6...3..49..3.5...41724................',
                         '.4.5.....8...9..3..76.2.....146..........9..7.....36....1..4.5..6......3..71..2..',
                         '.834.........7..5...........4.1.8..........27...3.....2.6.5....5.....8........1..',
                         '..9.....3.....9...7.....5.6..65..4.....3......28......3..75.6..6...........12.3.8',
                         '.26.39......6....19.....7.......4..9.5....2....85.....3..2..9..4....762.........4',
                         '2.3.8....8..7...........1...6.5.7...4......3....1............82.5....6...1.......',
                         '6..3.2....1.....5..........7.26............843.........8.15........8.2........7..',
                         '1.....9...64..1.7..7..4.......3.....3.89..5....7....2.....6.7.9.....4.1....129.3.',
                         '.........9......84.623...5....6...453...1...6...9...7....1.....4.5..2....3.8....9',
                         '.2....5938..5..46.94..6...8..2.3.....6..8.73.7..2.........4.38..7....6..........5',
                         '9.4..5...25.6..1..31......8.7...9...4..26......147....7.......2...3..8.6.4.....9.',
                         '...52.....9...3..4......7...1.....4..8..453..6...1...87.2........8....32.4..8..1.',
                         '53..2.9...24.3..5...9..........1.827...7.........981.............64....91.2.5.43.',
                         '1....786...7..8.1.8..2....9........24...1......9..5...6.8..........5.9.......93.4',
                         '....5...11......7..6.....8......4.....9.1.3.....596.2..8..62..7..7......3.5.7.2..',
                         '.47.2....8....1....3....9.2.....5...6..81..5.....4.....7....3.4...9...1.4..27.8..',
                         '......94.....9...53....5.7..8.4..1..463...........7.8.8..7.....7......28.5.26....',
                         '.2......6....41.....78....1......7....37.....6..412....1..74..5..8.5..7......39..',
                         '1.....3.8.6.4..............2.3.1...........758.........7.5...6.....8.2...4.......',
                         '2....1.9..1..3.7..9..8...2.......85..6.4.........7...3.2.3...6....5.....1.9...2.5',
                         '..7..8.....6.2.3...3......9.1..5..6.....1.....7.9....2........4.83..4...26....51.',
                         '...36....85.......9.4..8........68.........17..9..45...1.5...6.4....9..2.....3...',
                         '34.6.......7.......2..8.57......5....7..1..2....4......36.2..1.......9.......7.82',
                         '......4.18..2........6.7......8...6..4....3...1.......6......2..5..1....7...3....',
                         '.4..5..67...1...4....2.....1..8..3........2...6...........4..5.3.....8..2........',
                         '.......4...2..4..1.7..5..9...3..7....4..6....6..1..8...2....1..85.9...6.....8...3',
                         '8..7....4.5....6............3.97...8....43..5....2.9....6......2...6...7.71..83.2',
                         '.8...4.5....7..3............1..85...6.....2......4....3.26............417........',
                         '....7..8...6...5...2...3.61.1...7..2..8..534.2..9.......2......58...6.3.4...1....',
                         '......8.16..2........7.5......6...2..1....3...8.......2......7..4..8....5...3....',
                         '.2..........6....3.74.8.........3..2.8..4..1.6..5.........1.78.5....9..........4.',
                         '.52..68.......7.2.......6....48..9..2..41......1.....8..61..38.....9...63..6..1.9',
                         '....1.78.5....9..........4..2..........6....3.74.8.........3..2.8..4..1.6..5.....',
                         '1.......3.6.3..7...7...5..121.7...9...7........8.1..2....8.64....9.2..6....4.....',
                         '4...7.1....19.46.5.....1......7....2..2.3....847..6....14...8.6.2....3..6...9....',
                         '......8.17..2........5.6......7...5..1....3...8.......5......2..3..8....6...4....',
                         '963......1....8......2.5....4.8......1....7......3..257......3...9.2.4.7......9..',
                         '15.3......7..4.2....4.72.....8.........9..1.8.1..8.79......38...........6....7423',
                         '..........5724...98....947...9..3...5..9..12...3.1.9...6....25....56.....7......6',
                         '....75....1..2.....4...3...5.....3.2...8...1.......6.....1..48.2........7........',
                         '6.....7.3.4.8.................5.4.8.7..2.....1.3.......2.....5.....7.9......1....',
                         '....6...4..6.3....1..4..5.77.....8.5...8.....6.8....9...2.9....4....32....97..1..',
                         '.32.....58..3.....9.428...1...4...39...6...5.....1.....2...67.8.....4....95....6.',
                         '...5.3.......6.7..5.8....1636..2.......4.1.......3...567....2.8..4.7.......2..5..',
                         '.5.3.7.4.1.........3.......5.8.3.61....8..5.9.6..1........4...6...6927....2...9..',
                         '..5..8..18......9.......78....4.....64....9......53..2.6.........138..5....9.714.',
                         '..........72.6.1....51...82.8...13..4.........37.9..1.....238..5.4..9.........79.',
                         '...658.....4......12............96.7...3..5....2.8...3..19..8..3.6.....4....473..',
                         '.2.3.......6..8.9.83.5........2...8.7.9..5........6..4.......1...1...4.22..7..8.9',
                         '.5..9....1.....6.....3.8.....8.4...9514.......3....2..........4.8...6..77..15..6.',
                         '.....2.......7...17..3...9.8..7......2.89.6...13..6....9..5.824.....891..........',
                         '3...8.......7....51..............36...2..4....7...........6.13..452...........8..']

        elif size == 16:
            self.easy = ['D.8.GC.9..A.E7..659C.7BF.4...3.AG....34.B8.7D..F.B.E1D..9...42....1D.....6..953C89EF..7.D.3A.....45.D.A68.1..E.G7...2.F34...8..D5..B6G1DC794...E.G28E.C.F3B..4D.4...F.....E.5.G..3D..2.86AG.BFC.B7.....1.2D..G862.C.3..B..891D.....6..D...5BF9.2.DG.A..21.4..B73']
            self.hard = ['.E5G.....967.14..6...EA..5.B73..B..2...1..3.65G...9.C...E.F.A.....AD.....E.5.F......8DC...G.......1E...B4C..G98.....3F...8...D.1.....5..D......C....G.F..1......E.8.A2..F6......7.63B9..G.C.1..A57..2..E.F9.4.....294C..6..........4..D.1....G.7C......3..AD9.B2',
                         '4.9F....2..D.C.B.86.B..2.E.9..A....BF6C..1...7.37.A...45..G.....12..6.7..4..F.....3..2E1......5..5C.G..8.....A..96.D4...F3.A.....G..3...1.E2.48.....9.....8.E..C..5.............B..4.1..7.....95..FE7DA.C..19....A....9....3D54.........9..7B..E61..8....D..3.G.', '2E.C.....8.....7.46B.D.G..F....1...13.5..6..D29B5....CE..3......39..C....G..5...6.......7....9..E2B..3D.1.8.........B...59...F1D8.47.A..9..3B..........E.B...4.........76.D..1CE.3F.5.91......8G7.8A.1....6G...2.6...E2.3.1D.C...D.....A.24....9...34B......6...']

        self.size = size

    def main(self, solver, difficulty='all'):
        print('****************************************\n')
        if difficulty == 'easy' or difficulty == 'all':
            for i, p in enumerate(self.easy):
                print('             EASY PROBLEM {}'.format(str(i)))
                self.solve(solver, p, 'easy{}_{}.cnf'.format(str(self.size), str(i)))

        if difficulty == 'hard' or difficulty == 'all':
            for i, p in enumerate(self.hard):
                print('             HARD PROBLEM {}'.format(str(i)))
                self.solve(solver, p, 'hard{}_{}.cnf'.format(str(self.size), str(i)))

    def solve(self, solver, problem, filename):
        print('\n****************************************')
        if self.size == 9:
            print("====Problem====")
        elif self.size == 16:
            print("=========Problem=========")
        g = Grid(problem, self.size)
        g.display()
        s = solver(g, self.size, filename)
        solved = s.solve()
        if solved[1]:
            if self.size == 9:
                print("====Solution===")
            elif self.size == 16:
                print("=========Solution=========")
            assert all(s.consistent(s.sigma, spot, s.sigma[spot]) for spot in s.sigma)
            self.display_solution(s.sigma)
        else:
            print("=======No solution=======")

        return solved[0]

    def display_solution(self, d):
        for i in range(0, self.size):
            for j in range(0, self.size):
                s = MAP[d[(i + 1, j + 1)]]
                print(s, end='')
                if self.size == 9:
                    if j == 2 or j == 5:
                        print(" | ", end='')
                elif self.size == 16:
                    if j == 3 or j == 7 or j == 11:
                        print(" | ", end='')
            print()
            if self.size == 9:
                if i == 2 or i == 5:
                    print("---------------")
            elif self.size == 16:
                if i == 3 or i == 7 or i == 11:
                    print("-------------------------")

        print('****************************************\n')


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
            solver1 = Solver(g, size, '')
            solver2 = Solver2(g, size, '')
            solver3 = Solver3(g, size, '{}{}_{}.cnf'.format(dif, str(size), str(i)))

            t1, _ = solver1.solve()
            t2, _ = solver2.solve()
            t3, _ = solver3.solve()

            # self.times[dif + str(size) + str(1)].append(int(t1 * 1000))
            self.times[dif + str(size) + str(2)].append(int(t2 * 1000))
            self.times[dif + str(size) + str(3)].append(int(t3 * 1000))

    def plot(self, dif='hard', size=9):
        self.time(dif, size)

        t1 = self.times[dif + str(size) + '1']
        t2 = self.times[dif + str(size) + '2']
        t3 = self.times[dif + str(size) + '3']

        ind = np.arange(len(t2))  # the x locations for the groups
        width = 0.5  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(ind - width / 2, t2, width,
                        color='b', label='Solver 1')
        rects2 = ax.bar(ind - width / 2, t2, width,
                        color='r', label='Solver 2')
        rects3 = ax.bar(ind + width / 2, t3, width,
                        color='g', label='Solver 3')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Time (miliseconds)')
        ax.set_title('{} Problems {}'.format(dif.upper(), '{}X{}'.format(str(size), str(size))))
        ax.legend()

        plt.show()

    def plot_all(self):
        self.plot('easy', 9)
        self.plot('hard', 9)

        self.plot('easy', 16)
        self.plot('hard', 16)


''' Use Benchamrk().plot_all() to see the graphs.'''
#Benchmark().plot('easy', 9)
# Benchmark().plot_all()

''' Use Sudoku().main() to solve all problems using a specific solver'''
# Sudoku(9).main(Solver)  # You wouldn't want to do this!!
# Sudoku(9).main(Solver) # It would take FOREVER

# Sudoku(9).main(Solver2)
# Sudoku(16).main(Solver2)
#
# Sudoku(9).main(Solver3)
# Sudoku(16).main(Solver3)

''' Use Sudoku().solve([solver], [problem], [filename]) to solve one problem.'''
Sudoku(9).solve(Solver, Sudoku(9).easy[1], 'test')
# Sudoku(9).solve(Solver2, Sudoku(9).easy[1], 'test')
# Sudoku(9).solve(Solver3, Sudoku(9).easy[1], 'test')
