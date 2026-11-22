import unittest
from unittest.mock import patch
import random
from threading import Event

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

    def test_positional_evaluation_is_symmetric_and_rewards_development(self):
        self.assertEqual(move.evaluate(chess.Board()), 0)
        edge = chess.Board("4k3/8/8/8/8/8/8/N3K3 w - - 0 1")
        center = chess.Board("4k3/8/8/8/3N4/8/8/4K3 w - - 0 1")
        # Include an opposing pawn so these are not automatic draws.
        edge.set_piece_at(chess.A7, chess.Piece(chess.PAWN, chess.BLACK))
        center.set_piece_at(chess.A7, chess.Piece(chess.PAWN, chess.BLACK))
        self.assertGreater(move.evaluate(center), move.evaluate(edge))
        self.assertEqual(move.evaluate(center), -move.evaluate(center.mirror()))

    def test_king_centralization_is_rewarded_in_the_endgame(self):
        edge = chess.Board("4k3/p7/8/8/8/8/8/K7 w - - 0 1")
        center = chess.Board("4k3/p7/8/8/3K4/8/8/8 w - - 0 1")
        self.assertGreater(move.evaluate(center), move.evaluate(edge))
        self.assertEqual(move.evaluate(center), -move.evaluate(center.mirror()))

    def test_precomputed_evaluation_matches_original_formula(self):
        def original(board):
            if board.is_game_over():
                return move.position_score(board, 0)
            material = sum(value * (len(board.pieces(piece, chess.WHITE)) -
                                    len(board.pieces(piece, chess.BLACK)))
                           for piece, value in move.PIECE_VALUES.items())
            nonpawns = sum(move.PIECE_VALUES[piece] *
                           (len(board.pieces(piece, chess.WHITE)) + len(board.pieces(piece, chess.BLACK)))
                           for piece in (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN))
            positional = 0
            for square, piece in board.piece_map().items():
                file, rank = chess.square_file(square), chess.square_rank(square)
                advance = rank if piece.color else 7 - rank
                centrality = 6 - abs(2 * file - 7) - abs(2 * rank - 7)
                if piece.piece_type == chess.PAWN:
                    bonus = 5 * advance + 2 * (3 - abs(2 * file - 7))
                elif piece.piece_type == chess.KNIGHT:
                    bonus = 5 * centrality
                elif piece.piece_type == chess.BISHOP:
                    bonus = 3 * centrality
                elif piece.piece_type == chess.QUEEN:
                    bonus = centrality
                elif piece.piece_type == chess.KING:
                    bonus = 5 * centrality if nonpawns <= 2600 else -8 * advance
                else:
                    bonus = 0
                positional += bonus if piece.color else -bonus
            def pair_for(color):
                return len({(chess.square_file(s) + chess.square_rank(s)) % 2
                            for s in board.pieces(chess.BISHOP, color)}) == 2
            pair = move.BISHOP_PAIR_BONUS * (int(pair_for(chess.WHITE)) - int(pair_for(chess.BLACK)))
            return material + positional + pair

        rng = random.Random(10)
        board = chess.Board()
        for _ in range(150):
            self.assertEqual(move.evaluate(board), original(board), board.fen())
            if board.is_game_over():
                board.reset()
            board.push(rng.choice(list(board.legal_moves)))

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
                if position.is_game_over():
                    return move.position_score(position, ply)
                return move.quiescence(position, -float("inf"), float("inf"), ply=ply)
            scores = []
            for candidate in position.legal_moves:
                position.push(candidate)
                scores.append(minimax(position, depth - 1, ply + 1))
                position.pop()
            return max(scores) if position.turn == chess.WHITE else min(scores)

        self.assertEqual(move.search(board, 3), minimax(board, 3))

    def test_quiescence_sees_recapture_at_horizon(self):
        board = chess.Board("3rk3/3p4/8/8/8/8/8/3QK3 w - - 0 1")
        board.push_uci("d1d7")
        self.assertGreater(move.evaluate(board), 0)
        self.assertLess(move.search(board, 0), 0)

    def test_quiescence_handles_check_and_preserves_board(self):
        board = chess.Board("4k3/8/8/8/8/8/4R3/4K3 b - - 0 1")
        before = board.fen()
        self.assertTrue(board.is_check())
        score = move.quiescence(board, -float("inf"), float("inf"))
        self.assertIsInstance(score, (float, int))
        self.assertEqual(board.fen(), before)

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
            return calls

        with patch.dict(move.OPENING_BOOK, {}, clear=True), \
             patch.object(move, "search", side_effect=interrupt_during_second_depth):
            chosen = move.get_move(board, {"depth": 4}, on_depth=lambda d, s: completed.append(d))
        self.assertEqual(completed, [1])
        self.assertIn(chosen, board.legal_moves)
        self.assertEqual(board.fen(), original)

    def test_root_researches_tied_bounds_before_choosing(self):
        board = chess.Board("4k3/8/8/8/8/8/4P3/4K3 w - - 0 1")
        candidates = list(board.legal_moves)
        calls = []

        def fake_search(position, depth, alpha=-float("inf"), beta=float("inf"),
                        deadline=None, stop=None, ply=0):
            candidate = position.peek()
            calls.append((candidate, alpha, beta))
            # All later moves appear tied under the bound but are actually worse.
            if alpha != -float("inf"):
                return alpha
            return 100 if candidate == candidates[0] else 0

        with patch.dict(move.OPENING_BOOK, {}, clear=True), \
             patch.object(move, "choice", side_effect=lambda items: items[0]), \
             patch.object(move, "fallback_move", return_value=candidates[0]), \
             patch.object(move, "search", side_effect=fake_search):
            chosen = move.get_move(board, {"depth": 1})
        self.assertEqual(chosen, candidates[0])
        self.assertGreater(len(calls), len(candidates))

    def test_root_pruning_matches_full_window_for_both_colors(self):
        position = chess.Board("3rk3/3p4/8/8/8/8/8/3QK3 w - - 0 1")
        for board in (position, position.mirror()):
            original = board.fen()
            scores = {}
            for candidate in board.legal_moves:
                board.push(candidate)
                scores[candidate] = move.search(board, 1, ply=1)
                board.pop()
            target = max(scores.values()) if board.turn == chess.WHITE else min(scores.values())
            with patch.dict(move.OPENING_BOOK, {}, clear=True):
                chosen = move.get_move(board, {"depth": 2})
            self.assertEqual(scores[chosen], target)
            self.assertEqual(board.fen(), original)

    def test_fallback_chooses_static_capture_and_respects_stop(self):
        board = chess.Board("4k3/3q4/8/8/8/8/8/3QK3 w - - 0 1")
        original = board.fen()
        moves = list(board.legal_moves)
        chosen = move.fallback_move(board, moves, None, Event())
        self.assertEqual(chosen.uci(), "d1d7")
        self.assertEqual(board.fen(), original)
        stopped = Event()
        stopped.set()
        self.assertIn(move.fallback_move(board, moves, None, stopped), board.legal_moves)
        self.assertEqual(board.fen(), original)

    def test_bishop_pair_bonus_applies_to_the_correct_color(self):
        board = chess.Board("4k3/p7/8/8/8/8/8/2BBK3 w - - 0 1")
        with patch.object(move, "BISHOP_PAIR_BONUS", 0):
            baseline = move.evaluate(board)
        self.assertEqual(move.evaluate(board) - baseline, move.BISHOP_PAIR_BONUS)
        self.assertEqual(move.evaluate(board), -move.evaluate(board.mirror()))
        same_color = chess.Board("4k3/p7/8/8/8/4B3/8/2B1K3 w - - 0 1")
        with patch.object(move, "BISHOP_PAIR_BONUS", 0):
            same_color_baseline = move.evaluate(same_color)
        self.assertEqual(move.evaluate(same_color), same_color_baseline)


if __name__ == "__main__":
    unittest.main()
