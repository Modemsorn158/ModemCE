import chess
from random import choice

def get_move(board: chess.Board):
    moves = list(board.legal_moves)
    
    if not moves:
        return("0000")
    
    return choice(moves)