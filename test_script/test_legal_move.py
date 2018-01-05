from src.chess_zero.agent import chinese_chess

board = chinese_chess.Board()

for mov in board.generate_legal_moves():
    print(mov)