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

    def test_cannon(self):
        fen = '9/9/4P4/9/4P4/9/p1R1C4/9/4N4/9 w - - 0 1'
        fen = replace_chess(fen)
        board = Board(fen)
        correct_set = {'c3c9', 'c3c8', 'c3c7', 'c3c6', 'c3c5', 'c3c4', 'c3c2',
                       'c3c1', 'c3c0', 'c3d3', 'c3b3', 'c3a3', 'e1f3', 'e1d3',
                       'e1g2', 'e1c2', 'e1g0', 'e1c0', 'e3e4', 'e3e2', 'e3d3',
                       'e3f3', 'e3g3', 'e3h3', 'e3i3', 'e3a3', 'e7e8', 'e7f7',
                       'e7d7', 'e5e6', 'e5f5', 'e5d5', 'e7e8'}
        result_set = set()
        for step in board.generate_legal_moves():
            result_set.add(step.ucci())
            # print(step)
        self.assertEqual(correct_set, result_set)

        def test_cannon2(self):
            fen = '9/9/9/9/9/9/p1R1C4/9/4N4/9 w - - 0 1'
            fen = replace_chess(fen)
            board = Board(fen)
            correct_set = {'e3e2', 'e3e4', 'e3e5', 'e3e6', 'e3e7', 'e3e8', 'e3e9',
                           'e3f3', 'e3g3', 'e3h3', 'e3i3', 'e3d3', 'e3a3', 'e1c2',
                           'e1c0', 'e1d3', 'e1f3', 'e1g2', 'e1g0', 'c3c0', 'c3c1',
                           'c3c2', 'c3c4', 'c3c5', 'c3c6', 'c3c7', 'c3c8', 'c3c9',
                           'c3a3', 'c3b3', 'c3d3', 'a3a2', 'a3b3',}
            result_set = set()
            for step in board.generate_legal_moves():
                result_set.add(step.ucci())
            self.assertEqual(correct_set, result_set)



if __name__ == '__main__':
    unittest.main()
