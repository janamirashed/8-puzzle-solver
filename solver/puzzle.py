# puzzle.py
from enum import Enum
from math import isqrt, sqrt
BLANK = 0
class Move(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

    @property
    def dr(self):
        return self.value[0]

    @property
    def dc(self):
        return self.value[1]

    @property
    def name(self):
        return super().name.capitalize()

class PuzzleState:
    # tracks the board, parent state, move made, cost g(n), and f(n) for A*
    def __init__(self, board, parent_state=None, move=None, g=0, h=0):
        self.board = tuple(board)
        self.parentState = parent_state
        self.move = move
        self.g = g
        self.h = h
        self.f = g + h
        self.size = isqrt(len(self.board))     # isqrt returns an integer

    def is_goal(self):
        n = len(self.board)
        return self.board == (BLANK,) + tuple(range(1, n))

    # generates all reachable boards in one move
    def get_children(self, heuristic=None):
        children = []
        size = self.size
        blank = self.board.index(BLANK)  # the index of the gap on the board
        row, col = divmod(blank, size) # converts the flat index to (row, col)

        for move in Move:
            new_row, new_col = row + move.dr, col + move.dc
            if 0 <= new_row < size and 0 <= new_col < size: # valid movement
                new_blank = new_row * size + new_col
                new_board = list(self.board)
                new_board[blank], new_board[new_blank] = new_board[new_blank], new_board[blank]   # swap
                h = heuristic(tuple(new_board)) if heuristic else 0
                children.append(PuzzleState(new_board, self, move, self.g + 1, h))
        return children


# sum of horizontal and vertical distances of tiles from their goal positions
def manhattan_distance(board):
    size = isqrt(len(board))
    total = 0
    for i, tile in enumerate(board):
        if tile == BLANK:
            continue
        row, col = divmod(i, size)
        goal_row, goal_col = divmod(tile, size)
        total += abs(row - goal_row) + abs(col - goal_col)
    return total


# sum of straight-line distances of tiles from their goal positions
def euclidean_distance(board):
    size = isqrt(len(board))
    total = 0.0
    for i, tile in enumerate(board):
        if tile == BLANK:
            continue
        row, col = divmod(i, size)
        goal_row, goal_col = divmod(tile, size)
        total += sqrt((row - goal_row) ** 2 + (col - goal_col) ** 2)
    return total


# returns True if solvable (inversion count is even, ignoring BLANK)
def is_solvable(board):
    tiles = [t for t in board if t != BLANK]
    inversions = sum(
        1
        for i in range(len(tiles))
        for j in range(i + 1, len(tiles))
        if tiles[i] > tiles[j]
    )
    size = isqrt(len(board))
    if size % 2 == 1:
        return inversions % 2 == 0
    blank_row_from_top = board.index(BLANK) // size
    return (inversions + blank_row_from_top) % 2 == 0


# walks back through .parent pointers from goal to root and reverses the path
def trace_path(state):
    path = []
    while state is not None:
        path.append(state)
        state = state.parentState
    path.reverse()
    return path