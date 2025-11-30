from agent import Agent
import random

class RandomAgent(Agent):
    def get_move(self, game_array):
        # Get all legal moves
        legal_moves = []
        for i in range(len(game_array)):
            for j in range(len(game_array[i])):
                if game_array[i][j][3]:  # If can_play is True
                    legal_moves.append((i, j))
        
        if legal_moves:
            return random.choice(legal_moves)
        return None