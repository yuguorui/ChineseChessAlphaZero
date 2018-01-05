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
        """
        测试未过河小兵的行为。
        :return:
        """
        fen = '9/9/9/9/9/9/P1P1P1P1P/9/9/9 w - - 0 1'
        board = Board(fen)
        correct_set = {'a3a4', 'c3c4', 'e3e4', 'g3g4', 'i3i4'}
        result_set = set()
        for step in board.generate_legal_moves():
            result_set.add(step.ucci())
        self.assertEqual(correct_set, result_set)

    def test_pawn2(self):
        """
        测试红方过河小兵的行为。
        :return:
        """
        fen = '9/9/9/9/3rP4/9/P1P3P1P/9/9/9 w - - 0 1'
        board = Board(fen)
        correct_set = {'a3a4', 'c3c4', 'e5d5', 'e5f5', 'e5e6', 'g3g4', 'i3i4'}
        result_set = set()
        for step in board.generate_legal_moves():
            result_set.add(step.ucci())
        self.assertEqual(correct_set, result_set)

    def test_pawn3(self):
        """
        测试黑方过河小兵的行为。
        :return:
        """
        fen = '9/9/9/p1p3p1p/9/4pR3/9/9/9/9 b - - 0 1'
        board = Board(fen)
        correct_set = {'a6a5', 'c6c5', 'e4d4', 'e4f4', 'e4e3', 'g6g5', 'i6i5'}
        result_set = set()
        for step in board.generate_legal_moves():
            result_set.add(step.ucci())
        self.assertEqual(correct_set, result_set)

    def test_fen(self):
        """
        测试FEN字符串的设置是否存在问题。
        :return:
        """
        fen = 'r1bakabn1/9/1cn4cr/p1p1p3p/6p2/9/P1P1P1P1P/1C2C1N2/9/RNBAKABR1 w - - 0 4'
        fen = replace_chess(fen)
        board = Board(fen)
        self.assertEqual(fen, board.fen())


if __name__ == '__main__':
    unittest.main()
