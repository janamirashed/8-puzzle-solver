# dfs.py
import time
from .puzzle import PuzzleState, trace_path, is_solvable


def solve(initial_board, depth_limit=50):
    initial_board = tuple(initial_board)
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

    stack = [(initial_state, {initial_state.board})]
    visited_depth = {}
    nodes_expanded = 0
    max_search_depth = 0

    while stack:
        current, path_visited = stack.pop()

        # Skip if we already expanded this board at a shallower depth
        if current.board in visited_depth and visited_depth[current.board] <= current.g:
            continue

        visited_depth[current.board] = current.g
        nodes_expanded += 1

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
            }

        if current.g < depth_limit:
            # Reverse children so they pop in natural order
            for child in reversed(current.get_children()):
                if child.board not in path_visited:
                    stack.append((child, path_visited | {child.board}))

    return None