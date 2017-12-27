import os
import chess

def _project_dir():
    d = os.path.dirname
    return d(d(d(os.path.abspath(__file__))))


def _data_dir():
    return os.path.join(_project_dir(), "data")


def create_uci_labels():
    labels_array = []
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    numbers = ['1', '2', '3', '4', '5', '6', '7', '8']
    promoted_to = ['q', 'r', 'b', 'n']

    for l1 in range(8):
        for n1 in range(8):
            destinations = [(t, n1) for t in range(0, 8)] + \
                           [(l1, t) for t in range(0, 8)] + \
                           [(l1 + t, n1 + t) for t in range(-7, 8)] + \
                           [(l1 + t, n1 - t) for t in range(-7, 8)] + \
                           [(l1 + a, n1 + b) for (a, b) in [(-2, -1), (-1, -2), (-2, 1), (1, -2), (2, -1), (-1, 2), (2, 1), (1, 2)]]
            for (l2, n2) in destinations:
                if (l1, n1) != (l2, n2) and l2 in range(0, 8) and n2 in range(0, 8):
                    move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
                    labels_array.append(move)
    for l1 in range(8):
        l = letters[l1]
        for p in promoted_to:
            labels_array.append(l + '2' + l + '1' + p)
            labels_array.append(l + '7' + l + '8' + p)
            if l1 > 0:
                l_l = letters[l1 - 1]
                labels_array.append(l + '2' + l_l + '1' + p)
                labels_array.append(l + '7' + l_l + '8' + p)
            if l1 < 7:
                l_r = letters[l1 + 1]
                labels_array.append(l + '2' + l_r + '1' + p)
                labels_array.append(l + '7' + l_r + '8' + p)
    return labels_array


def create_ucci_labels():
    labels_array = []
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    
    for l1 in range(9):
        for n1 in range(10):
            # 一些通用行走规则 车 马 王 兵/卒 将
            destinations = [(t, n1) for t in range(0, 9)] + \
                           [(l1, t) for t in range(0, 10)] + \
                           [(l1 + a, n1 + b) for (a, b) in
                            [(-2, -1), (-1, -2), (-2, 1), (1, -2), (2, -1), (-1, 2), (2, 1), (1, 2)]]
            for (l2, n2) in destinations:
                if (l1, n1) != (l2, n2) and l2 in range(0, 9) and n2 in range(0, 10):
                    move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
                    labels_array.append(move)
    # 某些棋子走法只会出现在特定点，象/相 士/仕
    elephant_red = [(0, 2), (2, 0), (2, 4), (4, 2), (6, 0), (6, 4), (8, 2)]
    for (l1, n1) in elephant_red:
        destinations = [
            (l1 + a, n1 + b) for (a, b) in [(2, 2), (2, -2), (-2, 2), (-2, -2)]
        ]
        for (l2, n2) in destinations:
            if (l1, n1) != (l2, n2) and l2 in range(0, 9) and n2 in range(0, 5):
                move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
                labels_array.append(move)
    elephant_black = [(0, 7), (2, 5), (2, 9), (4, 7), (6, 5), (6, 9), (8, 7)]
    for (l1, n1) in elephant_black:
        destinations = [
            (l1 + a, n1 + b) for (a, b) in [(2, 2), (2, -2), (-2, 2), (-2, -2)]
        ]
        for (l2, n2) in destinations:
            if (l1, n1) != (l2, n2) and l2 in range(0, 9) and n2 in range(5, 10):
                move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
                labels_array.append(move)
    advisor_red = [(3, 0), (3, 2), (4, 1), (5, 0), (5, 2)]
    for (l1, n1) in advisor_red:
        destinations = [
            (l1 + a, n1 + b) for (a, b) in [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        ]
        for (l2, n2) in destinations:
            if (l1, n1) != (l2, n2) and l2 in range(3, 6) and n2 in range(0, 3):
                move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
                labels_array.append(move)
    advisor_black = [(3, 7), (3, 9), (4, 8), (5, 7), (5, 9)]
    for (l1, n1) in advisor_black:
        destinations = [
            (l1 + a, n1 + b) for (a, b) in [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        ]
        for (l2, n2) in destinations:
            if (l1, n1) != (l2, n2) and l2 in range(3, 6) and n2 in range(7, 10):
                move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
                labels_array.append(move)
    return labels_array


class Config:
    def __init__(self, config_type="mini"):
        self.opts = Options()
        self.resource = ResourceConfig()

        if config_type == "mini":
            import chess_zero.configs.mini as c
        elif config_type == "normal":
            import chess_zero.configs.normal as c
        elif config_type == "distributed":
            import chess_zero.configs.distributed as c
        else:
            raise RuntimeError(f"unknown config_type: {config_type}")
        self.model = c.ModelConfig()
        self.play = c.PlayConfig()
        self.play_data = c.PlayDataConfig()
        self.trainer = c.TrainerConfig()
        self.eval = c.EvaluateConfig()
        self.labels = create_ucci_labels()
        self.n_labels = len(self.labels)


class Options:
    new = False


class ResourceConfig:
    def __init__(self):
        self.project_dir = os.environ.get("PROJECT_DIR", _project_dir())
        self.data_dir = os.environ.get("DATA_DIR", _data_dir())
        self.model_dir = os.environ.get("MODEL_DIR", os.path.join(self.data_dir, "model"))
        self.model_best_config_path = os.path.join(self.model_dir, "model_best_config.json")
        self.model_best_weight_path = os.path.join(self.model_dir, "model_best_weight.h5")

        self.model_best_distributed_ftp_server = "files.000webhost.com"
        self.model_best_distributed_ftp_user = "chess-alpha-zero"
        self.model_best_distributed_ftp_password = "alpha-chess-zero-2"
        self.model_best_distributed_ftp_remote_path = "/public_html"

        self.next_generation_model_dir = os.path.join(self.model_dir, "next_generation")
        self.next_generation_model_dirname_tmpl = "model_%s"
        self.next_generation_model_config_filename = "model_config.json"
        self.next_generation_model_weight_filename = "model_weight.h5"

        self.play_data_dir = os.path.join(self.data_dir, "play_data")
        self.play_data_filename_tmpl = "play_%s.json"

        self.log_dir = os.path.join(self.project_dir, "logs")
        self.main_log_path = os.path.join(self.log_dir, "main.log")

    def create_directories(self):
        dirs = [self.project_dir, self.data_dir, self.model_dir, self.play_data_dir, self.log_dir,
                self.next_generation_model_dir]
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d)


class PlayWithHumanConfig:
    def __init__(self):
        self.simulation_num_per_move = 200
        self.thinking_loop = 5
        self.logging_thinking = True
        self.c_puct = 1
        self.parallel_search_num = 4
        self.noise_eps = 0
        self.change_tau_turn = 0
        self.resign_threshold = None

    def update_play_config(self, pc):
        """

        :param PlayConfig pc:
        :return:
        """
        pc.simulation_num_per_move = self.simulation_num_per_move
        pc.thinking_loop = self.thinking_loop
        pc.logging_thinking = self.logging_thinking
        pc.c_puct = self.c_puct
        pc.noise_eps = self.noise_eps
        pc.change_tau_turn = self.change_tau_turn
        pc.parallel_search_num = self.parallel_search_num
        pc.resign_threshold = self.resign_threshold
