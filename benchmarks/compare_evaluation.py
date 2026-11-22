"""Compare evaluation speed on fixed positions across saved source versions."""

import json
import subprocess
import types
from pathlib import Path
from time import perf_counter

import chess

ROOT = Path(__file__).resolve().parent.parent
POSITIONS = [
    chess.STARTING_FEN,
    "r3k2r/ppp2ppp/2n1bn2/3qp3/3P4/2N1PN2/PPP2PPP/R2QKB1R w KQkq - 0 1",
    "4k3/1p3pp1/p1p2n1p/3p4/3P4/2P1BN2/PP3PPP/4K3 w - - 0 1",
]
VERSIONS = {"CE5": "07bb2e1", "CE6": "acaf856", "CE9": "0bf5fd3", "CE10": "1ad05d5"}
boards = [chess.Board(fen) for fen in POSITIONS]
results = {"positions": POSITIONS, "repetitions_per_position": 3000, "versions": {}}
for name, commit in VERSIONS.items():
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / "move.py")
    source = subprocess.check_output(["git", "show", f"{commit}:move.py"], cwd=ROOT, text=True)
    exec(compile(source, f"{name}/move.py", "exec"), module.__dict__)
    scores = [module.evaluate(board) for board in boards]
    start = perf_counter()
    for _ in range(results["repetitions_per_position"]):
        for board in boards:
            module.evaluate(board)
    results["versions"][name] = {"commit": commit, "scores": scores,
                                 "seconds": round(perf_counter() - start, 6)}
print(json.dumps(results, indent=2))
