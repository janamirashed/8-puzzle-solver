import time
from itertools import islice
from .puzzle import PuzzleState, trace_path, is_solvable
from .tracer import Tracer

def peek(stack, n):
    return [state for state in stack[-n:]]

def solve(initial_board, depth_limit=50, tracer=None):
    initial_board = tuple(initial_board)
    if not is_solvable(initial_board):
        return None

    start_time = time.time()
    initial_state = PuzzleState(initial_board)

    if tracer is None: tracer = Tracer("Stack (bottom → top)", peek, next_at="last")

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

    stack = [initial_state]
    explored_depth = {}
    nodes_expanded = 0
    max_search_depth = 0

    while stack:
        current = stack.pop()
        if current.board in explored_depth and explored_depth[current.board] <= current.g:
            continue

        explored_depth[current.board] = current.g
        nodes_expanded += 1
        tracer.begin_step(current)
        if current.g > max_search_depth:
            max_search_depth = current.g

        if current.is_goal():
            states = trace_path(current)
            path = [list(s.board) for s in states]
            moves = [str(s.move.name if hasattr(s.move, "name") else s.move) for s in states[1:]]
            return {
                "path": path,
                "moves": moves,
                "cost": current.g,
                "nodes_expanded": nodes_expanded,
                "search_depth": max_search_depth,
                "running_time": round(time.time() - start_time, 5),
                "trace": tracer.result(),
            }

        if current.g < depth_limit:
            # Reverse children so they are popped in natural expansion order
            for child in reversed(current.get_children()):
                if child.board in explored_depth and explored_depth[child.board] <= child.g:
                    status = "visited"
                else:
                    status = "queued"
                    stack.append(child)
                tracer.child(child, status)
        tracer.end_step(stack, len(explored_depth))

    return None



# 4, 3, 2, 1, 7, 5, 0, 6, 8