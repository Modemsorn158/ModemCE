"""Build a position-indexed opening book from the bundled Lichess TSV files."""

import csv
import io
import json
from collections import defaultdict
from pathlib import Path

import chess.pgn
import chess.polyglot


ROOT = Path(__file__).resolve().parent
positions = defaultdict(set)
for path in sorted((ROOT / "data" / "openings").glob("*.tsv")):
    with path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            game = chess.pgn.read_game(io.StringIO(row["pgn"]))
            if game is None or game.errors:
                raise ValueError(f"Invalid opening in {path}: {row['pgn']}")
            board = game.board()
            for move in game.mainline_moves():
                positions[f"{chess.polyglot.zobrist_hash(board):016x}"].add(move.uci())
                board.push(move)

book = {key: sorted(moves) for key, moves in sorted(positions.items())}
(ROOT / "data" / "opening_book.json").write_text(
    json.dumps(book, separators=(",", ":")) + "\n", encoding="utf-8"
)
print(f"Built opening book with {len(book)} positions")
