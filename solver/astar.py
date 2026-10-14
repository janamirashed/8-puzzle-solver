# astar.py
import heapq
import itertools
from .puzzle import PuzzleState, trace_path, is_solvable, manhattan_distance, euclidean_distance

HEURISTICS = {
    "manhattan": manhattan_distance,
    "euclidean": euclidean_distance,
}

def solve(initial_board, heuristic="manhattan"):
    if heuristic not in HEURISTICS:
        raise ValueError(f"Unknown heuristic '{heuristic}'. Choose from {list(HEURISTICS)}")
    h = HEURISTICS[heuristic]

    initial_board = tuple(initial_board)
    if not is_solvable(initial_board):
        return None

    start = PuzzleState(initial_board, g=0, h=h(initial_board))

    counter = itertools.count()                  # tie-breaker for equal f values
    frontier = [(start.f, next(counter), start)]
    best_g = {start.board: 0}
    explored = set()
    nodes_expanded = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)

        if current.board in explored:
            continue
        explored.add(current.board)
        nodes_expanded += 1

        if current.is_goal():
            states = trace_path(current)
            return {
                "path": [s.board for s in states],           # boards from start to goal
                "moves": [s.move for s in states[1:]],       # blank moves taken
                "cost": current.g,
                "nodes_expanded": nodes_expanded,
            }

        for child in current.get_children(h):
            if child.board in explored:
                continue
            if child.g < best_g.get(child.board, float("inf")):
                best_g[child.board] = child.g
                heapq.heappush(frontier, (child.f, next(counter), child))

    return None