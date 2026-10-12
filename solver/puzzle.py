# puzzle.py — core puzzle logic and helper functions

class PuzzleState:
    # tracks the board, parent node, move made, cost g(n), and f(n) for A*
    pass


# sum of horizontal and vertical distances of tiles from their goal positions
def manhattan_distance(board):
    pass


# sum of straight-line distances of tiles from their goal positions
def euclidean_distance(board):
    pass


# returns True if solvable (inversion count is even, ignoring 0)
def is_solvable(board):
    pass


# walks back through .parent pointers from goal to root and reverses the path
def trace_path(state):
    pass
