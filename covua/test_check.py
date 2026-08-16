from game.board import Board, WHITE, BLACK, PIECE_UNICODE
from game.moves import MoveGenerator

board = Board()
# xóa bàn cờ 
board.grid = [[None for _ in range(8) ] for _ in range (8)]
# đặt vua trắng ở e1
board.grid[7][4] = 'wK'
#đặt vua đen ở a8 
board.grid[0][0] = 'bK'
# đặt xe đen ở e8
board.grid[0][4] = 'bR'
# đặt tượng ở vị trí c1
board.grid[7][2] = 'bB'

mg = MoveGenerator()

result = mg.attack_square(board, 6,3,BLACK)

print("kết quả: ", result)

piece = board.get(7,2)
symbol = PIECE_UNICODE.get(piece, piece)

position = board.to_algebraic(7,2)

# danh sách nước cac nước đi thô của tượng c1
moves = mg.raw_moves(board, 7, 2)
print(f"danh sách các nước đi của {symbol} ở {position}")
for move in moves:
    print(move)
    