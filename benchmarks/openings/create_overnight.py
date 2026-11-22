"""Create the fixed six-ply openings used by the overnight tournament."""

from pathlib import Path

import chess.pgn

LINES = [
    "e4 e5 Nf3 Nc6 Bb5 a6",
    "e4 e5 Nf3 Nc6 Bc4 Bc5",
    "e4 e5 Nf3 Nc6 Bc4 Nf6",
    "e4 e5 Nf3 Nf6 Nxe5 d6",
    "e4 c5 Nf3 d6 d4 cxd4",
    "e4 c5 Nf3 Nc6 d4 cxd4",
    "e4 c5 Nf3 e6 d4 cxd4",
    "e4 e6 d4 d5 Nc3 Nf6",
    "e4 e6 d4 d5 Nd2 Nf6",
    "e4 c6 d4 d5 Nc3 dxe4",
    "e4 c6 d4 d5 exd5 cxd5",
    "e4 d6 d4 Nf6 Nc3 g6",
    "e4 g6 d4 Bg7 Nc3 d6",
    "e4 d5 exd5 Qxd5 Nc3 Qa5",
    "e4 Nf6 e5 Nd5 d4 d6",
    "d4 d5 c4 e6 Nc3 Nf6",
    "d4 d5 c4 c6 Nf3 Nf6",
    "d4 d5 c4 dxc4 Nf3 Nf6",
    "d4 Nf6 c4 g6 Nc3 Bg7",
    "d4 Nf6 c4 e6 Nc3 Bb4",
    "d4 Nf6 c4 e6 Nf3 b6",
    "d4 Nf6 c4 e6 Nf3 d5",
    "d4 f5 c4 Nf6 g3 g6",
    "c4 e5 Nc3 Nf6 g3 d5",
    "Nf3 d5 g3 Nf6 Bg2 e6",
]


def main():
    output = Path(__file__).with_name("overnight.pgn")
    positions = set()
    with output.open("w", encoding="utf-8", newline="\n") as target:
        for number, line in enumerate(LINES, 1):
            game = chess.pgn.Game()
            game.headers["Event"] = f"Overnight opening {number}"
            board = game.board()
            node = game
            for san in line.split():
                move = board.parse_san(san)
                board.push(move)
                node = node.add_variation(move)
            if board.fen() in positions:
                raise ValueError(f"Duplicate opening: {line}")
            positions.add(board.fen())
            print(game, file=target, end="\n\n")
    print(f"Wrote {len(positions)} distinct openings to {output}")


if __name__ == "__main__":
    main()
