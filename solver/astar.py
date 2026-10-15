# astar.py — A* search
import heapq
import itertools
import time
from .puzzle import PuzzleState, trace_path, is_solvable, manhattan_distance, euclidean_distance
from .tracer import Tracer

HEURISTICS = {
    "manhattan": manhattan_distance,
    "euclidean": euclidean_distance,
}

def _peek(frontier, n):
    return [s for _, _, s in heapq.nsmallest(n, frontier)]


def solve(initial_board, heuristic="manhattan"):
    if heuristic not in HEURISTICS:
        raise ValueError(f"Unknown heuristic '{heuristic}'. Choose from {list(HEURISTICS)}")
    h = HEURISTICS[heuristic]

    if not is_solvable(initial_board):
        return None

    start_time = time.perf_counter()
    start = PuzzleState(initial_board, g=0, h=h(initial_board))
    tracer = Tracer("Frontier (priority queue, best f first)", _peek, heuristic, start.h)

    # already solved
    if start.is_goal():
        return {
            "path": [list(start.board)],
            "moves": [],
            "cost": 0,
            "nodes_expanded": 0,
            "search_depth": 0,
            "running_time": round(time.perf_counter() - start_time, 5),
            "trace": tracer.result(),
        }

    counter = itertools.count()  # tie-breaker
    frontier = [(start.f, next(counter), start)]
    best_g = {start.board: 0}    # cheapest g found so far for each board
    explored = set()
    nodes_expanded = 0
    max_search_depth = 0

    while frontier:
        _, _, current = heapq.heappop(frontier)

        if current.board in explored:
            continue
        if current.g > best_g.get(current.board, float("inf")):
            continue

        explored.add(current.board)
        nodes_expanded += 1
        tracer.begin_step(current, nodes_expanded)

        if current.is_goal():
            tracer.end_step(frontier, len(explored), goal=True)
            states = trace_path(current)
            return {
                "path": [list(s.board) for s in states],
                "moves": [s.move.label for s in states[1:]],
                "cost": current.g,
                "nodes_expanded": nodes_expanded,
                "search_depth": max_search_depth,
                "running_time": round(time.perf_counter() - start_time, 5),
                "trace": tracer.result(),
            }

        for child in current.get_children(h):
            if child.board in explored:
                status = "explored"
            elif child.g >= best_g.get(child.board, float("inf")):
                status = "worse"
                continue;
            else:
                status = "queued"
                best_g[child.board] = child.g
                max_search_depth = max(max_search_depth, child.g)
                heapq.heappush(frontier, (child.f, next(counter), child))
            tracer.child(child, status)

        tracer.end_step(frontier, len(explored))

    return None