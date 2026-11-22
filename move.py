import json
from pathlib import Path
from random import choice

import chess
import chess.polyglot


BOOK_PATH = Path(__file__).resolve().parent / "data" / "opening_book.json"
with BOOK_PATH.open(encoding="utf-8") as book_file:
    OPENING_BOOK = json.load(book_file)


def get_move(board: chess.Board):
    moves = list(board.legal_moves)
    if not moves:
        return "0000"

    book_moves = OPENING_BOOK.get(f"{chess.polyglot.zobrist_hash(board):016x}", [])
    legal_book_moves = [chess.Move.from_uci(move) for move in book_moves
                        if chess.Move.from_uci(move) in moves]
    return choice(legal_book_moves or moves)
