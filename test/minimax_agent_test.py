"""
Script để test tỉ lệ thắng của các agent
Yêu cầu: Minimax Agent thắng Random Agent >= 90%
"""


import time
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(".."))
from agent.minimaxAgt import MinimaxAgent
from agent.randomAgt import RandomAgent

class GameSimulator:
    def __init__(self, rows=9):
        self.rows = rows
        
    def initialize_game(self):
        """Khởi tạo bàn cờ rỗng"""
        return [["" for _ in range(self.rows)] for _ in range(self.rows)]
    
    def convert_to_game_array(self, board):
        """Chuyển board thành format game_array cho agents"""
        game_array = []
        gap = 80  # Giả định
        for i in range(self.rows):
            row = []
            for j in range(self.rows):
                x = j * gap + gap // 2
                y = i * gap + gap // 2
                symbol = board[i][j]
                can_play = (symbol == "")
                row.append((x, y, symbol, can_play))
            game_array.append(row)
        return game_array
    
    def check_winner(self, board):
        """Kiểm tra có người thắng không (5 liên tiếp)"""
        n = len(board)
        
        # Kiểm tra hàng ngang
        for r in range(n):
            for c in range(n - 4):
                seq = [board[r][c + k] for k in range(5)]
                if seq[0] != "" and all(x == seq[0] for x in seq):
                    return seq[0]
        
        # Kiểm tra hàng dọc
        for c in range(n):
            for r in range(n - 4):
                seq = [board[r + k][c] for k in range(5)]
                if seq[0] != "" and all(x == seq[0] for x in seq):
                    return seq[0]
        
        # Kiểm tra chéo xuôi
        for r in range(n - 4):
            for c in range(n - 4):
                seq = [board[r + k][c + k] for k in range(5)]
                if seq[0] != "" and all(x == seq[0] for x in seq):
                    return seq[0]
        
        # Kiểm tra chéo ngược
        for r in range(n - 4):
            for c in range(4, n):
                seq = [board[r + k][c - k] for k in range(5)]
                if seq[0] != "" and all(x == seq[0] for x in seq):
                    return seq[0]
        
        return None
    
    def is_board_full(self, board):
        """Kiểm tra bàn cờ đã đầy chưa"""
        return all(board[i][j] != "" for i in range(self.rows) for j in range(self.rows))
    
    def play_game(self, agent1, agent2, verbose=False, max_moves=81):
        """
        Chơi một ván game giữa 2 agents
        
        Args:
            agent1: Agent đi trước (X)
            agent2: Agent đi sau (O)
            verbose: In thông tin chi tiết
            max_moves: Số nước tối đa (tránh game vô hạn)
        
        Returns:
            winner: 'x', 'o', hoặc 'draw'
            moves: Số nước đi
        """
        board = self.initialize_game()
        current_agent = agent1
        current_symbol = 'x'
        move_count = 0
        
        if verbose:
            print(f"\n=== New Game: {agent1.__class__.__name__} (X) vs {agent2.__class__.__name__} (O) ===")
        
        while move_count < max_moves:
            # Chuyển board sang game_array format
            game_array = self.convert_to_game_array(board)
            
            # Agent chọn nước đi
            move = current_agent.get_move(game_array)
            
            if move is None:
                if verbose:
                    print(f"No valid move available!")
                break
            
            i, j = move
            
            # Kiểm tra nước đi hợp lệ
            if board[i][j] != "":
                if verbose:
                    print(f"Invalid move at ({i},{j})!")
                return 'invalid', move_count
            
            # Thực hiện nước đi
            board[i][j] = current_symbol
            move_count += 1
            
            if verbose:
                print(f"Move {move_count}: {current_symbol.upper()} -> ({i},{j})")
            
            # Kiểm tra thắng
            winner = self.check_winner(board)
            if winner:
                if verbose:
                    print(f"\n🎉 {winner.upper()} wins after {move_count} moves!")
                    self.print_board(board)
                return winner, move_count
            
            # Kiểm tra hòa
            if self.is_board_full(board):
                if verbose:
                    print(f"\n🤝 Draw after {move_count} moves!")
                    self.print_board(board)
                return 'draw', move_count
            
            # Đổi lượt
            current_agent = agent2 if current_agent == agent1 else agent1
            current_symbol = 'o' if current_symbol == 'x' else 'x'
        
        if verbose:
            print(f"\n⏱️ Game timeout after {max_moves} moves!")
        return 'timeout', move_count
    
    def print_board(self, board):
        """In bàn cờ ra console"""
        print("\n  ", end="")
        for j in range(self.rows):
            print(f"{j} ", end="")
        print()
        
        for i in range(self.rows):
            print(f"{i} ", end="")
            for j in range(self.rows):
                symbol = board[i][j] if board[i][j] != "" else "."
                print(f"{symbol} ", end="")
            print()


def run_test_suite(num_games=100, test_name="Minimax vs Random"):
    """
    Chạy test suite với số lượng games nhất định
    
    Args:
        num_games: Số ván chơi
        test_name: Tên test
    
    Returns:
        results: Dictionary chứa kết quả
    """
    print(f"\n{'='*70}")
    print(f"  {test_name}")
    print(f"  Testing {num_games} games")
    print(f"{'='*70}\n")
    
    simulator = GameSimulator(rows=9)
    
    # Khởi tạo agents
    minimax_agent = MinimaxAgent('x')
    random_agent = RandomAgent('o')
    
    # Thống kê
    results = {
        'minimax_wins': 0,
        'random_wins': 0,
        'draws': 0,
        'invalid': 0,
        'timeout': 0,
        'total_moves': 0,
        'game_details': []
    }
    
    start_time = time.time()
    
    # Chạy các games
    for game_num in range(1, num_games + 1):
        verbose = (game_num <= num_games)  # Chỉ in chi tiết 3 game đầu
        
        winner, moves = simulator.play_game(
            minimax_agent, 
            random_agent, 
            verbose=verbose
        )
        
        # Cập nhật thống kê
        if winner == 'x':
            results['minimax_wins'] += 1
        elif winner == 'o':
            results['random_wins'] += 1
        elif winner == 'draw':
            results['draws'] += 1
        elif winner == 'invalid':
            results['invalid'] += 1
        elif winner == 'timeout':
            results['timeout'] += 1
        
        results['total_moves'] += moves
        results['game_details'].append({
            'game': game_num,
            'winner': winner,
            'moves': moves
        })
        
        # Progress bar
        # if game_num % 10 == 0 or game_num <= 3:
        elapsed = time.time() - start_time
        avg_time = elapsed / game_num
        remaining = avg_time * (num_games - game_num)
        
        minimax_win_rate = (results['minimax_wins'] / game_num) * 100
        
        print(f"Game {game_num}/{num_games} | "
                f"Minimax: {results['minimax_wins']} ({minimax_win_rate:.1f}%) | "
                f"Random: {results['random_wins']} | "
                f"Draw: {results['draws']} | "
                f"ETA: {remaining:.0f}s")
    
    elapsed_time = time.time() - start_time
    
    # Tính toán kết quả
    total_decided = results['minimax_wins'] + results['random_wins']
    minimax_win_rate = (results['minimax_wins'] / num_games) * 100 if num_games > 0 else 0
    avg_moves = results['total_moves'] / num_games if num_games > 0 else 0
    
    # In kết quả
    print(f"\n{'='*70}")
    print(f"  RESULTS")
    print(f"{'='*70}")
    print(f"Total games:          {num_games}")
    print(f"Total time:           {elapsed_time:.2f}s")
    print(f"Average time/game:    {elapsed_time/num_games:.2f}s")
    print(f"Average moves/game:   {avg_moves:.1f}")
    print(f"\n{'─'*70}")
    print(f"Minimax wins:         {results['minimax_wins']} ({minimax_win_rate:.2f}%)")
    print(f"Random wins:          {results['random_wins']} ({results['random_wins']/num_games*100:.2f}%)")
    print(f"Draws:                {results['draws']} ({results['draws']/num_games*100:.2f}%)")
    print(f"Invalid games:        {results['invalid']}")
    print(f"Timeout games:        {results['timeout']}")
    print(f"{'─'*70}\n")
    
    # Đánh giá
    if minimax_win_rate >= 90:
        print(f"✅ PASS: Minimax win rate {minimax_win_rate:.2f}% >= 90%")
    else:
        print(f"❌ FAIL: Minimax win rate {minimax_win_rate:.2f}% < 90%")
        print(f"   Need to improve by {90 - minimax_win_rate:.2f}%")
    
    print(f"{'='*70}\n")
    
    # Lưu kết quả ra file
    results['summary'] = {
        'test_name': test_name,
        'num_games': num_games,
        'minimax_win_rate': minimax_win_rate,
        'elapsed_time': elapsed_time,
        'avg_moves': avg_moves,
        'timestamp': datetime.now().isoformat()
    }
    
    return results


def save_results(results, filename='test_results.json'):
    """Lưu kết quả test ra file JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {filename}")


def run_quick_test():
    """Test nhanh với 10 games"""
    print("\n🚀 Running Quick Test (10 games)...\n")
    results = run_test_suite(num_games=10, test_name="Quick Test: Minimax vs Random")
    return results


def run_standard_test():
    """Test chuẩn với 100 games"""
    print("\n🎯 Running Standard Test (100 games)...\n")
    results = run_test_suite(num_games=100, test_name="Standard Test: Minimax vs Random")
    save_results(results, 'test_results_100.json')
    return results


def run_extensive_test():
    """Test mở rộng với 500 games"""
    print("\n🔥 Running Extensive Test (500 games)...\n")
    results = run_test_suite(num_games=500, test_name="Extensive Test: Minimax vs Random")
    save_results(results, 'test_results_500.json')
    return results


def analyze_results(results):
    """Phân tích chi tiết kết quả"""
    print(f"\n{'='*70}")
    print(f"  DETAILED ANALYSIS")
    print(f"{'='*70}\n")
    
    # Phân tích moves
    moves_list = [game['moves'] for game in results['game_details']]
    avg_moves = sum(moves_list) / len(moves_list)
    min_moves = min(moves_list)
    max_moves = max(moves_list)
    
    print(f"Move Statistics:")
    print(f"  Average: {avg_moves:.1f}")
    print(f"  Min:     {min_moves}")
    print(f"  Max:     {max_moves}")
    
    # Phân tích theo độ dài game
    short_games = sum(1 for m in moves_list if m < 20)
    medium_games = sum(1 for m in moves_list if 20 <= m < 40)
    long_games = sum(1 for m in moves_list if m >= 40)
    
    print(f"\nGame Length Distribution:")
    print(f"  Short (<20 moves):   {short_games}")
    print(f"  Medium (20-40):      {medium_games}")
    print(f"  Long (>=40):         {long_games}")
    
    # Phân tích win rate theo độ dài
    minimax_wins_short = sum(1 for g in results['game_details'] 
                             if g['winner'] == 'x' and g['moves'] < 20)
    minimax_wins_medium = sum(1 for g in results['game_details'] 
                              if g['winner'] == 'x' and 20 <= g['moves'] < 40)
    minimax_wins_long = sum(1 for g in results['game_details'] 
                            if g['winner'] == 'x' and g['moves'] >= 40)
    
    print(f"\nMinimax Win Rate by Game Length:")
    if short_games > 0:
        print(f"  Short games:   {minimax_wins_short}/{short_games} ({minimax_wins_short/short_games*100:.1f}%)")
    if medium_games > 0:
        print(f"  Medium games:  {minimax_wins_medium}/{medium_games} ({minimax_wins_medium/medium_games*100:.1f}%)")
    if long_games > 0:
        print(f"  Long games:    {minimax_wins_long}/{long_games} ({minimax_wins_long/long_games*100:.1f}%)")
    
    print(f"{'='*70}\n")


if __name__ == "__main__":
    import sys
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                   TIC-TAC-TOE AGENT TESTING SUITE                  ║
║                                                                    ║
║  Testing requirement: Minimax Agent win rate >= 90% vs Random     ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Menu
    print("Choose test mode:")
    print("  1. Quick Test (10 games) - ~30 seconds")
    print("  2. Standard Test (100 games) - ~5 minutes")
    print("  3. Extensive Test (500 games) - ~25 minutes")
    print("  4. Custom number of games")
    
    choice = input("\nEnter choice (1-4) [default: 2]: ").strip() or "2"
    
    if choice == "1":
        results = run_quick_test()
    elif choice == "2":
        results = run_standard_test()
    elif choice == "3":
        results = run_extensive_test()
    elif choice == "4":
        try:
            num = int(input("Enter number of games: "))
            results = run_test_suite(num_games=num, test_name=f"Custom Test: {num} games")
            save_results(results, f'test_results_{num}.json')
        except ValueError:
            print("Invalid number!")
            sys.exit(1)
    else:
        print("Invalid choice!")
        sys.exit(1)
    
    # Phân tích chi tiết
    analyze_results(results)
    
    print("\n✅ Testing complete!")