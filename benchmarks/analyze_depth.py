"""Count out-of-book moves with and without Cute Chess depth annotations."""

import argparse
import collections
import json
import re
from pathlib import Path

import chess.pgn
import chess.polyglot

ROOT = Path(__file__).resolve().parent.parent
BOOK = json.loads((ROOT / "data/opening_book.json").read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pgn", type=Path)
    args = parser.parse_args()
    counts = collections.defaultdict(lambda: {"out_of_book": 0, "without_depth": 0})
    with args.pgn.open(encoding="utf-8-sig") as source:
        while game := chess.pgn.read_game(source):
            if game.errors:
                raise ValueError(game.errors)
            board = game.board()
            for node in game.mainline():
                name = game.headers["White" if board.turn else "Black"]
                key = f"{chess.polyglot.zobrist_hash(board):016x}"
                book_moves = BOOK.get(key, [])
                in_book = any(chess.Move.from_uci(uci) in board.legal_moves for uci in book_moves)
                if not in_book:
                    counts[name]["out_of_book"] += 1
                    if not re.search(r"/\d+\s", node.comment):
                        counts[name]["without_depth"] += 1
                board.push(node.move)
    print(json.dumps(dict(counts), indent=2))


if __name__ == "__main__":
    main()
