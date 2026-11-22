"""Summarize completed Cute Chess PGNs from the newer engine's perspective."""

import argparse
import re
from pathlib import Path

import chess.pgn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print("| Match | Wins–losses–draws | Score | Games |")
    print("| --- | ---: | ---: | ---: |")
    for path in sorted(args.directory.glob("ModemCE*-vs-ModemCE*.pgn"),
                       key=lambda p: int(re.search(r"ModemCE(\d+)", p.name).group(1))):
        match = re.fullmatch(r"ModemCE(\d+)-vs-ModemCE(\d+)\.pgn", path.name)
        newer, older = map(int, match.groups())
        wins = losses = draws = 0
        with path.open(encoding="utf-8-sig") as source:
            while game := chess.pgn.read_game(source):
                if game.errors:
                    raise ValueError(f"Invalid game in {path}: {game.errors}")
                result = game.headers.get("Result")
                if result == "1/2-1/2":
                    draws += 1
                elif result in ("1-0", "0-1"):
                    winner = game.headers["White" if result == "1-0" else "Black"]
                    if winner == f"ModemCE{newer}":
                        wins += 1
                    elif winner == f"ModemCE{older}":
                        losses += 1
                    else:
                        raise ValueError(f"Unexpected winner in {path}: {winner}")
                else:
                    raise ValueError(f"Unfinished game in {path}")
        games = wins + losses + draws
        if games:
            score = 100 * (wins + draws / 2) / games
            print(f"| CE{newer} vs CE{older} | {wins}–{losses}–{draws} | {score:.2f}% | {games} |")


if __name__ == "__main__":
    main()
