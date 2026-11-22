"""Compare leaf evaluations of CE4 and the current search at a fixed depth."""

import json
import subprocess
import sys
import types
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import chess

def load_version(version, commit):
    module = types.ModuleType(f"modemce{version}_move")
    module.__file__ = str(ROOT / "move.py")
    source = subprocess.check_output(["git", "show", f"{commit}:move.py"], cwd=ROOT, text=True)
    exec(compile(source, f"ModemCE{version}/move.py", "exec"), module.__dict__)
    return module


old = load_version(4, "14f08fb")
new = load_version(5, "07bb2e1")
positions = [
    "3rk3/3p4/8/8/8/8/8/3QK3 w - - 0 1",
    "r3k2r/ppp2ppp/2n1bn2/3qp3/3P4/2N1PN2/PPP2PPP/R2QKB1R w KQkq - 0 1",
    "4k3/1p3pp1/p1p2n1p/3p4/3P4/2P1BN2/PP3PPP/4K3 w - - 0 1",
]
results = []
for fen in positions:
    row = {"fen": fen, "depth_plies": 3}
    for label, module in (("ModemCE4", old), ("ModemCE5", new)):
        original = module.evaluate
        count = [0]

        def counted(board):
            count[0] += 1
            return original(board)

        module.evaluate = counted
        start = perf_counter()
        try:
            score = module.search(chess.Board(fen), 3)
            elapsed = perf_counter() - start
        finally:
            module.evaluate = original
        row[label] = {"score_white_cp": score, "leaf_evaluations": count[0],
                      "seconds": round(elapsed, 6)}
    results.append(row)
print(json.dumps(results, indent=2))
