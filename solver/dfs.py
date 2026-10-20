# dfs.py
import time
from itertools import islice
from .puzzle import PuzzleState, trace_path, is_solvable
from .tracer import Tracer

def peek(stack, n):
    # dfs uses a lifo stack, so the top items (end of list) are the next to be expanded
    return [state for state in stack[-n:]]

def solve(initial_board, depth_limit=50, tracer=None):
    initial_board = tuple(initial_board)
    # verify solvability before searching
    if not is_solvable(initial_board):
        return None

    start_time = time.time()
    initial_state = PuzzleState(initial_board)

    if tracer is None: tracer = Tracer("Stack (bottom → top)", peek, next_at="last")

    # return immediately if initial state is already the goal
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

    # lifo stack for dfs
    stack = [initial_state]
    # track the minimum depth each board was reached at to avoid loops without blocking better paths
    explored_depth = {}
    nodes_expanded = 0
    max_search_depth = 0

    while stack:
        # pop the most recently added state (top of the stack)
        current = stack.pop()
        # skip if we already expanded this board at a shallower or equal depth
        if current.board in explored_depth and explored_depth[current.board] <= current.g:
            continue

        explored_depth[current.board] = current.g
        nodes_expanded += 1
        tracer.begin_step(current)
        if current.g > max_search_depth:
            max_search_depth = current.g

        # goal check on node expansion
        if current.is_goal():
            # trace back parent pointers from goal to root
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

        # only explore children if within depth limit
        if current.g < depth_limit:
            # reverse children so they are popped in natural expansion order: up, down, left, right
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