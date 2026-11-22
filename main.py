from sys import stdin
from threading import Event, Thread

import chess

from move import MATE_SCORE, get_move


def parse_limits(arguments):
    limits = {}
    numeric = {"wtime", "btime", "winc", "binc", "movestogo", "movetime", "depth"}
    i = 0
    while i < len(arguments):
        key = arguments[i]
        if key in numeric and i + 1 < len(arguments):
            try:
                limits[key] = int(arguments[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            if key == "infinite":
                limits[key] = True
            i += 1
    return limits


def run():
    board = chess.Board()
    worker = None
    stop = None

    def stop_search():
        if worker is not None and worker.is_alive():
            stop.set()
            worker.join()

    for received in stdin:
        arguments = received.strip().split()
        if not arguments:
            continue
        command = arguments[0]
        if command == "uci":
            print("id name ModemCE9", flush=True)
            print("id author modem158", flush=True)
            print("uciok", flush=True)
        elif command == "isready":
            print("readyok", flush=True)
        elif command == "ucinewgame":
            stop_search()
            board.reset()
        elif command == "position":
            stop_search()
            if len(arguments) >= 2 and arguments[1] == "startpos":
                board.reset()
                moves = arguments[3:] if len(arguments) > 2 and arguments[2] == "moves" else []
            elif len(arguments) >= 8 and arguments[1] == "fen":
                board.set_fen(" ".join(arguments[2:8]))
                moves = arguments[9:] if len(arguments) > 8 and arguments[8] == "moves" else []
            else:
                continue
            for candidate in moves:
                board.push_uci(candidate)
        elif command == "go":
            stop_search()
            stop = Event()
            position = board.copy()
            limits = parse_limits(arguments[1:])

            def think(position=position, limits=limits, stop=stop):
                def report(depth, score):
                    # UCI scores are relative to the side to move.
                    relative = score if position.turn == chess.WHITE else -score
                    if abs(score) >= MATE_SCORE - depth:
                        moves_to_mate = (MATE_SCORE - abs(score) + 1) // 2
                        signed_mate = moves_to_mate if relative > 0 else -moves_to_mate
                        print(f"info depth {depth} score mate {signed_mate}", flush=True)
                    else:
                        print(f"info depth {depth} score cp {relative}", flush=True)
                print(f"bestmove {get_move(position, limits, stop, report)}", flush=True)

            worker = Thread(target=think)
            worker.start()
        elif command == "stop":
            stop_search()
        elif command == "quit":
            stop_search()
            break
    stop_search()


if __name__ == "__main__":
    run()
