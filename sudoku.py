from __future__ import print_function
import random, copy

class Grid:
	def __init__(self, problem):
		self.spots = [(i, j) for i in range(1,10) for j in range(1,10)]
		self.domains = {}
		#Need a dictionary that maps each spot to its related spots
		self.peers = {} 
		self.parse(problem)
	def parse(self, problem):
		for i in range(0, 9):
			for j in range(0, 9):
				c = problem[i*9+j] 
				if c == '.':
					self.domains[(i+1, j+1)] = range(1,10)
				else:
					self.domains[(i+1, j+1)] = [ord(c)-48]
	def display(self):
		for i in range(0, 9):
			for j in range(0, 9):
				d = self.domains[(i+1,j+1)]
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
		#sigma is the assignment function
		self.sigma = {}
		self.grid = grid
	def solve(self):
		return True
	def search(self, sigma):
		pass
	def consistent(self, spot, value, sigma):
		pass
	def infer(self, sigma):
		pass

easy = ["..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..",
"2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3"]

hard = ["4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......",
"52...6.........7.13...........4..8..6......5...........418.........3..2...87....."]

print("====Problem====")
g = Grid(easy[0])
#Display the original problem
g.display()
s = Solver(g)
if s.solve():
	print("====Solution===")
	#Display the solution
	#Feel free to call other functions to display
	g.display()
else:
	print("==No solution==")

