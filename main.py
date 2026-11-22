from sys import stdin
import chess

board = chess.Board()
while True:
    received = stdin.readline()
    if received == "":
        break
    arguments = received.strip().split()
    
    if not arguments == []:
        match arguments[0]:
            case "uci":
                print("id name ModemCE1", flush = True)
                print("id author modem158", flush = True)
                print("uciok", flush = True)
            case "isready":
                print("readyok", flush = True)
            case "position":
                length = len(arguments)
                if length >= 2:
                    match arguments[1]:
                        case "startpos":
                            board.reset()
                            if length >= 3:
                                if arguments[2] == "moves":
                                    for move in arguments[3:]:
                                        board.push_uci(move)
                        case "fen":
                            board.set_fen(" ".join(arguments[2:8]))
                            length = len(arguments)
                            if length >= 9:
                                if arguments[8] == "moves":
                                    for move in arguments[9:]:
                                        board.push_uci(move)
            case "quit":
                break 