from game.board import Board, WHITE, BLACK
from game.moves import MoveGenerator

class RuleChecker:
    #####
    # KIỂM TRA CHIẾU 
    def is_in_check(self, board: Board, gen: MoveGenerator, color: str) -> bool:
        """ check if the king is in check(kiểm tra vua có bị chiếu không)"""
        king_pos = board.find_king(color)
        if not king_pos:
            return True # vua không tìm thấy nghĩa vua đang bị chiếu
        
        king_r, king_c = king_pos
        opponent = BLACK if color == WHITE else WHITE
        for r in range(8):
            for c in range(8):
                if board.color_at(r,c) == opponent:
                    for move in gen.raw_moves(board ,r,c):
                        if move["to_row"] == king_r and move["to_col"] == king_c:
                            return True
        
        return False 
    
    # CHIẾU HẾT
    def is_checkmate(self ,board: Board, gen: MoveGenerator, color: str) -> bool:
        if not self.is_in_check(board,gen,color):
            return False
        return len(gen.legal_moves(board, color) ) == 0