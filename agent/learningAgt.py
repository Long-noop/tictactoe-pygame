from agent import Agent

class LearningAgent(Agent):
    def get_move(self, state):
        # Dựa vào model học máy đã train
        return model.predict_best_move(state)