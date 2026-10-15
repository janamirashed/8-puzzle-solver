# bfs.py
import time
from collections import deque
from itertools import islice
from .puzzle import PuzzleState, trace_path, is_solvable
from .tracer import Tracer


def peek(queue, n):
    # BFS removes from the front, so the first n entries are the next to be expanded
    return list(islice(queue, n))


def solve(initial_board):
    if not is_solvable(initial_board):
        return None

    start_time = time.time()
    initial_state = PuzzleState(initial_board)
    tracer = Tracer("Queue (front first)", peek)

    if initial_state.is_goal():
        return {
            "path": [list(initial_board)],
            "moves": [],
            "cost": 0,
            "nodes_expanded": 0,
            "search_depth": 0,
            "running_time": round(time.time() - start_time, 5),
            "trace": tracer.result(),
        }

    queue = deque([initial_state])
    visited = {initial_state.board}
    nodes_expanded = 0
    max_search_depth = 0

    while queue:
        current = queue.popleft()
        nodes_expanded += 1
        tracer.begin_step(current)

        for child in current.get_children():
            if child.g > max_search_depth:
                max_search_depth = child.g

            # goal check on generation is faster
            if child.is_goal():
                tracer.child(child, "goal")
                tracer.end_step(queue, nodes_expanded)
                states = trace_path(child)
                path = [list(s.board) for s in states]
                moves = [s.move.name.capitalize() for s in states if s.move is not None]
                return {
                    "path": path,
                    "moves": moves,
                    "cost": child.g,
                    "nodes_expanded": nodes_expanded,
                    "search_depth": max_search_depth,
                    "running_time": round(time.time() - start_time, 5),
                    "trace": tracer.result(),
                }

            if child.board in visited:
                status = "visited"        # already generated earlier
            else:
                status = "queued"
                visited.add(child.board)
                queue.append(child)
            tracer.child(child, status)

        tracer.end_step(queue, nodes_expanded)

    return None