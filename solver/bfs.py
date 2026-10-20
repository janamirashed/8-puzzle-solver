# bfs.py
import time
from collections import deque
from itertools import islice
from .puzzle import PuzzleState, trace_path, is_solvable
from .tracer import Tracer


def peek(queue, n):
    # bfs removes from the front, so the first n entries are the next to be expanded
    return list(islice(queue, n))


def solve(initial_board):
    # check if the puzzle is solvable first using inversion parity
    if not is_solvable(initial_board):
        return None

    start_time = time.time()
    initial_state = PuzzleState(initial_board)
    tracer = Tracer("Queue (front first)", peek)

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

    # fifo queue using deque for o(1) popleft
    queue = deque([initial_state])
    # visited set to avoid expanding the same board state twice (graph search)
    visited = {initial_state.board}
    nodes_expanded = 0
    max_search_depth = 0

    while queue:
        # take the shallowest node from the front of the queue
        current = queue.popleft()
        nodes_expanded += 1
        tracer.begin_step(current)

        # generate valid neighbors in order: up, down, left, right
        for child in current.get_children():
            if child.g > max_search_depth:
                max_search_depth = child.g

            # textbook bfs optimization: check for goal on generation instead of expansion
            if child.is_goal():
                tracer.child(child, "goal")
                tracer.end_step(queue, nodes_expanded)
                # backtrack parent pointers to reconstruct the full solution path
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

            # only add child to queue if we haven't seen this board configuration before
            if child.board in visited:
                status = "visited"        # already generated earlier
            else:
                status = "queued"
                visited.add(child.board)
                queue.append(child)
            tracer.child(child, status)

        tracer.end_step(queue, nodes_expanded)

    return None