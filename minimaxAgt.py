from agent import Agent

class MinimaxAgent(Agent):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.max_depth = 4  # Độ sâu tối đa cho thuật toán minimax
        self.scores = {
            'x': -1,  # Điểm cho người chơi (X)
            'o': 1,   # Điểm cho AI (O)
            'draw': 0 # Điểm cho trường hợp hòa
        }
        # Nếu AI là X, đảo ngược điểm số
        if symbol == 'x':
            self.scores['x'] = 1
            self.scores['o'] = -1

    def get_move(self, game_array):
        best_score = float('-inf')
        best_move = None
        
        # Tìm tất cả các nước đi hợp lệ
        legal_moves = []
        for i in range(len(game_array)):
            for j in range(len(game_array[i])):
                if game_array[i][j][3]:  # Nếu ô còn trống (can_play == True)
                    legal_moves.append((i, j))
        
        # Thử từng nước đi và chọn nước đi tốt nhất
        for move in legal_moves:
            i, j = move
            x, y, _, _ = game_array[i][j]
            # Thử nước đi
            game_array[i][j] = (x, y, self.symbol, False)
            # Tính điểm cho nước đi này bằng minimax
            score = self.minimax(game_array, 0, False)
            # Hoàn tác nước đi
            game_array[i][j] = (x, y, "", True)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move

    def minimax(self, game_array, depth, is_maximizing):
        # TODO: Implement minimax algorithm
        pass

    def get_winner(self, game_array):
        # TODO: Implement check winner function
        pass

    def evaluate_board(self, game_array):
        # TODO: Implement board evaluation function
        pass