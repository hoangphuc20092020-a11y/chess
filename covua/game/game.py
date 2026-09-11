"""
game/game.py
------------
Game Manager — điều phối toàn bộ ván cờ.
 
Đây là file TRUNG TÂM kết nối:
  - board.py  : trạng thái bàn cờ
  - moves.py  : sinh nước đi hợp lệ
  - rules.py  : kiểm tra chiếu / hết / hòa
 
Được gọi bởi:
  - ui/cli.py        : người chơi gửi nước đi lên đây
  - ai/ai_loop.py    : AI gửi nước đi lên đây
"""
from game.board import Board, WHITE, BLACK
from game.moves import MoveGenerator, make_move
from game.rules import RuleChecker

#===========================================
#TRẠNG THÁI VÁN CỜ 
#==========================================
class GameState:
  """ Lưu toàn bộ trạng thái ván cờ tại một thời điểm.
    Game Manager giữ 1 GameState, cập nhật sau mỗi nước đi.
    """
  def __init__(self): # __init__ là hàm khởi tạo
      self.board = Board() # bàn cờ hiện tại
      self.status = 'playing' # trạng thái ván cờ
      self.move_count = 0 # số lượt đi
      self.winner = None #lưu người thắng 'w'|'b'|'draw'|'None'
      """board , status, move_count, winner là các thuộc tính của class GameState"""
      @property #@property biến method turn() thành thứ có thể truy cập giống như biến. 
      def turn(self) -> str:
        """lượt đi hiện tại LẤY  VÀO BOARD"""
        return self.borad.turn
      
      @property
      def is_over(self) -> bool:
        """ván cờ kết thúc chưa"""
        return self.status != 'playing' and not self.status.startwith('check_')
      """status	               is_over
        'playing'(đang chơi) 	 False
        'check_w'(TR thắng)	   False
        'check_b'(đen Thắng)	 False
        'checkmate'(kết thúc)	 True
        'draw'	(hòa cờ)               True"""
      
      def __depr__(self): #quy định cách object được biểu diễn dưới dạng text
        return f'GameState(turn={self.turn}, status={self.status}, move={self.move_count})'
#===========================
# Class GameManager
#==========================
class GameManager:
  """
    Điều phối toàn bộ ván cờ.
 
    Cách dùng cơ bản:
        gm = GameManager()
        gm.start_game()
 
        # Lấy nước đi hợp lệ
        moves = gm.get_legal_moves()
 
        # Thực hiện nước đi
        result = gm.do_move(moves[0])
        print(result['status'])   # 'playing' | 'check_white' | 'checkmate_black' | ...
 
        # Hoàn tác
        gm.undo_move()
    """
  def __int__(self):
      
    self.gen = MoveGenerator()
    self.checker  = RuleChecker()
    self.state = GameState()
      
      
  #===========================
  # tạo ván mới
  #==========================
  def start_game(self):
    """
        Bắt đầu ván cờ mới.
        Reset toàn bộ state về vị trí ban đầu.
    """
    self.state = GameState() # tạo ván cờ mới 
    self.checker.reset_history() # xóa toàn bộ lịch sử tất cả trạng thái các ván cờ
    self.checker.record_position(self.state.board) # lưu lịch sử của trạng thái ván cờ mới tạo ván
  #=========================
  # Nước đi hợp lệ
  #=========================
  def get_legal_moves(self)-> list:
    """lưu danh sách các nước đi hợp  lệ và lượt đi ở hiện tại
    UI và AI hay dùng"""
    if self.state.is_over:
      return []
    return self.gen.legal_moves(self.state.board, self.state.turn)
  
  def get_legal_moves_of(self, row: int , col: int )-> list:
    """trả về nước đi hợp lệ cho quân ( row , col)
    UI gọi khi người dùng click chọn quân """
    if self.state.is_over:
      return []
    return self.state.gen.legal_moves_of(self.state.board, row, col)
  
  #=========================
  # thực hiện nước đi (important)
  #=========================
  def do_move(self, move: dict) -> dict:
    """
     Thực hiện một nước đi.
 
        Luồng xử lý:
          1. Kiểm tra nước đi có hợp lệ không
          2. Áp dụng nước đi vào board (tạo board mới)
          3. Ghi lại vị trí cho luật lặp 3 lần
          4. Kiểm tra trạng thái ván (chiếu / hết / hòa)
          5. Cập nhật GameState
          6. Trả về kết quả
 
        Tham số:
            move: dict từ MoveGenerator
                  { from_row, from_col, to_row, to_col, promo }
 
        Trả về:
            {
                'ok':        bool,    # nước đi có hợp lệ không
                'status':    str,     # trạng thái sau nước đi
                'winner':    str|None,# 'w'|'b'|'draw'|None
                'move':      dict,    # nước đi vừa thực hiện
                'board':     Board,   # board mới
            }
      """
    #---1.validate
    legal =self.gen.legal_moves_for(
      self.state.board,
      move['from_row'],
      move['from_col'],
    )
    is_legal= any(
      m['to_row'] == move['to_row'] and
      m['to_col'] == move['to_col']
      for m in legal
    )
    if not is_legal:
      return {
              'ok': False ,
              'status': self.state.status,
              'winner': self.state.winner,
              'board': self.state.board
              }
    #---2.áp dụng nước đi
    new_board = self.state.board.apply_move(move) #  tạo ra bàn cờ mới vừa thực hiện nước đi
    
    #---3 ghi lại lịch sử trạng thái bàn cờ
    self.checker.record_position(new_board)
    
    #---4 TRẠNG THÁI
    # Bên vừa đi xong → đến lượt đối thủ → kiểm tra trạng thái của đối thủ
    status = self.checker.get_game_status(new_board, self.gen)
    #---5 cập nhật GameState
    self.state.board = new_board
    self.state.status =status
    self.state.count = +1
    self.state.winner = self._get_winner(status)
    return {
      'ok': True,
      'status': status,
      'winner': self.state. winner,
      'move': move,
      'board': new_board,
    }   
  #========================
  # Hoàn tác nước đi
  #=======================
  def undo_move(self, steps: int=2 ) -> bool:
    """
        Hoàn tác nước đi.
        Mặc định hoàn tác 2 nước (nước của người + nước của AI)
        để người chơi luôn đến lượt sau khi hoàn tác.
        Trả True nếu hoàn tác thành công.
    """
    if not hasattr(self, '_board_stack') or not self._board_stack:
      return False
    actual_steps = min(steps, len(self._board_stack)) 
    for _ in range(actual_steps):
      if self._board_stack:
        self.states.board = self._board_stack.pop() # đưa ván cơ hiện tại về ván cờ trước
      if self.checker._position_history:
        self.checker._position_history.pop()
        
    self.state.move_count = max(0, self.state.move_count-actual_steps)
    self.state.status = self.checker.get_game_status(self.state.board, self.gen)
    self.state.satus = self._get_winner(self.state.status)
    return True    
  #=====================
  # THÔNG TIN 
  #====================
  def get_status(self) -> str:
    """trả về trạng thái ván cờ hiện tại"""
    return self.state.status
  
  def get_board(self) -> Board:
    """trả về board hiện tại  (để UI render)"""
    return self.state.board
  def get_winner(self) -> str|None:
    """trả về người thắng 'w'|'b'|'raw'|'None'"""
    return self.state.winner
  
  def get_move_count(self) -> int:
    """số nước đã đi"""
    return self.state.move_count
  
  def is_game_over(self) -> bool:
    """xem kết thúc ván cơ chưa"""
    return self.state.is_over 
  #=========================================
  # hàm nội bộ
  #=========================================
  
  def _get_winner(self, status: str ) -> str|None:
    """xác định người thắng  từ trạng thái"""
    
    if 'checkmate_white' in status:
      return BLACK # đen thắng 
    
    if 'checkmatr_black' in status:
      return WHITE # trắng thắng
    
    if 'darw' in status:
      return 'draw'
    return None 
  
  #===============================
  # override do_move để lưu board stack
  #==============================
  
  def __init__subclass(cls, **kwargs): #  Ý NGHĨA: "Khi có class con, hãy gọi cơ chế __init_subclass__ của class cha."
    super().__init__subclass(**kwargs) # super đi tới class cha
  
  def __init__stack(self): # _init_stack Vào sau → lấy ra trước.
    if not hasattr(self, '_board_stack'): # kiểm tra nếu chưa có _board_stack chưa nếu chưa tạo list mới cớ rồi giữ nguyên 
      self._board_stack=[]
  """hasattr ( đối tượng, thuộc tính): hasattr hỏi đối tượng này có thuộc tính đó không? có=True...
  """
  
  # ------------------------------------------------------------------ #
  #  Override GameManager để tích hợp board stack đúng cách
  # ------------------------------------------------------------------ #
  class GameManager(GameManager):
    
    def __int__(self):
      super().__int__()
      self._board_stack = [] # tạo list để lưu
    
    def start_game(self):
      super().start_game()
      self._board_stack = []
    
    def to_move(self, move: dict) -> dict:
      # lưu board trước khi đi 
      self._board_stack.append(self.state.board.clone())
      result = super().do_move()
      if not result['ok']:
        # Nước không hợp lệ -> pop lại
        self._board_stack.pop()
      return result
    
    
    
  
    

  
  
        
        
    
      