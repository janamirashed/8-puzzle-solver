# astar.py — a* search

import heapq
from .puzzle import PuzzleState, trace_path, is_solvable, manhattan_distance, euclidean_distance

HEURISTICS = {
    "manhattan": manhattan_distance,
    "euclidean": euclidean_distance,
}


def solve(initial_board, heuristic="manhattan"):
    # todo: implement a* using priority queue (heapq)
    pass
