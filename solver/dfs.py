# dfs.py
import time
from .puzzle import PuzzleState, trace_path, is_solvable


def solve(initial_board, depth_limit=50):
    if not is_solvable(initial_board):
        return None

    start_time = time.time()
    initial_state = PuzzleState(initial_board)

    if initial_state.is_goal():
        return {
            "path": [list(initial_board)],
            "moves": [],
            "cost": 0,
            "nodes_expanded": 0,
            "search_depth": 0,
            "running_time": round(time.time() - start_time, 5),
        }

    stack = [initial_state]
    visited = {initial_state.board}
    nodes_expanded = 0
    max_search_depth = 0

    while stack:
        current = stack.pop()
        nodes_expanded += 1

        if current.g > max_search_depth:
            max_search_depth = current.g

        if current.is_goal():
            states = trace_path(current)
            path = [list(s.board) for s in states]
            moves = [s.move.name.capitalize() for s in states if s.move is not None]
            return {
                "path": path,
                "moves": moves,
                "cost": current.g,
                "nodes_expanded": nodes_expanded,
                "search_depth": max_search_depth,
                "running_time": round(time.time() - start_time, 5),
            }

        if current.g < depth_limit:
            # reverse children so they pop in natural order
            for child in reversed(current.get_children()):
                if child.board not in visited:
                    visited.add(child.board)
                    stack.append(child)

    return None
