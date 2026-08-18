# MỖI DÒNG CODE LÀ  NGHỆ THUẬT
# KHÔNG HIỂU CODE ĐÓ LÀM GÌ,THÌ ĐỪNG VIẾT VÀO 
"""
game/moves.py
-------------
Sinh tất cả nước đi hợp lệ cho từng loại quân.
 
Phân biệt 2 loại:
  - Raw moves  : nước đi thô, chưa kiểm tra có để vua bị chiếu không
  - Legal moves: nước đi hợp lệ thực sự (đã lọc qua rules.py)
 
Cách dùng:
    from game.moves import MoveGenerator
    gen = MoveGenerator()
    moves = gen.legal_moves(board, 'w')
"""
from game.board import Board, WHITE, BLACK, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING

#------------------------------------------------------------------#
# CẤU TRÚC MỘT NƯỚC ĐI
#------------------------------------------------------------------#
#* rất quan trọng cho được quân từ đâu đi đến đâu
def make_move(fr: int, fc: int, tr: int, tc: int, promo= None) -> dict: # promo là viết tắt của promotion = phong tốt
    """
    Tạo dict biểu diễn một nước đi.
    fr/fc = from_row/from_col
    tr/tc = to_row/to_col
    promo = 'Q'|'R'|'B'|'N' khi tốt phong cấp, None nếu không
    """
    return {
        'from_row': fr,
        'from_col': fc,
        'to_row': tr,
        'to_col': tc,
        'promo': promo,
    }

#--------------------------------------------------------------#
#  CLASS MomveGenerator
#--------------------------------------------------------------#

class MoveGenerator:
    """
    Sinh nước đi cho tất cả loại quân.
 
    Luồng hoạt động:
      raw_moves(board, r, c)
          ↓ (chưa lọc chiếu)
      legal_moves(board, color)
          ↓ (đã lọc — chỉ những nước không để vua bị chiếu)
          → dùng trong game.py và mcts.py
    """
    # HÀM PUBLIC CHÍNH
    def legal_moves(self, board: Board, color: str) -> list: # list chứa được dict
        """* Trả danh sách các nước đi HỢP LỆ của màu color.
        đây là hàm mà game.py và AI gọi vào nhiều nhất.
        """
        moves= [] 
        for r in range(8):
            for c in range(8):
                if board.color_at(r,c) == color:
                    moves.extend( # extend là lấy từng phần tử cho ds mới thêm vào ds cũ
                        self.legal_moves_for(board, r, c) 
                        )
        return moves # danh sách của nưowc đi của quân màu đó
    
    
    def legal_moves_for(self, board: Board, row: int , col: int) -> list:
        """ trả danh sách nước đi hợp lệ cho quân tại (r,c)
        lọc ra những nước để vua bị chiếu """
        piece = board.get(row,col)
        if not piece:
            return[]
        color = board.color_of(piece)
        raw = self.raw_moves(board, row, col)
        
        #lọc: chỉ giữ nước đi không để vua bị chiếu
        legal = []
        for move in raw:
            new_board = board.apply_move(move)#***
            if not self._is_in_check(new_board, color):
                legal.append(move)
        return legal
    
    
    def raw_moves(self, board: Board, row: int, col: int) -> list:
        """ sinh nước đi thô cho quân tại (row, col).
        chưa lọc chiều - dùng nội bộ và trong rulles.py """
        piece = board.get(row, col)
        if not piece:
            return []
        
        piece_type = board.type_of(piece)
        color = board.color_of(piece)
        
        dispatch = {
            PAWN: self._pawn_moves,
            KNIGHT: self._knight_moves,
            BISHOP: self._bishop_moves,
            ROOK: self._rook_moves,
            QUEEN: self._queen_moves,
            KING: self._king_moves,
        }
        
        fn = dispatch.get(piece_type)
        return fn(board, row, col, color) if fn else []
    
    # NƯỚC ĐI CỦA TỪNG LOẠI QUÂN
    def _pawn_moves(self, board: Board , r: int, c: int, color: str) -> list:
        """
        tốt (pawn):
        - đi thẳng 1 (không ăn)
        - có thể đi 2 ô từ hàng xuất phát (không ăn)
        - ăn chéo 1 ô ( chỉ khi nào có quân địch)
        - phong cấp khi đế hàng cuối ( tự động chọn mặt định hậu)
        """
        moves = []
        # trắng đi lên thì row giảm , đen đi xuống thì row tăng
        direction = -1 if color == WHITE else 1 # direcrion( phương hướng)
        start_row = 6 if color == WHITE else 1 # start row ( hàng mà xuất phát )
        promo_row = 0 if color == WHITE else 7 # promo_row (hàng điều kiện phong)
        
        # đi thẳng 1 ô --
        nr = r + direction
        if board.in_bounds(nr, c) and board.is_empty(nr, c):
            if nr == promo_row:
                # phong cấp: tạo 4 nước cho 4 lựa chọn
                for p in [QUEEN, ROOK, BISHOP, KNIGHT]:
                    moves.append(make_move(r,c,nr,c, promo=p)) # nên ghi promo=p tránh ghi p để sao có mở rộng thêm tham số trong hàm make_moves
            else:
                moves.append(make_move(r, c, nr, c))
        
            if r == start_row:
                nr2 = r + 2*direction
                if board.in_bounds(nr2, c) and board.is_empty(nr2, c):
                    moves.append(make_move(r,c, nr2, c))
        
        # ăn chéo 
        for dc in [-1,1]:
            nc = c + dc
            if board.in_bounds(nr, nc) and board.is_enemy(nr, nc, color):
                if nr == promo_row:
                    for p in [QUEEN, ROOK, BISHOP, KNIGHT]:
                        moves.append(make_move(r, c, nr, nc, promo=p))
                else:
                    moves.append(make_move(r, c, nr, nc))
        return moves
    
    def _knight_moves(self, board: Board, r: int , c: int, color: str) -> list:
        """mã : nhảy hình chữ L -8 hướng cố định.
        có thể nhảy qya qyaan khác , chỉ cần ô đó không có quân mình """
        moves = []
        jumps = [(-2,-1), (-2,+1), (-1, -2), (-1, +2), (+1, -2), (+1, +2), (+2,-1), (+2,+1), ]
        for dr, dc in jumps:
            nr,  nc = r + dr , c+ dc
            if board.in_bounds(nr, nc) and not board.is_friend(nr, nc, color):
                moves.append(make_move(r, c, nr, nc))
        return moves 
    
    def _bishop_moves(self, board: Board, r: int, c: int, color: str) -> list:
        """ tượng (bigshop): trược theo bốn đường chéo. 
        dừng khi gặp quân - ăn quân địch không ăn quân mình """
        return self._slide(board, r, c, color, [(-1,-1),(-1,+1), (+1,-1), (+1,+1)])
    
    def _rook_moves(self, board: Board, r: int, c: int, color: str) -> list:
        """xe(rook): trược hướng ngang dọc , gặp quân địch ăn - quân ta dừng"""
        return self._slide(board, r, c, color, [(-1,0), (+1,0), (0,-1), (0,+1)])
    
        
    def _queen_moves(self, board: Board, r: int, c: int, color: str) -> list:
        """"hậu(queen): kết hợp bigshop với rook """
        return self._slide(board, r , c, color, [
            (-1,-1),(-1,0), (-1,+1,),
            (0,-1),         (0,+1),
            (+1,-1), (+1,0), (+1,+1),
        ])
    
    def _king_moves(self, board: Board, r: int, c: int, color: str )-> list:
        """vua (king): di chuyển 1 ô theo 8 hướng."""
        moves = []
        for dr in [-1, 0, +1]:
            for dc in [-1, 0, +1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if board.in_bounds(nr,nc) and not board.is_friend(nr, nc , color):
                    moves.append(make_move(r, c, nr, nc))
        return moves
    #---------------------------------------------------#
    # Hàm hỗ trợ dùng cho tượng , xe , hậu
    #---------------------------------------------------#
    
    def _slide(self, board: Board, r: int, c: int, color: str, direction: list ) -> list:
        """sinh nước đi trược theo danh sách hướng (dr, dc).
        """
        moves = []
        for dr, dc in direction:
            nr, nc = dr + r, dc + c
            while board.in_bounds(nr, nc):
                if board.is_empty(nr, nc):
                    # ô trống -> đi được, tiếp tục trượt
                    moves.append(make_move(r, c, nr, nc))
                elif board.is_enemy(nr,nc,color):
                    # Quân địch -> ăn được, dừng
                    moves.append(make_move(r, c, nr, nc))
                    break
                else:
                    # Quân địch -> không đi được, dừng
                    break
                nr += dr 
                nc += dc
        return moves
    def _is_in_check(self, board: Board , color: str) -> bool:
        """kiểm tra vua của color có đang bị chiếu không
        Dùng nội bộ để lọc legal moves - KHÔNG dùng rules.py
        để tránh import vòng tròn.
        """
        king_pos = board.find_king(color)
        if not king_pos:
            return True # không có vua coi như bị chiếu
        king_r, king_c = king_pos # king_r , king_c vị trí cột dòng mà vua đang ở
        opponent = BLACK if color == WHITE else WHITE
        
        # Duyệt tất cả quân địch , xem có raw move nào tấn công vua không
        for r in range(8):
            for c in range(8):
                if board.color_at(r, c) == opponent:
                    for move in self.raw_moves(board, r, c):
                        if move['to_row'] == king_r and move['to_col'] == king_c:
                            return True
        return False 
    
    # attack square (ô tấn công)
    def attack_square(self, board: Board, row: int, col: int, by_color: str) -> bool:
        """kiêm tại 1 ô (row, col) có bị màu by_color tấn công hay không
        dùng trong rules.py để kiểm tra ô vua đi qua có an toàn không """
        for r in range(8):
            for c in range(8):
                if board.color_at(r,c) == by_color:
                    for move in self.raw_moves(board, r, c):
                        if move['to_row'] == row and move['to_col'] == col:
                            return True
        return False
    
    def move_to_index(self, move: dict) -> int: # biến một nước đi cơ vua thành một số nguyên
        # ví vụ từ e2 -> e4 là sẽ đại diện cho 1 số nào đó trong 0-4095
        # phân tích nước đi 1 ô bàn cờ 8x8 có 64 ô một nước đi có xuất phát -> ô đích có 64x64 = 4096 cặp nước đi
        """
        Chuyển nước đi thành index 0- 4095.
        Dùng cho Neural Network: policy head có 4096 output (64×64).
        from_square * 64 + to_square
        """
        from_sq = move['from_row'] * 8 + move['from_col'] # thức 
        to_sq   = move['to_row']   * 8 + move['to_col']
        return from_sq * 64 + to_sq
    
    @staticmethod
    def index_to_move(index: int) -> dict:
        """ chuyển index 0-4095 thành nước đi.
        ngược lại với move_to_index"""
        from_sq = index // 64
        to_sq = index % 64
        return make_move(
            from_sq // 8, from_sq % 8,
            to_sq // 8, to_sq %8, 
        )