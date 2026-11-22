from sys import stdin

while True:
    received = stdin.readline()
    if received == "":
        break
    received = received.strip()
    
    match received:
        case "uci":
            print("id name ModemCE1", flush = True)
            print("id author modem158", flush = True)
            print("uciok", flush = True)
        case "isready":
            print("readyok", flush = True)
        case "quit":
            break