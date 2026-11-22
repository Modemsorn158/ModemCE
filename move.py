import json
from pathlib import Path
from random import choice
from threading import Event
from time import monotonic

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


class SearchStopped(Exception):
    pass


def search(board: chess.Board, depth: int, alpha=-float("inf"),
           beta=float("inf"), deadline=None, stop=None, ply=0):
    """Alpha-beta minimax, with depth measured in individual moves (plies)."""
    if (stop is not None and stop.is_set()) or (deadline is not None and monotonic() >= deadline):
        raise SearchStopped
    if depth == 0 or board.is_game_over():
        score = evaluate(board)
        # Prefer a quicker win or a slower loss over the same eventual mate.
        if score == MATE_SCORE:
            return score - ply
        if score == -MATE_SCORE:
            return score + ply
        return score

    maximizing = board.turn == chess.WHITE
    best = -float("inf") if maximizing else float("inf")
    for candidate in sorted(board.legal_moves, key=board.is_capture, reverse=True):
        board.push(candidate)
        try:
            score = search(board, depth - 1, alpha, beta, deadline, stop, ply + 1)
        finally:
            board.pop()
        if maximizing:
            best = max(best, score)
            alpha = max(alpha, best)
        else:
            best = min(best, score)
            beta = min(beta, best)
        if alpha >= beta:
            break
    return best


def time_budget(board: chess.Board, limits: dict):
    """Return seconds to search, or None for an explicitly unbounded search."""
    if "movetime" in limits:
        milliseconds = max(0, limits["movetime"])
        return max(0, milliseconds - min(50, milliseconds * 0.05)) / 1000
    remaining = limits.get("wtime" if board.turn == chess.WHITE else "btime")
    if remaining is not None:
        remaining = max(0, remaining)
        increment = max(0, limits.get("winc" if board.turn == chess.WHITE else "binc", 0))
        moves_left = max(1, limits.get("movestogo", 30))
        reserve = min(1000, remaining * 0.05)
        allocation = min(remaining / moves_left + increment * 0.75,
                         remaining * 0.10, remaining - reserve)
        return max(0, allocation) / 1000
    if "infinite" in limits or "depth" in limits:
        return None
    return 0.5


def get_move(board: chess.Board, limits=None, stop=None, on_depth=None):
    limits = limits or {}
    stop = stop or Event()
    moves = list(board.legal_moves)
    if not moves:
        return "0000"

    book_moves = OPENING_BOOK.get(f"{chess.polyglot.zobrist_hash(board):016x}", [])
    legal_book_moves = [chess.Move.from_uci(move) for move in book_moves
                        if chess.Move.from_uci(move) in moves]
    if legal_book_moves:
        if "infinite" in limits:
            stop.wait()
        return choice(legal_book_moves)

    budget = time_budget(board, limits)
    deadline = None if budget is None else monotonic() + budget
    best_move = choice(moves)  # Legal fallback if even depth one cannot finish.
    max_depth = max(1, limits.get("depth", 64))
    for depth in range(1, max_depth + 1):
        scores = []
        try:
            ordered = [best_move] + [candidate for candidate in moves if candidate != best_move]
            for candidate in ordered:
                board.push(candidate)
                try:
                    scores.append(search(board, depth - 1, deadline=deadline, stop=stop, ply=1))
                finally:
                    board.pop()
        except SearchStopped:
            break
        best_score = max(scores) if board.turn == chess.WHITE else min(scores)
        best_move = choice([candidate for candidate, score in zip(ordered, scores)
                            if score == best_score])
        if on_depth:
            on_depth(depth, best_score)
        if abs(best_score) >= MATE_SCORE - depth:
            break
    if "infinite" in limits and not stop.is_set():
        stop.wait()
    return best_move
