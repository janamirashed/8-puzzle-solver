# idfs.py
import time
from .puzzle import is_solvable
from . import dfs

def solve(initial_board, max_depth=100):
    initial_board = tuple(initial_board)
    if not is_solvable(initial_board):
        return None

    start_time = time.time()
    total_nodes_expanded = 0
    max_search_depth = 0

    for depth in range(max_depth + 1):
        result = dfs.solve(initial_board, depth_limit=depth)

        if result is not None:
            total_nodes_expanded += result["nodes_expanded"]
            max_search_depth = max(max_search_depth, result["search_depth"])

            # If a valid path is found, return accumulated metrics
            if result["path"]:
                result["nodes_expanded"] = total_nodes_expanded
                result["search_depth"] = max_search_depth
                result["running_time"] = round(time.time() - start_time, 5)
                return result

    return None