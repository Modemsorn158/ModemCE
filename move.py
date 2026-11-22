import json
from pathlib import Path
from random import choice

import chess
import chess.polyglot


BOOK_PATH = Path(__file__).resolve().parent / "data" / "opening_book.json"
with BOOK_PATH.open(encoding="utf-8") as book_file:
    OPENING_BOOK = json.load(book_file)

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
}
MATE_SCORE = 100_000


def evaluate(board: chess.Board):
    """Score a position in centipawns from White's perspective."""
    outcome = board.outcome()
    if outcome is not None:
        if outcome.winner is None:
            return 0
        return MATE_SCORE if outcome.winner == chess.WHITE else -MATE_SCORE

    return sum(
        value * (len(board.pieces(piece, chess.WHITE)) -
                 len(board.pieces(piece, chess.BLACK)))
        for piece, value in PIECE_VALUES.items()
    )


def search(board: chess.Board, depth: int):
    """Minimax with depth measured in individual moves (plies)."""
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    scores = []
    for move in board.legal_moves:
        board.push(move)
        try:
            scores.append(search(board, depth - 1))
        finally:
            board.pop()
    return max(scores) if board.turn == chess.WHITE else min(scores)


def get_move(board: chess.Board):
    moves = list(board.legal_moves)
    if not moves:
        return "0000"

    book_moves = OPENING_BOOK.get(f"{chess.polyglot.zobrist_hash(board):016x}", [])
    legal_book_moves = [chess.Move.from_uci(move) for move in book_moves
                        if chess.Move.from_uci(move) in moves]
    if legal_book_moves:
        return choice(legal_book_moves)

    scores = []
    for move in moves:
        board.push(move)
        try:
            scores.append(search(board, 1))
        finally:
            board.pop()
    best_score = max(scores) if board.turn == chess.WHITE else min(scores)
    return choice([move for move, score in zip(moves, scores) if score == best_score])
