import numpy as np
from typing import Optional
# màu cờ
WHITE = 'w'
BLACK = 'b'
# loại quân
KING = 'K'
QUEEN = 'Q'
ROOK = 'R'
BISHOP = 'B'
KNIGHT = 'N'
PAWN = 'P'
# ký hiệu Unicode để in ra terminal
PIECE_UNICODE = {
    'wK': '♔', 'wQ': '♕', 'wR': '♖', 'wB': '♗', 'wN': '♘', 'wP': '♙',
    'bK': '♚', 'bQ': '♛', 'bR': '♜', 'bB': '♝', 'bN': '♞', 'bP': '♟',  
}

# tạo điểm cho từng quân cờ ( dùng cho AI evaluation )
PIECE_VALUES = {
    PAWN: 100,
    KNIGHT: 320,
    BISHOP: 330,
    ROOK: 500,
    QUEEN: 900,
    KING: 20000,
}
# khởi tạo trạng thái ban đầu của bàn cờ
INITIAL_BOARD =[
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
    
]

class Board:
    """
    Biểu diễn bàn cơ 8x8.
    mỗi ô là None (trống) hoặc chuỗi 2 ký tự:
    - ký tự 1: màu ('w' = trắng , 'b' = đen)
    - ký tự 2: type ('K','Q','R','B','N','P')
    ví dụ: 'wK'"= vua trắng 
    
    """
    def __init__(self):
        # Mảng 8x8 lưu vị trí quân
        self.grid = [row[:] for row in INITIAL_BOARD] # row[:] giúp tạo một bản sao hoàn toàn độc lập của từng hang
        
        # lượt đi hiện tại
        self.turn = WHITE 
        
        # Nước đi cuối cùng 
        self.last_move = None
        
        # lịch sử các nước đi ( dùng để hoàn tắt )
        self.history = []
        
    # ------- #
    # Truy cập ô
    #---------#
    
     # lấy quân tại (row, col), trả về None nếu trống
    def get(self, row: int, col: int ) -> Optional[str]:
        return self.grid[row][col]
    
     # lấy quân tại (row, col).
    def set(self, row: int, col: int, piece: Optional[str]):
        self.grid[row][col] = piece
    
    # kiểm tra ô có trống không
    def is_empty(self, row: int, col: int) -> bool:
        return self.grid[row][col] is None # bool là true hoặc false
         # nếu ô (row, col) rỗng thì true ngược lại
    
    # kiểm tra tọa độ có nằm trong bàn cơ không
    def in_bounds(self, row: int , col: int) -> bool:
        return 0 <= row < 8 and 0 <= col < 8
 
    #------#
    # thông tin quân cờ
    #-----#
    
    @staticmethod
    def color_of(piece: str) -> str:
        return piece[0] # lấy màu quân: 'wK' -> 'w'
    
    @staticmethod
    def type_of(piece: str) -> str:
        return piece[1] # lấy loại quân
    
    def color_at(self, row: int, col: int) -> Optional[str]:
        piece = self.grid[row][col] 
        return piece[0] if  piece else None # lấy màu quân tại ô trả về None nếu trống
    
    def is_enemy(self, row: int, col: int, color: str) -> bool:
        piece = self.grid[row][col]
        return piece is not None and piece[0] != color #d KT có phải quân địch không
    
    def is_friend(self, row: int, col: int, color: str) -> bool:
        piece = self.grid[row][col]
        return piece is not None and piece == color
    
    
    # ---------------------------------------------------------------- #
    #  Áp dụng nước đi
    # ---------------------------------------------------------------- #   
    
    def apply_move(self, move: dict) -> 'Board': # Board nằm trong ngoặc '' vì hàm này nằm trong chính lớp Board lúc này lớp Board vấn chưa định nghĩa xong nên dùng '' để python không bị lỗi
        """
        Áp dụng nước đi, trả về Board MỚI (không thay đổi board hiện tại).
        move = {
            'from_row': int, 'from_col': int,
            'to_row':   int, 'to_col':   int,
            'promo':    str | None   (phong cấp: 'Q','R','B','N')
        }
        """
        new_board = self.clone() # tạo bản sao của bàn cờ hiện tại
        fr, fc = move['from_row'], move['from_col']
        tr, tc = move['to_row'], move['to_col']
        
        piece = new_board.grid[fr][fc]
        new_board.grid[tr][tc] = piece
        new_board.grid[fr][fc] = None
        
        if move.get('promo'):
           color = self.color_of(piece)
           new_board.grid[tr][tc] = color + move['promo']
        
        new_board.last_move = move
        new_board.turn = BLACK if self.turn == WHITE else WHITE
        return new_board 
    # ---------------------------------------------------------------- #
    #  Clone & Reset
    # ---------------------------------------------------------------- #
    def clone(self) -> 'Board':
        """tạo bản sao độc lập của Board. """
        new_board = Board.__new__(Board) # dòng này giúp tạo ra bản thể Board mới mà không kích hoạt lại quy trình khởi tạo ban đầu
        new_board.grid = [row[:] for row in self.grid]
        new_board.turn = self.turn
        new_board.last_move = self.last_move
        new_board.history = self.history[:]
        return new_board
    
    def reset(self):
        """reset về vị trí ban đầu"""
        self.grid = [row[:] for row in INITIAL_BOARD]
        self.turn = WHITE
        self.last_move = None
        self.history = []
        
    # ---------------------------------------------------------------- #
    #  Tìm kiếm
    # ---------------------------------------------------------------- #    
    def find_king(self, color: str) -> Optional[tuple]:
        """tìm vị trí vua. Trả (row, col) hoặc None"""
        target = color + KING # target- mục tiêu
        for r in range(8):
            for c in range(8):
                if self.grid[r][c] == target:
                    return (r,c)
        return None
    
    def find_pieces(self, color:str ) -> list:
        """ Trả về danh sách (row, col) tất cả quân của một màu"""
        pieces = []
        for r in range(8):
            for c in range(8):
                if self.color_at(r,c) == color:
                    pieces.append((r, c))
        return pieces
# ---------------------------------------------------------------- #
#  Chuyển đổi định dạng
# ---------------------------------------------------------------- #
    @staticmethod
    def to_algebraic(row: int , col: int ) -> str: # algebraic nghĩa là đại số
        return 'abcdefgh'[col] + str(8 - row)
    
    @staticmethod
    def from_algebraic(notation: str) -> tuple:
        """e2 -> (6, 4)"""
        col = ord(notation[0]) - ord('a') # [0] chính là e Vd e=101 -ord('a')= 97 = 4
        row = 8 -int(notation[1])
        return (row, col) 
     
    def to_tensor(self) -> np.ndarray:
        """ chuyển board thành tensor 8x8x12 dùng cho Netword.
        12 kênh = 6 quân 2 màu 
        giá trị 1 = có quân, 0 = không quân"""
        tensor = np.zeros((8,8,12), dtype = np.float32)
        
        # đây là Dicrionary
        piece_to_channel = {
            'wp': 0, 'wN': 1, 'wB': 2,
            'wR': 3, 'wQ': 4, 'WK': 5,
            
            'bp': 6, 'bN': 7, 'bB': 8,
            'bR': 9, 'bQ': 10, 'bK': 11,
        }
        
        for r in range(8):
            for c in range(8):
             piece = self.grid[r][c]
             if piece and piece in piece_to_channel:
                 tensor[r][c][piece_to_channel[piece]] =1.0
        return tensor

    # ---------------------------------------------------------------- #
    #  In ra terminal
    # ---------------------------------------------------------------- #
    def __str__(self) -> str:
        """In bàn cờ ra terminal với ký hiệu Unicode."""
        lines = []
        lines.append('  a b c d e f g h')
        lines.append('  ─────────────────')
        for r in range(8):
            row_str = f'{8 - r} │'
            for c in range(8):
                piece = self.grid[r][c]
                symbol = PIECE_UNICODE.get(piece, '·') if piece else '·'
                row_str += f'{symbol} '
            row_str += f'│ {8 - r}'
            lines.append(row_str)
        lines.append('  ─────────────────')
        lines.append('  a b c d e f g h')
        lines.append(f"\n  Lượt: {'Trắng' if self.turn == WHITE else 'Đen'}")
        return '\n'.join(lines)
 
    def __repr__(self) -> str:
        return f'Board(turn={self.turn})'

if __name__ == '__main__':
    board = Board()
    print(board)
    print()
 
    # Test clone
    board2 = board.clone()
    board2.set(6, 4, None)  # xóa tốt e2 trên board2
    print('board gốc ô e2:', board.get(6, 4))   # vẫn còn 'wP'
    print('board2   ô e2:', board2.get(6, 4))   # None
 
    # Test to_algebraic
    print('(6,4) →', Board.to_algebraic(6, 4))  # e2
    print('e2 →', Board.from_algebraic('e2'))    # (6, 4)
 
    # Test tensor shape
    tensor = board.to_tensor()
    print('Tensor shape:', tensor.shape)          # (8, 8, 12)
 
    # Test find_king
    print('Vua trắng:', board.find_king('w'))    # (7, 4)
    print('Vua đen:  ', board.find_king('b'))    # (0, 4)