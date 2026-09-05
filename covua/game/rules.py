from game.board import Board, WHITE, BLACK
from game.moves import MoveGenerator

class RuleChecker:
    #CLASS NÀY KIỂM TRA 3 TRẠNG THÁI CHÍNH:
    """1.is_in_check - vua đang bị chiếu
    2. is_checkmate - chiếu hết (thua)
    3. is_draw - hòa cờ (stalemate/ lặp lại trạng thái 3 lần/ 50 nước)"""
    
    def __init__(self):  # __ ngay đầu có nghĩa khởi tạo khi RuleChecker được tạo vd rc= RuleChecker() THÌ __position_history được khởi tạo ngay rỗng
        self._position_history: list[str] = []
        # khởi tạo ra để lưu lịch sự trạng thái bàn cờ ví dụ ["bRbN...|bP...|...|wPw...|wRbN...|w"]
        
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
    
    # HÒA CỜ
    def is_draw (self,board: Board, gen: MoveGenerator, color ) ->bool:
        
        """Hòa khi một trong các điều kiện sau xảy ra:
          a) Stalemate      — không bị chiếu nhưng không còn nước đi
          b) Lặp vị trí 3x — cùng thế cờ xuất hiện 3 lần
          c) Quy tắc 50 nước — 50 nước liên tiếp không ăn quân, không đi tốt
          d) Thiếu quân     — không đủ quân để chiếu hết
          """
        return (
            self.is_stalemate(board , gen , color)
            or self.is_threefold_repetition()
            or self.is_fifty_move_rule(board)
            or self.is_insufficient_material(board)
        )
    
    def is_stalemate(self, board: Board , gen: MoveGenerator, color) -> bool:
        """hòa cờ không còn nước đi hợp lệ"""
        if  self.is_in_check(board , gen, color): 
            return False
        return len(gen.legal_moves(board, color))==0
    
    
    def is_threefold_repetition(self) -> bool:
        """check 1 trạng thái bàn cờ có xuất hiện three lần không"""
        if len(self._position_history()) < 3:
            return False
        for pos in set(self._position_history): # set lượt bỏ trùng lập list VD _position_history={"A", "B","C", "A"} thì set làm thành còn {"A", "B","C"} lưu ý này không làm mất dữ liệu trong _p_h
            if self._position_history(pos).count >= 3:
                return True
        return False
    
    def is_fifty_move_rule(self,board: Board):
        """
        Quy tắc 50 nước: nếu 50 nước liên tiếp không có quân bị ăn
        và không có tốt nào di chuyển → hòa.
 
        Đếm từ lịch sử nước đi của board:
        - Reset về 0 khi: tốt di chuyển hoặc quân bị ăn
        - Đạt 100 half-moves (50 nước mỗi bên) → hòa
        """
        half_move_clock = 0
        for snapshot in reversed(board.history): # reversed() chi ngược danh sách
            captured = snapshot['captured'] # quân bị ăn (None nếu không)
            piece = snapshot['piece'] # quân vừa di chuyển
            
            # reset nếu ăn quân hoặc tốt di chuyển
            if captured or (piece and piece[1] =='p'):
                break
            half_move_clock += 1
        return half_move_clock >= 100
    
    def is_insufficient_material(self, board: Board) -> bool:
        """
        Thiếu quân để chiếu hết → hòa tự động.
 
        Các trường hợp hòa do thiếu quân:
          - Vua vs Vua
          - Vua + Tượng vs Vua
          - Vua + Mã vs Vua
          - Vua + Tượng vs Vua + Tượng (cùng màu ô)
        """
        pieces = {'w': [], 'b': []}
        for r in range(8):
            for c in range(8):
                p = board.get(r,c)
                if p:
                    pieces[p[0]].append((p[1], r, c))
        
        # loại bỏ vua khỏi danh sách để kiểm tra
        
                    
        
    
    def record_position(self, board: Board):
        """ ghi lại lịch sử vị trí của 1 trạng thái bàn cờ khi thực hiện nước cờ
        """
        self._position_history.append(self._board_to_key(board))
        
    def reset_history(self):
        """xóa lịch sử khi bắt đầu ván mới"""
        self._position_history = []
        
        
    @staticmethod
    def _board_to_key(board: Board ) -> str:
        """chuyển trạng thái bàn cờ thành chuỗi key
        để kiểm tra lặp lại 3 lần"""
        rows =[]
        for r in range(8):
            row = ''.join(
                board.get(r, c) or '.' for c in range(8)
                )
            rows.append(row)
        return '|'.join(rows) + f'|{board.turn}'
            
        
    
    