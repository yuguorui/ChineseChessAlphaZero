import os
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from logging import getLogger
from multiprocessing import Manager
from threading import Thread
from time import time

from chess_zero.agent.model_chess import ChessModel
from chess_zero.agent.player_chess import ChineseChessPlayer
from chess_zero.config import Config
from chess_zero.env.chess_env import ChineseChessEnv, Winner
from chess_zero.lib.data_helper import (get_game_data_filenames,  # , pretty_print
                                        write_game_data_to_file)
from chess_zero.lib.logger import setup_module_logger
from chess_zero.lib.model_helper import (load_best_model_weight,
                                         reload_best_model_weight_if_changed,
                                         save_as_best_model)

logger = getLogger(__name__)
setup_module_logger(logger, 'self.log')


def start(config: Config):
    return SelfPlayWorker(config).start()


# noinspection PyAttributeOutsideInit
class SelfPlayWorker:
    def __init__(self, config: Config):
        """
        在这里创建新的工作进程。
        :param config:
        """
        self.config = config
        self.current_model = self.load_model()
        self.m = Manager()
        self.cur_pipes = self.m.list([self.current_model.get_pipes(self.config.play.search_threads) for _ in
                                      range(self.config.play.max_processes)])

    def start(self):
        self.buffer = []

        futures = deque()
        with ProcessPoolExecutor(max_workers=self.config.play.max_processes) as executor:
            for game_idx in range(self.config.play.max_processes):
                futures.append(executor.submit(self_play_buffer, self.config, cur=self.cur_pipes))
            game_idx = 0
            while True:
                start_time = time()
                env, data = futures.popleft().result()
                game_idx += 1
                logger.info(f"game {game_idx:3} time={time() - start_time:5.1f}s "
                      f"halfmoves={env.num_halfmoves:3} {env.winner:12} "
                      f"{'by resign ' if env.resigned else '          '}")


                # pretty_print(env, ("current_model", "current_model"))
                self.buffer += data
                if (game_idx % self.config.play_data.nb_game_in_file) == 0:
                    self.flush_buffer()
                    reload_best_model_weight_if_changed(self.current_model)
                futures.append(executor.submit(self_play_buffer, self.config, cur=self.cur_pipes))  # Keep it going

        # if len(data) > 0:
        #     self.flush_buffer()

    def load_model(self):
        model = ChessModel(self.config)
        if self.config.opts.new or not load_best_model_weight(model):
            model.build()
            save_as_best_model(model)
        return model

    def flush_buffer(self):
        rc = self.config.resource
        game_id = datetime.now().strftime("%Y%m%d-%H%M%S.%f")
        path = os.path.join(rc.play_data_dir, rc.play_data_filename_tmpl % game_id)
        logger.info(f"save play data to {path}")
        thread = Thread(target=write_game_data_to_file, args=(path, self.buffer))
        thread.start()
        self.buffer = []

    def remove_play_data(self):
        files = get_game_data_filenames(self.config.resource)
        if len(files) < self.config.play_data.max_file_num:
            return
        for i in range(len(files) - self.config.play_data.max_file_num):
            os.remove(files[i])


def self_play_buffer(config, cur) -> (ChineseChessPlayer, list):
    pipes = cur.pop()  # borrow
    env = ChineseChessEnv().reset()

    white = ChineseChessPlayer(config, pipes=pipes)
    black = ChineseChessPlayer(config, pipes=pipes)

    while not env.done:
        if env.white_to_move:
            action = white.action(env)
        else:
            action = black.action(env)
        env.step(action)
        # print(f'Move: {action}')
        logger.debug(f'Move: {action}')
        # print(f'{env.board}')
        # print(f'{env.board.fen()}')
        logger.debug(f'{env.board.fen()}')
        logger.debug('=====================================')
        if env.num_halfmoves >= config.play.max_game_length:
            env.adjudicate()

    if env.winner == Winner.white:
        black_win = -1
    elif env.winner == Winner.black:
        black_win = 1
    else:
        black_win = 0

    black.finish_game(black_win)
    white.finish_game(-black_win)

    data = []
    for i in range(len(white.moves)):
        data.append(white.moves[i])
        if i < len(black.moves):
            data.append(black.moves[i])

    cur.append(pipes)
    return env, data
