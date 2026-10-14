# astar.py
import heapq
import itertools
import time
from .puzzle import PuzzleState, trace_path, is_solvable, manhattan_distance, euclidean_distance

HEURISTICS = {
    "manhattan": manhattan_distance,
    "euclidean": euclidean_distance,
}


def solve(initial_board, heuristic="manhattan"):
    if heuristic not in HEURISTICS:
        raise ValueError(f"Unknown heuristic '{heuristic}'. Choose from {list(HEURISTICS)}")
    h = HEURISTICS[heuristic]
    start_time = time.time()

    initial_board = tuple(initial_board)
    if not is_solvable(initial_board):
        return None

    start = PuzzleState(initial_board, g=0, h=h(initial_board))
    if start.is_goal():
        return {
            "path": [list(start.board)],
            "moves": [],
            "cost": 0,
            "nodes_expanded": 0,
            "search_depth": 0,
            "running_time": round(time.time() - start_time, 5),
        }

    counter = itertools.count()  # tie-breaker for equal f values
    frontier = [(start.f, next(counter), start)]
    best_g = {start.board: 0}  # cheapest cost g
    explored = set()
    nodes_expanded = 0
    max_search_depth = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)

        if current.board in explored:
            continue
        explored.add(current.board)
        nodes_expanded += 1

        if current.is_goal():
            states = trace_path(current)
            moves = [str(s.move.name if hasattr(s.move, "name") else s.move) for s in states[1:]]
            return {
                "path": [list(s.board) for s in states],
                "moves": moves,
                "cost": current.g,
                "nodes_expanded": nodes_expanded,
                "search_depth": max_search_depth,
                "running_time": round(time.time() - start_time, 5),
            }

        for child in current.get_children(h):
            if child.board in explored:
                continue
            if child.g < best_g.get(child.board, float("inf")):
                best_g[child.board] = child.g
                if child.g > max_search_depth:
                    max_search_depth = child.g
                heapq.heappush(frontier, (child.f, next(counter), child))

    return None