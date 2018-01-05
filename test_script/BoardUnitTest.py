import unittest

from chess_zero.agent.chinese_chess import Board


def replace_chess(fen):
    fen = fen.replace('n', 'h')
    fen = fen.replace('N', 'H')
    fen = fen.replace('b', 'e')
    fen = fen.replace('B', 'E')
    return fen


class BoardUnitTest(unittest.TestCase):
    def test_pawn1(self):
        fen = '9/9/9/9/9/9/P1P1P1P1P/9/9/9 w - - 0 1'
        board = Board(fen)
        corrent_set = {'a3a4', 'c3c4', 'e3e4', 'g3g4', 'i3i4'}
        result_set = set()
        for step in board.generate_legal_moves():
            result_set.add(step.ucci())
        self.assertEqual(corrent_set, result_set)

    def test_fen(self):
        fen = 'r1bakabn1/9/1cn4cr/p1p1p3p/6p2/9/P1P1P1P1P/1C2C1N2/9/RNBAKABR1 w - - 0 4'
        fen = replace_chess(fen)
        board = Board(fen)
        self.assertEqual(fen, board.fen())


if __name__ == '__main__':
    unittest.main()
