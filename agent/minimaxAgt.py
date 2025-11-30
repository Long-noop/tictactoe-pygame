from agent import Agent
import random

class MinimaxAgent(Agent):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.max_depth = 3  # Có thể tăng lên 4 với các tối ưu
        self.opponent = 'x' if symbol == 'o' else 'o'
        self.transposition_table = {}  # Cache để lưu các trạng thái đã tính

    def get_move(self, game_array):
        """Tìm nước đi tốt nhất sử dụng Minimax với Alpha-Beta Pruning"""
        # Clear cache mỗi lần đi để tránh memory leak
        if len(self.transposition_table) > 100000:
            self.transposition_table.clear()
        
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Tìm các nước đi hợp lệ, ưu tiên các ô gần quân đã đánh
        legal_moves = self._get_prioritized_moves(game_array)
        
        if not legal_moves:
            return None
        
        # Thử từng nước đi và chọn nước đi tốt nhất
        for move in legal_moves:
            i, j = move
            # Thử nước đi
            self._make_move(game_array, i, j, self.symbol)
            
            # Tính điểm cho nước đi này bằng minimax
            score = self._minimax(game_array, self.max_depth - 1, alpha, beta, False)
            
            # Hoàn tác nước đi
            self._undo_move(game_array, i, j)
            
            # Cập nhật nước đi tốt nhất
            if score > best_score:
                best_score = score
                best_move = move
            
            # Cập nhật alpha
            alpha = max(alpha, best_score)
            
            # Early termination nếu tìm thấy nước thắng chắc chắn
            if best_score >= 10000:
                break
        
        return best_move

    def _get_prioritized_moves(self, game_array):
        """
        Lấy các nước đi hợp lệ và sắp xếp theo độ ưu tiên
        Chỉ xét các ô trong khoảng 2 ô xung quanh các quân đã đánh
        """
        n = len(game_array)
        occupied = set()
        
        # Tìm tất cả các ô đã có quân
        for i in range(n):
            for j in range(n):
                if game_array[i][j][2] != "":
                    occupied.add((i, j))
        
        # Nếu bàn trống, đánh vào trung tâm
        if not occupied:
            center = n // 2
            return [(center, center)]
        
        # Tìm các ô trong vùng 2 ô xung quanh quân đã đánh
        candidate_moves = set()
        for (oi, oj) in occupied:
            for di in range(-2, 3):
                for dj in range(-2, 3):
                    ni, nj = oi + di, oj + dj
                    if 0 <= ni < n and 0 <= nj < n and game_array[ni][nj][3]:
                        candidate_moves.add((ni, nj))
        
        # Nếu không có nước đi nào, return tất cả nước đi hợp lệ
        if not candidate_moves:
            return self._get_all_legal_moves(game_array)
        
        # Đánh giá và sắp xếp các nước đi theo điểm
        moves_with_scores = []
        for move in candidate_moves:
            i, j = move
            # Đánh giá nhanh nước đi này
            score = self._quick_evaluate_move(game_array, i, j)
            moves_with_scores.append((score, move))
        
        # Sắp xếp theo điểm giảm dần
        moves_with_scores.sort(reverse=True, key=lambda x: x[0])
        
        # Chỉ lấy top 15-20 nước đi tốt nhất để giảm branching factor
        max_moves = min(20, len(moves_with_scores))
        return [move for _, move in moves_with_scores[:max_moves]]

    def _quick_evaluate_move(self, game_array, i, j):
        """Đánh giá nhanh một nước đi mà không cần minimax"""
        score = 0
        
        # Thử đánh cả hai symbol để xem nước đi này có tạo thế tấn công/phòng thủ không
        for symbol in [self.symbol, self.opponent]:
            self._make_move(game_array, i, j, symbol)
            
            # Kiểm tra xem có tạo thế thắng không
            if self._check_winner(game_array) == symbol:
                self._undo_move(game_array, i, j)
                return 10000 if symbol == self.symbol else 9000
            
            # Đếm số chuỗi 4, 3, 2 tạo được
            board = self._get_board(game_array)
            temp_score = self._count_threats(board, i, j, symbol)
            
            if symbol == self.symbol:
                score += temp_score
            else:
                score += temp_score * 0.9  # Phòng thủ quan trọng nhưng ít hơn tấn công
            
            self._undo_move(game_array, i, j)
        
        return score

    def _count_threats(self, board, row, col, symbol):
        """Đếm số lượng thế nguy hiểm tại một vị trí"""
        n = len(board)
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # ngang, dọc, chéo xuôi, chéo ngược
        
        for dr, dc in directions:
            # Đếm chuỗi trong mỗi hướng
            count = 1  # Đếm ô hiện tại
            empty = 0
            
            # Đếm về phía trước
            for step in range(1, 5):
                r, c = row + dr * step, col + dc * step
                if 0 <= r < n and 0 <= c < n:
                    if board[r][c] == symbol:
                        count += 1
                    elif board[r][c] == "":
                        empty += 1
                        break
                    else:
                        break
                else:
                    break
            
            # Đếm về phía sau
            for step in range(1, 5):
                r, c = row - dr * step, col - dc * step
                if 0 <= r < n and 0 <= c < n:
                    if board[r][c] == symbol:
                        count += 1
                    elif board[r][c] == "":
                        empty += 1
                        break
                    else:
                        break
                else:
                    break
            
            # Tính điểm dựa trên số quân liên tiếp
            if count >= 4:
                score += 1000
            elif count == 3 and empty >= 1:
                score += 100
            elif count == 2 and empty >= 2:
                score += 10
        
        return score

    def _minimax(self, game_array, depth, alpha, beta, is_maximizing):
        """Thuật toán Minimax với Alpha-Beta Pruning và Transposition Table"""
        
        # Tạo hash key cho trạng thái hiện tại
        board_key = self._get_board_hash(game_array)
        
        # Kiểm tra trong cache
        if board_key in self.transposition_table:
            cached_depth, cached_score = self.transposition_table[board_key]
            if cached_depth >= depth:
                return cached_score
        
        # Kiểm tra điều kiện dừng
        winner = self._check_winner(game_array)
        if winner == self.symbol:
            return 10000 + depth
        elif winner == self.opponent:
            return -10000 - depth
        elif self._is_draw(game_array):
            return 0
        
        if depth == 0:
            score = self._evaluate_board(game_array)
            self.transposition_table[board_key] = (depth, score)
            return score
        
        # Lấy các nước đi được ưu tiên
        legal_moves = self._get_prioritized_moves(game_array)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                i, j = move
                self._make_move(game_array, i, j, self.symbol)
                eval_score = self._minimax(game_array, depth - 1, alpha, beta, False)
                self._undo_move(game_array, i, j)
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Beta cutoff
            
            self.transposition_table[board_key] = (depth, max_eval)
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                i, j = move
                self._make_move(game_array, i, j, self.opponent)
                eval_score = self._minimax(game_array, depth - 1, alpha, beta, True)
                self._undo_move(game_array, i, j)
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            
            self.transposition_table[board_key] = (depth, min_eval)
            return min_eval

    def _get_board_hash(self, game_array):
        """Tạo hash key cho trạng thái bàn cờ"""
        return tuple(tuple(game_array[i][j][2] for j in range(len(game_array[i]))) 
                    for i in range(len(game_array)))

    def _get_all_legal_moves(self, game_array):
        """Lấy tất cả các nước đi hợp lệ"""
        moves = []
        for i in range(len(game_array)):
            for j in range(len(game_array[i])):
                if game_array[i][j][3]:
                    moves.append((i, j))
        return moves

    def _make_move(self, game_array, i, j, symbol):
        """Thực hiện nước đi"""
        x, y, _, _ = game_array[i][j]
        game_array[i][j] = (x, y, symbol, False)

    def _undo_move(self, game_array, i, j):
        """Hoàn tác nước đi"""
        x, y, _, _ = game_array[i][j]
        game_array[i][j] = (x, y, "", True)

    def _get_board(self, game_array):
        """Chuyển game_array sang board 2D đơn giản"""
        return [[game_array[r][c][2] for c in range(len(game_array[r]))] for r in range(len(game_array))]

    def _check_winner(self, game_array):
        """Kiểm tra xem có ai thắng không"""
        board = self._get_board(game_array)
        n = len(board)
        
        # Chỉ kiểm tra xung quanh các quân vừa đánh gần đây
        for r in range(n):
            for c in range(n - 4):
                seq = [board[r][c + k] for k in range(5)]
                if seq[0] != "" and all(x == seq[0] for x in seq):
                    return seq[0]
        
        for c in range(n):
            for r in range(n - 4):
                seq = [board[r + k][c] for k in range(5)]
                if seq[0] != "" and all(x == seq[0] for x in seq):
                    return seq[0]
        
        for r in range(n - 4):
            for c in range(n - 4):
                seq = [board[r + k][c + k] for k in range(5)]
                if seq[0] != "" and all(x == seq[0] for x in seq):
                    return seq[0]
        
        for r in range(n - 4):
            for c in range(4, n):
                seq = [board[r + k][c - k] for k in range(5)]
                if seq[0] != "" and all(x == seq[0] for x in seq):
                    return seq[0]
        
        return None

    def _is_draw(self, game_array):
        """Kiểm tra xem bàn cờ đã đầy chưa (hòa)"""
        # Chỉ kiểm tra trong vùng có quân
        for row in game_array:
            for cell in row:
                if cell[3]:
                    return False
        return True

    def _evaluate_board(self, game_array):
        """Hàm đánh giá trạng thái bàn cờ - version tối ưu"""
        board = self._get_board(game_array)
        score = 0
        n = len(board)
        
        # Chỉ đánh giá các đoạn có ít nhất 1 quân
        def evaluate_segment(segment, player):
            opponent = self.opponent if player == self.symbol else self.symbol
            
            if opponent in segment:
                return 0
            
            player_count = segment.count(player)
            
            if player_count == 4:
                return 500
            elif player_count == 3:
                return 50
            elif player_count == 2:
                return 10
            elif player_count == 1:
                return 1
            return 0
        
        # Đánh giá hàng ngang
        for r in range(n):
            for c in range(n - 4):
                segment = [board[r][c + k] for k in range(5)]
                if "" not in segment or segment.count("") <= 2:  # Chỉ đánh giá nếu có tiềm năng
                    score += evaluate_segment(segment, self.symbol)
                    score -= evaluate_segment(segment, self.opponent)
        
        # Đánh giá hàng dọc
        for c in range(n):
            for r in range(n - 4):
                segment = [board[r + k][c] for k in range(5)]
                if "" not in segment or segment.count("") <= 2:
                    score += evaluate_segment(segment, self.symbol)
                    score -= evaluate_segment(segment, self.opponent)
        
        # Đánh giá chéo xuôi
        for r in range(n - 4):
            for c in range(n - 4):
                segment = [board[r + k][c + k] for k in range(5)]
                if "" not in segment or segment.count("") <= 2:
                    score += evaluate_segment(segment, self.symbol)
                    score -= evaluate_segment(segment, self.opponent)
        
        # Đánh giá chéo ngược
        for r in range(n - 4):
            for c in range(4, n):
                segment = [board[r + k][c - k] for k in range(5)]
                if "" not in segment or segment.count("") <= 2:
                    score += evaluate_segment(segment, self.symbol)
                    score -= evaluate_segment(segment, self.opponent)
        
        return score