from chess_zero.env.chess_env import ChineseChessEnv


def test_env():
    env1 = ChineseChessEnv()
    env2 = env1.copy()

    env1.num_halfmoves = 10

    print(env2.num_halfmoves)

if __name__ == '__main__':
    test_env()