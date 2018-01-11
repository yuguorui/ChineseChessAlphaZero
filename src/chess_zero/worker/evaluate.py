import os
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from logging import getLogger
from multiprocessing import Manager
from time import sleep

from chess_zero.agent.model_chess import ChessModel
from chess_zero.agent.player_chess import ChineseChessPlayer
from chess_zero.config import Config
from chess_zero.env.chess_env import ChineseChessEnv, Winner
from chess_zero.lib.data_helper import get_next_generation_model_dirs
from chess_zero.lib.logger import setup_module_logger
from chess_zero.lib.model_helper import (load_best_model_weight,
                                         save_as_best_model)

logger = getLogger(__name__)
setup_module_logger(logger, 'eva.log')


def start(config: Config):
    return EvaluateWorker(config).start()


class EvaluateWorker:
    def __init__(self, config: Config):
        """
        :param config:
        """
        self.config = config
        self.play_config = config.eval.play_config
        self.current_model = self.load_current_model()
        self.m = Manager()
        self.cur_pipes = self.m.list([self.current_model.get_pipes(self.play_config.search_threads) for _ in
                                      range(self.play_config.max_processes)])

    def start(self):
        while True:
            ng_model, model_dir = self.load_next_generation_model()
            logger.info(f"start evaluate model {model_dir}")
            ng_is_great = self.evaluate_model(ng_model)
            if ng_is_great:
                logger.info(f"New Model become best model: {model_dir}")
                save_as_best_model(ng_model)
                self.current_model = ng_model
            self.move_model(model_dir)

    def evaluate_model(self, ng_model):
        ng_pipes = self.m.list(
            [ng_model.get_pipes(self.play_config.search_threads) for _ in range(self.play_config.max_processes)])

        futures = []
        logger.info(f"current worker: {self.play_config.max_processes}")
        with ProcessPoolExecutor(max_workers=self.play_config.max_processes) as executor:
            for game_idx in range(self.config.eval.game_num):
                fut = executor.submit(play_game, self.config, cur=self.cur_pipes, ng=ng_pipes,
                                      current_white=(game_idx % 2 == 0))
                futures.append(fut)

            results = []
            for fut in as_completed(futures):
                # ng_score := if ng_model win -> 1, lose -> 0, draw -> 0.5
                ng_score, env, current_white = fut.result()
                results.append(ng_score)
                win_rate = sum(results) / len(results)
                game_idx = len(results)
                logger.info(f"game {game_idx:3}: ng_score={ng_score:.1f} as {'black' if current_white else 'white'} "
                             f"{'by resign ' if env.resigned else '          '}"
                             f"win_rate={win_rate*100:5.1f}% "
                             f"{env.board.fen().split(' ')[0]}")

                colors = ("current_model", "ng_model")
                if not current_white:
                    colors = reversed(colors)
                # pretty_print(env, colors)
                print(env, colors)

                if len(results) - sum(results) >= self.config.eval.game_num * (1 - self.config.eval.replace_rate):
                    logger.info(f"lose count reach {results.count(0)} so give up challenge")
                    # executor.shutdown(False)
                    return False
                if sum(results) >= self.config.eval.game_num * self.config.eval.replace_rate:
                    logger.info(f"win count reach {results.count(1)} so change best model")
                    # executor.shutdown(False)
                    return True

        win_rate = sum(results) / len(results)
        logger.info(f"winning rate {win_rate*100:.1f}%")
        return win_rate >= self.config.eval.replace_rate

    def move_model(self, model_dir):
        rc = self.config.resource
        new_dir = os.path.join(rc.model_dir, "copies", os.path.basename(model_dir))
        # os.rename(model_dir, new_dir)
        shutil.move(model_dir, new_dir)

    def load_current_model(self):
        model = ChessModel(self.config)
        load_best_model_weight(model)
        return model

    def load_next_generation_model(self):
        rc = self.config.resource
        while True:
            dirs = get_next_generation_model_dirs(self.config.resource)
            if dirs:
                break
            logger.info("There is no next generation model to evaluate")
            sleep(60)
        model_dir = dirs[-1] if self.config.eval.evaluate_latest_first else dirs[0]
        config_path = os.path.join(model_dir, rc.next_generation_model_config_filename)
        weight_path = os.path.join(model_dir, rc.next_generation_model_weight_filename)
        model = ChessModel(self.config)
        model.load(config_path, weight_path)
        return model, model_dir


def play_game(config, cur, ng, current_white: bool) -> (float, ChineseChessEnv, bool):
    cur_pipes = cur.pop()
    ng_pipes = ng.pop()
    env = ChineseChessEnv().reset()

    current_player = ChineseChessPlayer(config, pipes=cur_pipes, play_config=config.eval.play_config)
    ng_player = ChineseChessPlayer(config, pipes=ng_pipes, play_config=config.eval.play_config)
    if current_white:
        white, black = current_player, ng_player
    else:
        white, black = ng_player, current_player

    while not env.done:
        if env.white_to_move:
            action = white.action(env)
        else:
            action = black.action(env)
        env.step(action)
        logger.debug(action)
        logger.debug(env.board.fen())
        if env.num_halfmoves >= config.eval.max_game_length:
            env.adjudicate()

    if env.winner == Winner.draw:
        ng_score = 0.5
    elif env.white_won == current_white:
        ng_score = 0
    else:
        ng_score = 1
    cur.append(cur_pipes)
    ng.append(ng_pipes)
    return ng_score, env, current_white
