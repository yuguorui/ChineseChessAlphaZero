import enum
from logging import getLogger

import numpy as np
import copy
from chess_zero.agent import chinese_chess

logger = getLogger(__name__)

# noinspection PyArgumentList
Winner = enum.Enum("Winner", "black white draw")

pieces_order = 'KAEHRCPkaehrcp'  # 将士相马车炮兵
# castling_order = 'KQkq'
ind = {
    pieces_order[i]: i
    for i in range(len(pieces_order))
}


def maybe_flip_fen(fen, flip=False):
    if not flip:
        return fen
    foo = fen.split(' ')
    rows = foo[0].split('/')

    def swapcase(a):
        if a.isalpha():
            return a.lower() if a.isupper() else a.upper()
        return a

    def swapall(aa):
        return "".join([swapcase(a) for a in aa])

    return (
            "/".join([swapall(row) for row in reversed(rows)])  # 棋子位置数值区域
            + " " + ('w' if foo[1] == 'b' else 'b')  # 轮走棋方
            + " " + "-"  # 吃过路兵目标格
            + " " + foo[3] + " " + foo[4] + " " + foo[5]  # 易位可行性, 半回合计数，回合数
    )


def aux_planes(fen):
    foo = fen.split(' ')

    en_passant = np.zeros((8, 8), dtype=np.float32)

    fifty_move_count = int(foo[4])
    fifty_move = np.full((8, 8), fifty_move_count, dtype=np.float32)

    castling = foo[2]
    auxiliary_planes = [np.full((8, 8), int('K' in castling), dtype=np.float32),
                        np.full((8, 8), int('Q' in castling), dtype=np.float32),
                        np.full((8, 8), int('k' in castling), dtype=np.float32),
                        np.full((8, 8), int('q' in castling), dtype=np.float32),
                        fifty_move,
                        en_passant]

    ret = np.asarray(auxiliary_planes, dtype=np.float32)
    assert ret.shape == (6, 8, 8)
    return ret


# FEN board is like this:
# a8 b8 .. h8
# a7 b7 .. h7
# .. .. .. ..
# a1 b1 .. h1
#
# FEN string is like this:
#  0  1 ..  7
#  8  9 .. 15
# .. .. .. ..
# 56 57 .. 63

# my planes are like this:
# 00 01 .. 07
# 10 11 .. 17
# .. .. .. ..
# 70 71 .. 77
#


def to_planes(fen):
    board_state = replace_tags_board(fen)
    pieces_both = np.zeros(shape=(14, 10, 9), dtype=np.float32)
    for rank in range(10):
        for file in range(9):
            v = board_state[rank * 9 + file]
            if v.isalpha():
                pieces_both[ind[v]][rank][file] = 1
    assert pieces_both.shape == (14, 10, 9)
    return pieces_both


def all_input_planes(fen):
    # 去除辅助平面
    # current_aux_planes = aux_planes(fen)
    # ret = np.vstack((history_both, current_aux_planes))

    history_both = to_planes(fen)
    ret = history_both

    # assert ret.shape == (20, 10, 9)
    return ret


def canon_input_planes(fen):
    fen = maybe_flip_fen(fen, is_black_turn(fen))
    return all_input_planes(fen)


class ChineseChessEnv:

    def __init__(self):
        self.board = None
        self.num_halfmoves = 0
        self.winner = None  # type: Winner
        self.resigned = False
        self.result = None

    def reset(self):
        self.board = chinese_chess.Board()
        self.num_halfmoves = 0
        self.winner = None
        self.resigned = False
        return self

    def update(self, board):
        self.board = chinese_chess.Board(board)
        self.winner = None
        self.resigned = False
        return self

    @property
    def done(self):
        return self.winner is not None

    @property
    def white_won(self):
        return self.winner == Winner.white

    @property
    def white_to_move(self):
        return self.board.turn == chinese_chess.WHITE

    def step(self, action: str, check_over=True):
        """
        :param action:
        :param check_over:
        :return:
        """
        if check_over and action is None:
            self._resign()
            return

        self.board.push_uci(action)

        self.num_halfmoves += 1

        if check_over and self.board.result(claim_draw=True) != "*":
            self._game_over()

    def _game_over(self):
        if self.winner is None:
            self.result = self.board.result(claim_draw=True)
            if self.result == '1-0':
                self.winner = Winner.white
            elif self.result == '0-1':
                self.winner = Winner.black
            else:
                self.winner = Winner.draw

    def _resign(self):
        self.resigned = True
        if self.white_to_move:  # WHITE RESIGNED!
            self.winner = Winner.black
            self.result = "0-1"
        else:
            self.winner = Winner.white
            self.result = "1-0"

    def adjudicate(self):
        score = self.testeval(absolute=True)
        if abs(score) < 0.01:
            self.winner = Winner.draw
            self.result = "1/2-1/2"
        elif score > 0:
            self.winner = Winner.white
            self.result = "1-0"
        else:
            self.winner = Winner.black
            self.result = "0-1"

    def ending_average_game(self):
        self.winner = Winner.draw
        self.result = "1/2-1/2"

    def copy(self):
        env = copy.copy(self)
        env.board = copy.copy(self.board)
        return env

    def render(self):
        print("\n")
        print(self.board)
        print("\n")

    @property
    def observation(self):
        return self.board.fen()

    def deltamove(self, fen_next):
        moves = list(self.board.legal_moves)
        for mov in moves:
            self.board.push(mov)
            fee = self.board.fen()
            self.board.pop()
            if fee == fen_next:
                return mov.uci()
        return None

    def replace_tags(self):
        return replace_tags_board(self.board.fen())

    def canonical_input_planes(self):
        return canon_input_planes(self.board.fen())

    def testeval(self, absolute=False) -> float:
        return testeval(self.board.fen(), absolute)


def testeval(fen, absolute=False) -> float:
    piece_vals = {'K': 3, 'A': 2, 'E': 3.25, 'H': 4, 'R': 5, 'C': 4, 'P': 1}
    ans = 0.0
    tot = 0
    for c in fen.split(' ')[0]:
        if not c.isalpha():
            continue

        if c.isupper():
            ans += piece_vals[c]
            tot += piece_vals[c]
        else:
            ans -= piece_vals[c.upper()]
            tot += piece_vals[c.upper()]
    v = ans / tot
    if not absolute and is_black_turn(fen):
        v = -v
    assert abs(v) < 1
    return np.tanh(v * 3)  # arbitrary


def replace_tags_board(board_san):
    """
    Forsyth?Edwards Notation (FEN) is a standard notation for describing a particular board position of a chess game.
    The purpose of FEN is to provide all the necessary information to restart a game from a particular position.
    :return:
    """
    board_san = board_san.split(" ")[0]
    board_san = board_san.replace("2", "11")
    board_san = board_san.replace("3", "111")
    board_san = board_san.replace("4", "1111")
    board_san = board_san.replace("5", "11111")
    board_san = board_san.replace("6", "111111")
    board_san = board_san.replace("7", "1111111")
    board_san = board_san.replace("8", "11111111")
    board_san = board_san.replace("9", "111111111")

    return board_san.replace("/", "")


def is_black_turn(fen):
    return fen.split(" ")[1] == 'b'
