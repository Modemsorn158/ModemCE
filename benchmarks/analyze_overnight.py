"""Summarize overnight batches and bootstrap by opening, not by game."""

import argparse
import json
import random
import re
from collections import defaultdict
from pathlib import Path

import chess.pgn


def analyze(folder, rng, replicates):
    match = re.fullmatch(r"(ModemCE\d+)-vs-(ModemCE\d+)", folder.name)
    if match is None:
        raise ValueError(f"Unexpected match folder: {folder}")
    newer, older = match.groups()
    clusters = defaultdict(list)
    wins = losses = draws = 0
    for pgn in sorted(folder.glob("batch-*.pgn")):
        with pgn.open(encoding="utf-8-sig") as source:
            while game := chess.pgn.read_game(source):
                if game.errors:
                    raise ValueError(f"Invalid game in {pgn}: {game.errors}")
                if {game.headers["White"], game.headers["Black"]} != {newer, older}:
                    raise ValueError(f"Unexpected players in {pgn}")
                result = game.headers["Result"]
                if result == "1/2-1/2":
                    score = 0.5
                    draws += 1
                elif result in ("1-0", "0-1"):
                    winner = game.headers["White" if result == "1-0" else "Black"]
                    score = float(winner == newer)
                    wins += int(score == 1)
                    losses += int(score == 0)
                else:
                    raise ValueError(f"Unfinished game in {pgn}")
                opening = tuple(m.uci() for m in list(game.mainline_moves())[:6])
                if len(opening) != 6:
                    raise ValueError(f"Opening missing in {pgn}")
                clusters[opening].append(score)
    total = wins + losses + draws
    if not total:
        return None
    groups = list(clusters.values())
    cluster_means = [sum(group) / len(group) for group in groups]
    interval = None
    # A percentile bootstrap cannot estimate uncertainty when every observed
    # opening has the same average; reporting e.g. [100%, 100%] is misleading.
    if len(groups) >= 5 and min(cluster_means) != max(cluster_means):
        estimates = []
        for _ in range(replicates):
            sample = [rng.choice(groups) for _ in groups]
            estimates.append(sum(map(sum, sample)) / sum(map(len, sample)))
        estimates.sort()
        interval = [round(100 * estimates[int(0.025 * (replicates - 1))], 2),
                    round(100 * estimates[int(0.975 * (replicates - 1))], 2)]
    return {
        "newer": newer, "older": older, "wins": wins, "losses": losses, "draws": draws,
        "games": total, "unique_openings": len(groups),
        "score_percent": round(100 * (wins + draws / 2) / total, 2),
        "opening_cluster_bootstrap_95_percent": interval,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--replicates", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261122)
    args = parser.parse_args()
    if args.replicates < 100:
        parser.error("use at least 100 bootstrap replicates")
    rng = random.Random(args.seed)
    results = [result for folder in sorted(args.directory.glob("ModemCE*-vs-ModemCE*"))
               if (result := analyze(folder, rng, args.replicates)) is not None]
    print(json.dumps({"seed": args.seed, "replicates": args.replicates, "matches": results}, indent=2))


if __name__ == "__main__":
    main()
