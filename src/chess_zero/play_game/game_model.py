from logging import getLogger

from chess_zero.agent.player_chess import HistoryItem
from chess_zero.agent.player_chess import ChineseChessPlayer
from chess_zero.config import Config
from chess_zero.lib.model_helper import load_best_model_weight
# import chess
from chess_zero.agent.chinese_chess import WHITE, BLACK, Move

logger = getLogger(__name__)


class PlayWithHuman:
    def __init__(self, config: Config):
        self.config = config
        self.human_color = None
        self.observers = []
        self.model = self._load_model()
        self.ai = None  # type: ChineseChessPlayer
        self.last_evaluation = None
        self.last_history = None  # type: HistoryItem

    def start_game(self, human_is_black):
        self.human_color = BLACK if human_is_black else WHITE
        self.ai = ChineseChessPlayer(self.config, self.model)

    def _load_model(self):
        from chess_zero.agent.model_chess import ChessModel
        model = ChessModel(self.config)
        if not load_best_model_weight(model):
            raise RuntimeError("Best model not found!")
        return model

    def move_by_ai(self, env):
        if self.ai is None:
            self.ai = ChineseChessPlayer(self.config, self.model)
        action = self.ai.action(env.observation)

        self.last_history = self.ai.ask_thought_about(env.observation)
        self.last_evaluation = self.last_history.values[self.last_history.action]
        logger.debug(f"Evaluation history by AI = {self.last_history}")
        logger.debug(f"Evaluation by AI = {self.last_evaluation}")

        return action

    def move_by_human(self, env):
        while True:
            try:
                move = input('\nEnter your move in UCCI format (a1a2, b2b6, ...): ')
                if Move.from_ucci(move) in env.board.legal_moves:
                    return move
                else:
                    print("That is NOT a valid move :(.")
            except:
                print("That is NOT a valid move :(.")
