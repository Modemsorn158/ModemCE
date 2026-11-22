import unittest
from unittest.mock import patch

import chess
import chess.polyglot

import move


class SearchTests(unittest.TestCase):
    def test_finds_mate_for_either_side(self):
        for fen in ("7k/8/5KQ1/8/8/8/8/8 w - - 0 1",
                    "8/8/8/8/8/5kq1/8/7K b - - 0 1"):
            board = chess.Board(fen)
            original = board.fen()
            with patch.dict(move.OPENING_BOOK, {}, clear=True):
                chosen = move.get_move(board, {"depth": 2})
            self.assertEqual(board.fen(), original)
            board.push(chosen)
            self.assertTrue(board.is_checkmate(), chosen)

    def test_search_accounts_for_opponents_recapture(self):
        board = chess.Board("3rk3/3p4/8/8/8/8/8/3QK3 w - - 0 1")
        board.push_uci("d1d7")
        self.assertLess(move.search(board, 1), 0)
        board.pop()
        with patch.dict(move.OPENING_BOOK, {}, clear=True):
            self.assertNotEqual(move.get_move(board, {"depth": 2}).uci(), "d1d7")

    def test_terminal_positions(self):
        mate = chess.Board("7k/6Q1/6K1/8/8/8/8/8 b - - 0 1")
        stalemate = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
        self.assertEqual(move.evaluate(mate), move.MATE_SCORE)
        self.assertEqual(move.evaluate(stalemate), 0)
        self.assertEqual(move.get_move(mate), "0000")

    def test_book_takes_precedence(self):
        board = chess.Board()
        key = f"{chess.polyglot.zobrist_hash(board):016x}"
        with patch.dict(move.OPENING_BOOK, {key: ["e2e4"]}, clear=True):
            self.assertEqual(move.get_move(board).uci(), "e2e4")

    def test_time_budget_uses_side_to_move_and_leaves_reserve(self):
        board = chess.Board()
        limits = {"wtime": 30000, "btime": 6000, "winc": 1000, "movestogo": 10}
        self.assertAlmostEqual(move.time_budget(board, limits), 3.0)
        board.push_uci("e2e4")
        self.assertAlmostEqual(move.time_budget(board, limits), 0.6)
        self.assertLess(move.time_budget(board, {"movetime": 1000}), 1.0)
        self.assertIsNone(move.time_budget(board, {"depth": 3}))

    def test_move_ordering_prefers_valuable_captures_and_promotions(self):
        board = chess.Board("4k3/8/8/3q1p2/4P3/8/8/4K3 w - - 0 1")
        self.assertGreater(move.move_order_score(board, chess.Move.from_uci("e4d5")),
                           move.move_order_score(board, chess.Move.from_uci("e4f5")))
        promotion = chess.Board("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
        self.assertGreater(move.move_order_score(promotion, chess.Move.from_uci("a7a8q")),
                           move.move_order_score(promotion, chess.Move.from_uci("a7a8n")))

    def test_ordered_alpha_beta_matches_exhaustive_minimax(self):
        board = chess.Board("3rk3/3p4/8/8/8/8/8/3QK3 w - - 0 1")

        def minimax(position, depth, ply=0):
            if depth == 0 or position.is_game_over():
                score = move.evaluate(position)
                if score == move.MATE_SCORE:
                    return score - ply
                if score == -move.MATE_SCORE:
                    return score + ply
                return score
            scores = []
            for candidate in position.legal_moves:
                position.push(candidate)
                scores.append(minimax(position, depth - 1, ply + 1))
                position.pop()
            return max(scores) if position.turn == chess.WHITE else min(scores)

        self.assertEqual(move.search(board, 3), minimax(board, 3))

    def test_interrupted_iteration_keeps_last_completed_move(self):
        board = chess.Board("3rk3/3p4/8/8/8/8/8/3QK3 w - - 0 1")
        original = board.fen()
        completed = []
        calls = 0
        first_depth_count = board.legal_moves.count()

        def interrupt_during_second_depth(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls > first_depth_count:
                raise move.SearchStopped
            return 0

        with patch.dict(move.OPENING_BOOK, {}, clear=True), \
             patch.object(move, "search", side_effect=interrupt_during_second_depth):
            chosen = move.get_move(board, {"depth": 4}, on_depth=lambda d, s: completed.append(d))
        self.assertEqual(completed, [1])
        self.assertIn(chosen, board.legal_moves)
        self.assertEqual(board.fen(), original)


if __name__ == "__main__":
    unittest.main()
