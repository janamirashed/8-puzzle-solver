# tracer.py

MAX_STEPS = 200
FRONTIER_PREVIEW = 6

class Tracer:
    def __init__(self, structure, peek, heuristic=None, initial_h=None,
                 max_steps=MAX_STEPS, preview=FRONTIER_PREVIEW, next_at="first"):
        self.structure = structure
        self.peek = peek
        self.heuristic = heuristic
        self.initial_h = initial_h
        self.max_steps = max_steps
        self.preview = preview
        self.informed = heuristic is not None
        self.steps = []
        self._step = None
        self._total = 0
        self._label = None
        self._next_at = next_at

    def _costs(self, s):
        costs = {"g": s.g}
        if self.informed:
            costs["h"] = round(s.h, 2)
            costs["f"] = round(s.f, 2)
        return costs

    def begin_iteration(self, label):
        self._label = label

    def begin_step(self, state, number=None):
        # A* passes its own count; searches that restart (IDS) let the tracer count
        self._total = number if number is not None else self._total + 1
        self._step = None
        if len(self.steps) < self.max_steps:
            self._step = {"step": self._total, "board": list(state.board),
                          **self._costs(state), "goal": False, "children": []}
            if self._label:
                self._step["label"] = self._label

    def child(self, state, status):
        if self._step is not None:
            self._step["children"].append({
                "move": state.move.name, "board": list(state.board),
                **self._costs(state), "status": status,
            })

    def end_step(self, frontier, explored_size, goal=False):
        if self._step is None:
            return
        self._step["goal"] = goal
        self._step["frontier"] = [
            {"board": list(s.board), **self._costs(s)}
            for s in self.peek(frontier, self.preview)
        ]
        self._step["frontier_size"] = len(frontier)
        self._step["explored_size"] = explored_size
        self.steps.append(self._step)
        self._step = None

    def result(self):
        trace = {"structure": self.structure, "steps": self.steps,
                 "truncated": self._total > len(self.steps), "next_at": self._next_at}
        if self.informed:
            trace["heuristic"] = self.heuristic
            trace["initial_h"] = round(self.initial_h, 2)
        return trace