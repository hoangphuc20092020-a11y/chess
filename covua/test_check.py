from game.board import Board, WHITE, BLACK, PIECE_UNICODE
from game.moves import MoveGenerator
from game.rules import RuleChecker

board = Board()
# xóa bàn cờ 
board.grid = [[None for _ in range(8) ] for _ in range (8)]
# đặt vua trắng ở e1
board.grid[6][4] = 'wK'
#đặt vua đen ở a8 
board.grid[0][0] = 'bK'
# đặt xe đen ở a2
board.grid[6][0] = 'bR'
# đặt hậu đen ở vị trí a1
board.grid[7][0] = 'bQ'

mg = MoveGenerator()
rc = RuleChecker()
result = mg.attack_square(board, 6,3,BLACK)
result1 = rc.is_checkmate(board,mg,WHITE)

print("kết quả: ", result1)

# piece = board.get(7,2)
# symbol = PIECE_UNICODE.get(piece, piece)

# position = board.to_algebraic(7,2)

# # danh sách nước cac nước đi thô của tượng c1
# moves = mg.raw_moves(board, 7, 2)
# print(f"danh sách các nước đi của {symbol} ở {position}")
# for move in moves:
#     print(move)
    