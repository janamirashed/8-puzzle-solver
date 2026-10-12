from flask import Flask, render_template, request, jsonify
from solver import bfs, dfs, idfs, astar
from solver.puzzle import is_solvable

app = Flask(__name__)

# map algorithm names from frontend to solver functions
SOLVERS = {
    "bfs":             bfs.solve,
    "dfs":             dfs.solve,
    "idfs":            idfs.solve,
    "astar_manhattan": lambda b: astar.solve(b, heuristic="manhattan"),
    "astar_euclidean": lambda b: astar.solve(b, heuristic="euclidean"),
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json()

    # basic input checks
    if not data or "initial_state" not in data or "algorithm" not in data:
        return jsonify({"success": False, "error": "missing initial_state or algorithm"}), 400

    initial_state = data["initial_state"]
    algorithm     = data["algorithm"]

    if sorted(initial_state) != list(range(9)):
        return jsonify({"success": False, "error": "board must contain digits 0-8 exactly once"}), 400

    if algorithm not in SOLVERS:
        return jsonify({"success": False, "error": f"unknown algorithm: {algorithm}"}), 400

    # no point running if it's already unsolvable
    if is_solvable(initial_state) is False:
        return jsonify({"success": False, "error": "this puzzle is unsolvable"}), 200

    result = SOLVERS[algorithm](initial_state)

    if result is None:
        return jsonify({"success": False, "error": "no solution found"}), 200

    return jsonify({"success": True, "algorithm": algorithm, **result})


if __name__ == "__main__":
    app.run(debug=True)
