#
# This is a model simplify and modify the python-chess api
# so that it can operate chinese chess
#
import copy
import logging

logger = logging.getLogger(__name__)
logger.level = logging.DEBUG

COLORS = [WHITE, BLACK] = [True, False]
COLOR_NAMES = ["black", "white"]

PIECE_TYPES = [PAWN, HORSE, ELEPHANT, ROOK,
               ADVISOR, KING, CANNON] = list(range(1, 8))
PIECE_SYMBOLS = ["", "p", "h", "e", "r", "a", "k", "c"]
PIECE_NAMES = ["", "pawn", "horse", "elephant",
               "rook", "advisor", "king", "cannon"]

UNICODE_PIECE_SYMBOLS = {
    "K": u"帅", "k": u"将",
    "A": u"仕", "a": u"士",
    "E": u"相", "e": u"象",
    "H": u"马", "h": u"马",
    "R": u"车", "r": u"车",
    "C": u"炮", "c": u"炮",
    "P": u"兵", "p": u"卒"
}

FILE_NAMES = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]

RANK_NAMES = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

STARTING_FEN = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR w - - 0 1"
"""The FEN for the standard chess starting position."""

STARTING_BOARD_FEN = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR"
"""The board part of the FEN for the standard chess starting position."""

SQUARES = [
    A0, B0, C0, D0, E0, F0, G0, H0, I0,
    A1, B1, C1, D1, E1, F1, G1, H1, I1,
    A2, B2, C2, D2, E2, F2, G2, H2, I2,
    A3, B3, C3, D3, E3, F3, G3, H3, I3,
    A4, B4, C4, D4, E4, F4, G4, H4, I4,
    A5, B5, C5, D5, E5, F5, G5, H5, I5,
    A6, B6, C6, D6, E6, F6, G6, H6, I6,
    A7, B7, C7, D7, E7, F7, G7, H7, I7,
    A8, B8, C8, D8, E8, F8, G8, H8, I8,
    A9, B9, C9, D9, E9, F9, G9, H9, I9] = range(90)


def get_square(r, c):
    return SQUARES[r * 9 + c]


def square_col(square):
    """Gets the column index of the square where ``0`` is the a column."""
    return square % 9


def square_row(square):
    """Gets the row index of the square where ``0`` is the first row."""
    return square // 9


def square_name(square):
    """Gets the name of the square, like ``a3``."""
    return FILE_NAMES[square_col(square)] + RANK_NAMES[square_row(square)]


def square_distance(a, b):
    """
    Gets the distance (i.e., the number of king steps) from square *a* to *b*.
    """
    return max(abs(square_col(a) - square_col(b)), abs(square_row(a) - square_row(b)))


def square_mirror(square):
    """Mirrors the square vertically."""
    return (9 - square // 9) * 9 + square % 9


SQUARES_180 = [square_mirror(sq) for sq in SQUARES]
SQUARE_NAMES = [square_name(sq) for sq in SQUARES]

BB_VOID = 0
BB_ALL = int('1' * 90, 2)  # 90 bit
BB_SQUARES = [
    BB_A0, BB_B0, BB_C0, BB_D0, BB_E0, BB_F0, BB_G0, BB_H0, BB_I0,
    BB_A1, BB_B1, BB_C1, BB_D1, BB_E1, BB_F1, BB_G1, BB_H1, BB_I1,
    BB_A2, BB_B2, BB_C2, BB_D2, BB_E2, BB_F2, BB_G2, BB_H2, BB_I2,
    BB_A3, BB_B3, BB_C3, BB_D3, BB_E3, BB_F3, BB_G3, BB_H3, BB_I3,
    BB_A4, BB_B4, BB_C4, BB_D4, BB_E4, BB_F4, BB_G4, BB_H4, BB_I4,
    BB_A5, BB_B5, BB_C5, BB_D5, BB_E5, BB_F5, BB_G5, BB_H5, BB_I5,
    BB_A6, BB_B6, BB_C6, BB_D6, BB_E6, BB_F6, BB_G6, BB_H6, BB_I6,
    BB_A7, BB_B7, BB_C7, BB_D7, BB_E7, BB_F7, BB_G7, BB_H7, BB_I7,
    BB_A8, BB_B8, BB_C8, BB_D8, BB_E8, BB_F8, BB_G8, BB_H8, BB_I8,
    BB_A9, BB_B9, BB_C9, BB_D9, BB_E9, BB_F9, BB_G9, BB_H9, BB_I9
] = [1 << sq for sq in SQUARES]

BB_CORNERS = BB_A0 | BB_I0 | BB_A9 | BB_I9


def msb(bb):
    return bb.bit_length() - 1


def scan_reversed(bb, _BB_SQUARES=BB_SQUARES):
    while bb:
        r = bb.bit_length() - 1
        yield r
        bb ^= _BB_SQUARES[r]


def _default_limit(square):
    return 0 <= square < 90


def _king_white_limit(square):
    """
    黑方田字格限制
    :param square:
    :return:
    """
    return square in [3, 4, 5, 12, 13, 14, 21, 22, 23]


def _king_black_limit(square):
    """
    白方田字格限制
    :param square:
    :return:
    """
    return square in [66, 67, 68, 75, 76, 77, 84, 85, 86]


def _pawn_white_limit(square):
    if 0 <= square < 45:
        return square in [27, 29, 31, 33, 35, 36, 38, 40, 42, 44]
    else:
        return 0 <= square < 90


def _pawn_black_limit(square):
    if 45 <= square < 90:
        return square in [45, 47, 49, 51, 53, 54, 56, 58, 60, 62]
    else:
        return 0 <= square < 90


def _elephant_white_limit(square):
    return square in [2, 6, 18, 22, 26, 38, 42]


def _elephant_black_limit(square):
    return square in [47, 51, 63, 67, 71, 83, 87]


def _advisor_white_limit(square):
    return square in [3, 5, 13, 21, 23]


def _advisor_black_limit(square):
    return square in [66, 68, 76, 84, 86]


def _sliding_attacks(square, occupied, deltas, limit=_default_limit):
    """
    计算棋子的攻击范围
    :param square:
    :param occupied:
    :param deltas:
    :param limit:
    :return:
    """
    attacks = 0
    for delta in deltas:
        sq = square
        while True:
            sq += delta
            if not limit(sq) or square_distance(sq, sq - delta) > 2:
                break
            attacks |= BB_SQUARES[sq]
            if occupied & BB_SQUARES[sq]:
                break
    return attacks


# BB_HORSE_ATTACKS = [
#     _sliding_attacks(
#         sq, BB_ALL, [19, 17, 11, 7, -19, -17, -11, -7])
#     for sq in SQUARES
# ]

"""
  1
0-h-2
  3
"""
HORSE_INCREMENT = [(7, -11), (17, 19), (-7, 11), (-19, -17)]
BB_HORSE_ATTACKS = []
for sq in SQUARES:
    outer_list = []
    for s in range(15, -1, -1):
        inner = 0
        for i in scan_reversed(s):
            t = _sliding_attacks(sq, BB_ALL, HORSE_INCREMENT[i])
            inner |= t
        outer_list.append(inner)
    BB_HORSE_ATTACKS.append(outer_list)

BB_KING_ATTACKS = [
    _sliding_attacks(
        sq, BB_ALL, [9, 1, -9, -1],
        lambda x: _king_white_limit(x) or _king_black_limit(x)) for sq in SQUARES
]

# BB_ELEPHANT_ATTACKS = [
#     _sliding_attacks(
#         sq, BB_ALL, [20, 16, -20, -16],
#         lambda x: _elephant_white_limit(x) or _elephant_black_limit(x)) for sq in SQUARES
# ]

"""
0---1
|-E-|
2---3
"""
ELEPHANT_INCREMENT = [(16,), (20,), (-20,), (-16,)]
BB_ELEPHANT_ATTACKS = []

def _elephant_limit(x):
    if 0 <= x < 45:
        return _elephant_white_limit(x)
    else:
        return _elephant_black_limit(x)

for sq in SQUARES:
    outer_list = []
    for s in range(15, -1, -1):
        inner = 0
        for i in scan_reversed(s):
            t = _sliding_attacks(sq, BB_ALL, ELEPHANT_INCREMENT[i], _elephant_limit)
            inner |= t
        outer_list.append(inner)
    BB_ELEPHANT_ATTACKS.append(outer_list)

BB_ADVISOR_ATTACKS = [
    _sliding_attacks(
        sq, BB_ALL, [10, 8, -10, -8],
        lambda x: _advisor_white_limit(x) or _advisor_black_limit(x)) for sq in SQUARES
]

BB_PAWN_ATTACKS = [
    [_sliding_attacks(
        sq, BB_ALL, [-1, 1, -9],
        _pawn_black_limit) for sq in SQUARES],
    [_sliding_attacks(
        sq, BB_ALL, [-1, 1, 9],
        _pawn_white_limit) for sq in SQUARES]
]

BB_COL = [
    BB_COL_A,
    BB_COL_B,
    BB_COL_C,
    BB_COL_D,
    BB_COL_E,
    BB_COL_F,
    BB_COL_G,
    BB_COL_H,
    BB_COL_I
] = [0x201008040201008040201 << i for i in range(9)]

BB_ROW = [
    BB_ROW_0,
    BB_ROW_1,
    BB_ROW_2,
    BB_ROW_3,
    BB_ROW_4,
    BB_ROW_5,
    BB_ROW_6,
    BB_ROW_7,
    BB_ROW_8,
    BB_ROW_9
] = [0x1ff << (9 * i) for i in range(10)]


def _edges(square):
    return (((BB_ROW_0 | BB_ROW_9) & ~BB_ROW[square_row(square)]) |
            ((BB_COL_A | BB_COL_I) & ~BB_COL[square_col(square)]))


def _carry_rippler(mask):
    """
    如下文的注释，返回mask的子集
    :param mask:
    :return:
    """
    # Carry-Rippler trick to iterate subsets of mask.
    subset = 0
    while True:
        yield subset
        subset = (subset - mask) & mask
        if not subset:
            break


def _attack_table(deltas):
    mask_table = []
    attack_table = []

    for square in SQUARES:
        attacks = {}

        mask = _sliding_attacks(square, BB_VOID, deltas) & ~_edges(square)
        for subset in _carry_rippler(mask):
            attacks[subset] = _sliding_attacks(square, subset, deltas)

        attack_table.append(attacks)
        mask_table.append(mask)

    return mask_table, attack_table


BB_DIAG_MASKS, BB_DIAG_ATTACKS = _attack_table([-10, -8, 8, 10])
BB_FILE_MASKS, BB_FILE_ATTACKS = _attack_table([-9, 9])
BB_RANK_MASKS, BB_RANK_ATTACKS = _attack_table([-1, 1])


def _rays():
    rays = []
    between = []
    for a, bb_a in enumerate(BB_SQUARES):
        rays_row = []
        between_row = []
        for b, bb_b in enumerate(BB_SQUARES):
            if BB_DIAG_ATTACKS[a][0] & bb_b:
                # rays_row.append(
                #     (BB_DIAG_ATTACKS[a][0] & BB_DIAG_ATTACKS[b][0]) | bb_a | bb_b)
                # between_row.append(
                #     BB_DIAG_ATTACKS[a][BB_DIAG_MASKS[a] & bb_b] & BB_DIAG_ATTACKS[b][BB_DIAG_MASKS[b] & bb_a])
                """
                BB_RANK_ATTACKS的第一个参数代表起始棋子，第二个参数代表棋子的遮挡情况
                下可行的行攻击方法，详情见上面的attack_table函数。
                """
            elif BB_RANK_ATTACKS[a][0] & bb_b:
                rays_row.append(BB_RANK_ATTACKS[a][0] | bb_a)
                between_row.append(
                    BB_RANK_ATTACKS[a][BB_RANK_MASKS[a] & bb_b] &
                    BB_RANK_ATTACKS[b][BB_RANK_MASKS[b] & bb_a])
            elif BB_FILE_ATTACKS[a][0] & bb_b:
                rays_row.append(BB_FILE_ATTACKS[a][0] | bb_a)
                between_row.append(
                    BB_FILE_ATTACKS[a][BB_FILE_MASKS[a] & bb_b] &
                    BB_FILE_ATTACKS[b][BB_FILE_MASKS[b] & bb_a])
            else:
                rays_row.append(0)
                between_row.append(0)
        rays.append(rays_row)
        between.append(between_row)
    return rays, between


BB_RAYS, BB_BETWEEN = _rays()


class Piece(object):
    """A piece with type and color."""

    def __init__(self, piece_type, color):
        self.piece_type = piece_type
        self.color = color

    def symbol(self):
        """
        Gets the symbol ``P``, ``H``, ``E``, ``R``, ``A``, ``C`` or ``K`` for white
        pieces or the lower-case variants for the black pieces.
        """
        if self.color == WHITE:
            return PIECE_SYMBOLS[self.piece_type].upper()
        else:
            return PIECE_SYMBOLS[self.piece_type]

    @classmethod
    def from_symbol(cls, symbol):
        """
        Creates a :class:`~chess.Piece` instance from a piece symbol.

        :raises: :exc:`ValueError` if the symbol is invalid.
        """
        if symbol.islower():
            return cls(PIECE_SYMBOLS.index(symbol), BLACK)
        else:
            return cls(PIECE_SYMBOLS.index(symbol.lower()), WHITE)

    def __hash__(self):
        return hash(self.piece_type * (self.color + 1))

    def __eq__(self, other):
        ne = self.__ne__(other)
        return NotImplemented if ne is NotImplemented else not ne

    def __ne__(self, other):
        try:
            if self.piece_type != other.piece_type:
                return True
            elif self.color != other.color:
                return True
            else:
                return False
        except AttributeError:
            return NotImplemented


class Move(object):
    """
    Represents a move from a square to a square and possibly the promotion
    piece type.

    Drops and null moves are supported.
    """

    def __init__(self, from_square, to_square, promotion=None, drop=None):
        self.from_square = from_square
        self.to_square = to_square
        self.promotion = promotion
        self.drop = drop

    @classmethod
    def from_ucci(cls, ucci):
        """
        Parses an UCCI(simple ICCS) string.

        :raises: :exc:`ValueError` if the UCCI string is invalid.
        """
        if ucci == "0000":
            return cls.null()
        elif len(ucci) == 4:
            return cls(SQUARE_NAMES.index(ucci[0:2]), SQUARE_NAMES.index(ucci[2:4]))
        else:
            raise ValueError(
                "expected uci string to be of length 4 or 5: {0}".format(repr(ucci)))

    def ucci(self):
        return square_name(self.from_square) + square_name(self.to_square)

    @classmethod
    def null(cls):
        """
        Gets a null move.

        A null move just passes the turn to the other side (and possibly
        forfeits en passant capturing). Null moves evaluate to ``False`` in
        boolean contexts.

        False
        """
        return cls(0, 0)

    def __str__(self):
        if self.from_square == 0 and self.to_square == 0:
            return 'NULL'
        else:
            return f'{square_name(self.from_square)} -> {square_name(self.to_square)}'.upper()

    def __eq__(self, other):
        ne = self.__ne__(other)
        return NotImplemented if ne is NotImplemented else not ne

    def __ne__(self, other):
        try:
            if self.from_square != other.from_square:
                return True
            elif self.to_square != other.to_square:
                return True
            elif self.promotion != other.promotion:
                return True
            elif self.drop != other.drop:
                return True
            else:
                return False
        except AttributeError:
            return NotImplemented

    def __hash__(self):
        return hash((self.to_square, self.from_square, self.promotion, self.drop))

    def __copy__(self):
        return type(self)(self.from_square, self.to_square, self.promotion, self.drop)

    def __deepcopy__(self, memo):
        move = self.__copy__()
        memo[id(self)] = move
        return move

    def __bool__(self):
        return bool(self.from_square or self.to_square or self.promotion or self.drop)


class BaseBoard(object):
    """
    A board representing the position of chess pieces. See
    :class:`~chess.Board` for a full board with move generation.

    The board is initialized with the standard chess starting position, unless
    otherwise specified in the optional *board_fen* argument. If *board_fen*
    is ``None``, an empty board is created.
    """

    def __init__(self, board_fen=STARTING_BOARD_FEN):
        self.occupied_co = [BB_VOID, BB_VOID]

        if board_fen is None:
            self._clear_board()
        elif board_fen == STARTING_BOARD_FEN:
            self._reset_board()
        else:
            self._set_board_fen(board_fen)

    def _reset_board(self):
        self.pawns = (BB_A3 | BB_C3 | BB_E3 | BB_G3 | BB_I3 |
                      BB_A6 | BB_C6 | BB_E6 | BB_G6 | BB_I6)
        self.horses = BB_B0 | BB_H0 | BB_B9 | BB_H9
        self.elephants = BB_C0 | BB_G0 | BB_C9 | BB_G9
        self.rooks = BB_CORNERS
        self.advisers = BB_D0 | BB_F0 | BB_D9 | BB_F9
        self.kings = BB_E0 | BB_E9
        self.cannons = BB_B2 | BB_H2 | BB_B7 | BB_H7

        self.promoted = BB_VOID

        self.occupied_co[WHITE] = BB_ROW_0 | BB_B2 | BB_H2 | BB_A3 | BB_C3 | BB_E3 | BB_G3 | BB_I3
        self.occupied_co[BLACK] = BB_ROW_9 | BB_B7 | BB_H7 | BB_A6 | BB_C6 | BB_E6 | BB_G6 | BB_I6
        self.occupied = self.occupied_co[WHITE] | self.occupied_co[BLACK]

    def reset_board(self):
        self._set_board_fen(STARTING_BOARD_FEN)

    def _clear_board(self):
        self.pawns = BB_VOID
        self.horses = BB_VOID
        self.elephants = BB_VOID
        self.rooks = BB_VOID
        self.advisers = BB_VOID
        self.kings = BB_VOID
        self.cannons = BB_VOID

        self.promoted = BB_VOID

        self.occupied_co[WHITE] = BB_VOID
        self.occupied_co[BLACK] = BB_VOID
        self.occupied = BB_VOID

    def clear_board(self):
        """Clears the board."""
        self._clear_board()

    def piece_at(self, square):
        """Gets the :class:`piece <chess.Piece>` at the given square."""
        piece_type = self.piece_type_at(square)
        if piece_type:
            mask = BB_SQUARES[square]
            color = bool(self.occupied_co[WHITE] & mask)
            return Piece(piece_type, color)

    def piece_type_at(self, square):
        """Gets the piece type without type at the given square."""
        mask = BB_SQUARES[square]

        if not self.occupied & mask:
            return None
        elif self.pawns & mask:
            return PAWN
        elif self.horses & mask:
            return HORSE
        elif self.elephants & mask:
            return ELEPHANT
        elif self.rooks & mask:
            return ROOK
        elif self.advisers & mask:
            return ADVISOR
        elif self.kings & mask:
            return KING
        elif self.cannons & mask:
            return CANNON

    def board_fen(self):
        """
        Gets the board FEN.
        """
        builder = []
        empty = 0

        for square in SQUARES_180:
            piece = self.piece_at(square)

            if not piece:
                empty += 1
            else:
                if empty:
                    builder.append(str(empty))
                    empty = 0
                builder.append(piece.symbol())

            if BB_SQUARES[square] & BB_COL_I:
                if empty:
                    builder.append(str(empty))
                    empty = 0

                if square != I0:
                    builder.append("/")

        return "".join(builder)

    def _remove_piece_at(self, square):
        piece_type = self.piece_type_at(square)
        mask = BB_SQUARES[square]

        if piece_type == PAWN:
            self.pawns ^= mask
        elif piece_type == HORSE:
            self.horses ^= mask
        elif piece_type == ELEPHANT:
            self.elephants ^= mask
        elif piece_type == ROOK:
            self.rooks ^= mask
        elif piece_type == ADVISOR:
            self.advisers ^= mask
        elif piece_type == KING:
            self.kings ^= mask
        elif piece_type == CANNON:
            self.cannons ^= mask
        else:
            return

        self.occupied ^= mask
        self.occupied_co[WHITE] &= ~mask
        self.occupied_co[BLACK] &= ~mask

        self.promoted &= ~mask

        return piece_type

    def _set_piece_at(self, square, piece_type, color, promoted=False):
        self._remove_piece_at(square)

        mask = BB_SQUARES[square]

        if piece_type == PAWN:
            self.pawns |= mask
        elif piece_type == HORSE:
            self.horses |= mask
        elif piece_type == ELEPHANT:
            self.elephants |= mask
        elif piece_type == ROOK:
            self.rooks |= mask
        elif piece_type == ADVISOR:
            self.advisers |= mask
        elif piece_type == KING:
            self.kings |= mask
        elif piece_type == CANNON:
            self.cannons |= mask

        self.occupied ^= mask
        self.occupied_co[color] ^= mask

        if promoted:
            self.promoted ^= mask

    def _set_board_fen(self, fen):
        # Ensure the FEN is valid.
        rows = fen.split("/")
        if len(rows) != 10:
            raise ValueError(
                "expected 10 rows in position part of fen: {0}".format(repr(fen)))

        # Validate each row.
        for row in rows:
            field_sum = 0
            previous_was_digit = False

            for c in row:
                if c in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    if previous_was_digit:
                        raise ValueError(
                            "two subsequent digits in position part of fen: {0}".format(repr(fen)))
                    field_sum += int(c)
                    previous_was_digit = True
                elif c.lower() in ["p", "h", "e", "r", "c", "k", "a"]:
                    field_sum += 1
                    previous_was_digit = False
                else:
                    raise ValueError(
                        "invalid character in position part of fen: {0}".format(repr(fen)))

            if field_sum != 9:
                raise ValueError(
                    "expected 9 columns per row in position part of fen: {0}".format(repr(fen)))

        # Clear the board.
        self._clear_board()

        # Put pieces on the board.
        square_index = 0
        for c in fen:
            if c in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                square_index += int(c)
            elif c.lower() in ["p", "h", "e", "r", "a", "k", "c"]:
                piece = Piece.from_symbol(c)
                self._set_piece_at(
                    SQUARES_180[square_index], piece.piece_type, piece.color)
                square_index += 1

    def king(self, color):
        """
        Finds the king square of the given side. Returns ``None`` if there
        is no king of that color.

        In variants with king promotions, only non-promoted kings are
        considered.
        """
        king_mask = self.occupied_co[color] & self.kings
        if king_mask:
            return msb(king_mask)

    def copy(self):
        """Creates a copy of the board."""
        board = type(self)(None)

        board.pawns = self.pawns
        board.horses = self.horses
        board.elephants = self.elephants
        board.rooks = self.rooks
        board.advisers = self.advisers
        board.kings = self.kings
        board.cannons = self.cannons

        board.occupied_co[WHITE] = self.occupied_co[WHITE]
        board.occupied_co[BLACK] = self.occupied_co[BLACK]
        board.occupied = self.occupied

        return board

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        board = self.copy()
        memo[id(self)] = board
        return board


class Board(BaseBoard):
    """
    A :class:`~chess.BaseBoard` and additional information representing
    a chess position.

    Provides move generation, validation, parsing, attack generation,
    game end detection, move counters and the capability to make and unmake
    moves.

    The board is initialized to the standard chess starting position,
    unless otherwise specified in the optional *fen* argument.
    If *fen* is ``None``, an empty board is created.

    Optionally supports *chess960*. In Chess960 castling moves are encoded
    by a king move to the corresponding rook square.
    Use :func:`chess.Board.from_chess960_pos()` to create a board with one
    of the Chess960 starting positions.

    It's safe to set :data:`~Board.turn`, :data:`~Board.castling_rights`,
    :data:`~Board.ep_square`, :data:`~Board.halfmove_clock` and
    :data:`~Board.fullmove_number` directly.
    """
    ucci_variant = "chinese chess"
    starting_fen = STARTING_FEN

    def __init__(self, fen=STARTING_FEN, chess960=False):

        # noinspection PyTypeChecker
        BaseBoard.__init__(self, None)

        self.chess960 = chess960

        self.pseudo_legal_moves = PseudoLegalMoveGenerator(self)
        self.legal_moves = LegalMoveGenerator(self)

        self.move_stack = []
        self.stack = []

        if fen is None:
            self.clear()
        elif fen == type(self).starting_fen:
            self.reset()
        else:
            self.set_fen(fen)

    def copy(self, stack=True):
        board = super(Board, self).copy()

        board.chess960 = self.chess960

        board.turn = self.turn
        board.fullmove_number = self.fullmove_number
        board.halfmove_clock = self.halfmove_clock

        if stack:
            board.move_stack = copy.deepcopy(self.move_stack)
            board.stack = copy.copy(self.stack)

        return board

    def reset(self):
        """Restores the starting position."""
        self.turn = WHITE
        self.halfmove_clock = 0
        self.fullmove_number = 1

        self.reset_board()

    def reset_board(self):
        super(Board, self).reset_board()
        self.clear_stack()

    def clear(self):
        """
        Clears the board.

        Resets move stacks and move counters. The side to move is white. There
        are no rooks or kings, so castling rights are removed.

        In order to be in a valid :func:`~chess.Board.status()` at least kings
        need to be put on the board.
        """
        self.turn = WHITE
        self.halfmove_clock = 0
        self.fullmove_number = 1

        self.clear_board()

    def clear_board(self):
        super(Board, self).clear_board()
        self.clear_stack()

    def clear_stack(self):
        """Clears the move stack."""
        del self.move_stack[:]
        del self.stack[:]

    def fen(self, shredder=False, en_passant="legal", promoted=None):
        """
        Gets a FEN representation of the position.

        A FEN string (e.g.,
        ``rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1``) consists
        of the position part :func:`~chess.Board.board_fen()`, the
        :data:`~chess.Board.turn`, the castling part
        (:data:`~chess.Board.castling_rights`),
        the en passant square (:data:`~chess.Board.ep_square`),
        the :data:`~chess.Board.halfmove_clock`
        and the :data:`~chess.Board.fullmove_number`.
        """
        return " ".join([
            self.epd(shredder=shredder, en_passant=en_passant,
                     promoted=promoted),
            str(self.halfmove_clock),
            str(self.fullmove_number)
        ])

    def epd(self, shredder=False, en_passant="legal", promoted=None, **operations):
        """
        Gets an EPD representation of the current position.

        See :func:`~chess.Board.fen()` for FEN formatting options (*shredder*,
        *ep_square* and *promoted*).

        EPD operations can be given as keyword arguments. Supported operands
        are strings, integers, floats, moves, lists of moves and ``None``.
        All other operands are converted to strings.

        A list of moves for *pv* will be interpreted as a variation. All other
        move lists are interpreted as a set of moves in the current position.

        *hmvc* and *fmvc* are not included by default. You can use:

        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - hmvc 0; fmvc 1;'
        """
        epd = []

        epd.append(self.board_fen())
        epd.append("w" if self.turn == WHITE else "b")
        epd.append("-")
        epd.append("-")

        return " ".join(epd)

    def set_fen(self, fen):
        """
        Parses a FEN and sets the position from it.

        :raises: :exc:`ValueError` if the FEN string is invalid.
        """
        # Ensure there are six parts.
        parts = fen.split()
        if len(parts) != 6:
            raise ValueError(
                "fen string should consist of 6 parts: {0}".format(repr(fen)))

        # Check that the turn part is valid.
        if not parts[1] in ["w", "b"]:
            raise ValueError(
                "expected 'w' or 'b' for turn part of fen: {0}".format(repr(fen)))

        # Check that the half-move part is valid.
        if int(parts[4]) < 0:
            raise ValueError(
                "half-move clock can not be negative: {0}".format(repr(fen)))

        # Check that the full-move number part is valid.
        # 0 is allowed for compability, but later replaced with 1.
        if int(parts[5]) < 0:
            raise ValueError(
                "full-move number must be positive: {0}".format(repr(fen)))

        # Validate the board part and set it.
        self._set_board_fen(parts[0])

        # Set the turn.
        if parts[1] == "w":
            self.turn = WHITE
        else:
            self.turn = BLACK

        # Set the mover counters.
        self.halfmove_clock = int(parts[4])
        self.fullmove_number = int(parts[5]) or 1

        # Clear move stack.
        self.clear_stack()

    def parse_ucci(self, ucci):
        """
        Parses the given move in UCCI notation.

        The returned move is guaranteed to be either legal or a null move.

        :raises: :exc:`ValueError` if the move is invalid or illegal in the
            current position (but not a null move).
        """
        move = Move.from_ucci(ucci)

        if not move:
            return move

        if not self.is_legal(move):
            raise ValueError("illegal ucci: {0} in {1}".format(
                repr(ucci), self.fen()))

        return move

    def push_ucci(self, ucci):
        """
        Parses a move in UCCI notation and puts it on the move stack.

        Returns the move.

        :raises: :exc:`ValueError` if the move is invalid or illegal in the
            current position (but not a null move).
        """
        move = self.parse_ucci(ucci)
        self.push(move)
        return move

    def attacks_mask(self, square):
        """
            根据棋子的类型，计算可能的攻击方法。

            :param square: 起始计算的棋子位置，数字编号（0-89）
        """
        bb_square = BB_SQUARES[square]

        # 炮在这里不加处理
        if bb_square & self.cannons:
            return BB_ALL

        if bb_square & self.pawns:
            if bb_square & self.occupied_co[WHITE]:
                return BB_PAWN_ATTACKS[WHITE][square]
            else:
                return BB_PAWN_ATTACKS[BLACK][square]
        elif bb_square & self.horses:
            return BB_HORSE_ATTACKS[square][self._get_horse_around(square)]
        elif bb_square & self.kings:
            return BB_KING_ATTACKS[square]
        elif bb_square & self.elephants:
            return BB_ELEPHANT_ATTACKS[square][self._get_elephant_around(square)]
        elif bb_square & self.advisers:
            return BB_ADVISOR_ATTACKS[square]
        else:
            attacks = 0
            if bb_square & self.rooks:
                attacks |= (BB_RANK_ATTACKS[square][BB_RANK_MASKS[square] & self.occupied] | BB_FILE_ATTACKS[square][
                    BB_FILE_MASKS[square] & self.occupied])
            return attacks

    def _get_horse_around(self, square):
        ans = 0
        dd = [-1, 9, 1, -9]
        for i, d in enumerate(dd):
            if 0 <= square + d < 90 and (self.occupied & BB_SQUARES[square + d]):
                ans |= 1 << i
        return ans

    def _get_elephant_around(self, square):
        ans = 0
        dd = [8, 10, -10, -8]
        for i, d in enumerate(dd):
            if 0 <= square + d < 90 and (self.occupied & BB_SQUARES[square + d]):
                ans |= 1 << i
        return ans

    def _attackers_mask(self, color, square, occupied):
        rank_pieces = BB_RANK_MASKS[square] & occupied
        file_pieces = BB_FILE_MASKS[square] & occupied

        rooks = self.rooks

        attackers = (
                (BB_KING_ATTACKS[square] & self.kings) |
                (BB_HORSE_ATTACKS[square][self._get_horse_around(square)] & self.horses) |
                (BB_RANK_ATTACKS[square][rank_pieces] & rooks) |
                (BB_FILE_ATTACKS[square][file_pieces] & rooks) |
                (BB_PAWN_ATTACKS[not color][square] & self.pawns))

        # Find the cannon, check if the square is in it.
        cannons = self.cannons & self.occupied_co[color]
        cannon_bb = 0
        for c in scan_reversed(cannons):
            attacked = list(self._cannon_attack(c, color))
            if square in attacked:
                cannon_bb |= BB_SQUARES[c]

        attackers |= cannon_bb

        return attackers & self.occupied_co[color]

    def attackers_mask(self, color, square):
        """
        指定棋子是否被color方攻击？
        :param color:
        :param square:
        :return:
        """
        return self._attackers_mask(color, square, self.occupied)

    def is_king_face_king(self, move):
        new_kings = self.kings
        if not new_kings:
            return False
        if self.piece_type_at(move.from_square) == KING:
            new_kings = (new_kings | BB_SQUARES[move.to_square]) ^ BB_SQUARES[move.from_square]
        new_occupied = (self.occupied | BB_SQUARES[move.to_square]) ^ BB_SQUARES[move.from_square]
        new_occupied_co = [BB_VOID, BB_VOID]
        new_occupied_co[self.turn] = (self.occupied_co[self.turn] | BB_SQUARES[move.to_square]) ^ BB_SQUARES[move.from_square]
        new_occupied_co[not self.turn] = self.occupied_co[not self.turn]
        
        king_white = msb(new_occupied_co[True] & new_kings)
        king_black = msb(new_occupied_co[False] & new_kings)
        col_white = square_col(king_white)
        col_black = square_col(king_black)
        if col_white == col_black:
            mask = new_kings
            row_white = square_row(king_white)
            for i in range(0, row_white):
                mask = mask | (new_occupied & BB_SQUARES[get_square(i, col_white)])
            row_black = square_row(king_black)
            for i in range(row_black+1, 10):
                mask = mask | (new_occupied & BB_SQUARES[get_square(i, col_black)])
            mask = new_occupied & BB_COL[col_white] ^ mask
            return not mask
        return False

    def is_pseudo_legal(self, move):
        # Null moves are not pseudo legal.
        if not move:
            return False

        # Drops are not pseudo legal.
        if move.drop:
            return False

        # Source square must not be vacant.
        piece = self.piece_type_at(move.from_square)
        if not piece:
            return False

        # Get square masks.
        from_mask = BB_SQUARES[move.from_square]
        to_mask = BB_SQUARES[move.to_square]

        # Check turn.
        if not self.occupied_co[self.turn] & from_mask:
            return False

        # Destination square can not be occupied.
        if self.occupied_co[self.turn] & to_mask:
            return False

        # Handle all other pieces.
        return bool(self.attacks_mask(move.from_square) & to_mask)

    def is_into_check(self, move):
        """
        Checks if the given move would leave the king in check or put it into
        check. The move must be at least pseudo legal.
        """
        king = self.king(self.turn)
        if king is None:
            return False

        checkers = self.attackers_mask(not self.turn, king)
        if checkers:
            # If already in check, look if it is an evasion.
            if move not in self._generate_evasions(king, checkers, BB_SQUARES[move.from_square],
                                                   BB_SQUARES[move.to_square]):
                return True

        # return not self._is_safe(king, self._slider_blockers(king), move)
        return not self._is_safe(king, False, move)

    def is_legal(self, move):
        return not self.is_variant_end() and self.is_pseudo_legal(move) and not self.is_king_face_king(move)
        # and not self.is_into_check(move)

    def is_variant_end(self):
        """
        Checks if the game is over due to a special variant end condition.

        Note, for example, that stalemate is not considered a variant-specific
        end condition (this method will return ``False``), yet it can have a
        special **result** in suicide chess (any of
        :func:`~chess.Board.is_variant_loss()`,
        :func:`~chess.Board.is_variant_win()`,
        :func:`~chess.Board.is_variant_draw()` might return ``True``).
        """
        return False

    def _cannon_attack(self, square, turn=None):
        """
        生成炮的可能走法。
        :param square: int，[0,90)，代表棋子的位置
        :return:
        """
        if turn is None:
            turn = self.turn

        r = square_row(square)
        c = square_col(square)
        bb_same_row = BB_ROW[r] & self.occupied
        bb_same_col = BB_COL[c] & self.occupied
        pieces_row_index = list(scan_reversed(bb_same_row))
        pieces_col_index = list(scan_reversed(bb_same_col))
        # 生成攻击
        r_index = pieces_row_index.index(square)
        c_index = pieces_col_index.index(square)

        if r_index - 2 >= 0:
            to_square = pieces_row_index[r_index - 2]
            if BB_SQUARES[to_square] & self.occupied_co[~turn]:
                yield Move(square, to_square)

        if r_index + 2 < len(pieces_row_index):
            to_square = pieces_row_index[r_index + 2]
            if BB_SQUARES[to_square] & self.occupied_co[~turn]:
                yield Move(square, to_square)

        if c_index - 2 >= 0:
            to_square = pieces_col_index[c_index - 2]
            if BB_SQUARES[to_square] & self.occupied_co[~turn]:
                yield Move(square, to_square)
        if c_index + 2 < len(pieces_col_index):
            to_square = pieces_col_index[c_index + 2]
            if BB_SQUARES[to_square] & self.occupied_co[~turn]:
                yield Move(square, to_square)

    def _cannon_move(self, square):
        """
        生成炮的可能走法。
        :param square: int，[0,90)，代表棋子的位置
        :return:
        """
        r = square_row(square)
        c = square_col(square)
        bb_same_row = BB_ROW[r] & self.occupied
        bb_same_col = BB_COL[c] & self.occupied
        pieces_row_index = list(scan_reversed(bb_same_row))
        pieces_col_index = list(scan_reversed(bb_same_col))

        # 生成移动代码（不包含攻击）
        r_index = pieces_row_index.index(square)
        if r_index + 1 < len(pieces_row_index):
            r_down_edge = pieces_row_index[r_index + 1] + 1
        else:
            r_down_edge = get_square(r, 0)
        if r_index - 1 >= 0:
            r_up_edge = pieces_row_index[r_index - 1] - 1
        else:
            r_up_edge = get_square(r, 8)

        for x in range(r_down_edge, r_up_edge + 1):
            if x == square:
                continue
            yield Move(square, x)

        c_index = pieces_col_index.index(square)
        if c_index + 1 < len(pieces_col_index):
            r_left_edge = pieces_col_index[c_index + 1] + 9
        else:
            r_left_edge = get_square(0, c)
        if c_index - 1 >= 0:
            r_right_edge = pieces_col_index[c_index - 1] - 9
        else:
            r_right_edge = get_square(9, c)

        for x in range(r_left_edge, r_right_edge + 9, 9):
            if x == square:
                continue
            yield Move(square, x)

    def generate_pseudo_legal_moves(self, from_mask=BB_ALL, to_mask=BB_ALL):
        """
        生成当前局面下，所有种类棋子可行的移动路径。

        """
        our_pieces = self.occupied_co[self.turn]

        # Generate piece moves.
        non_pawns = our_pieces & ~self.pawns & ~self.cannons & from_mask
        for from_square in scan_reversed(non_pawns):
            # logger.debug(f'from square: {square_name(from_square)}')
            moves = self.attacks_mask(from_square) & ~our_pieces & to_mask
            for to_square in scan_reversed(moves):
                # logger.debug(f'to square: {square_name(to_square)}')
                yield Move(from_square, to_square)

        cannons = self.cannons & self.occupied_co[self.turn] & from_mask
        for c in scan_reversed(cannons):
            yield from self._cannon_attack(c)

        for c in scan_reversed(cannons):
            yield from self._cannon_move(c)

        # The remaining moves are all pawn moves.
        pawns = self.pawns & self.occupied_co[self.turn] & from_mask
        if not pawns:
            return

        # Generate pawn captures.
        capturers = pawns
        for from_square in scan_reversed(capturers):
            targets = (BB_PAWN_ATTACKS[self.turn][from_square] & ~self.occupied_co[self.turn])

            for to_square in scan_reversed(targets):
                # if square_row(to_square) in [0, 9]:
                #     yield Move(from_square, to_square, ROOK)
                # else:
                yield Move(from_square, to_square)

        # Prepare pawn advance generation.
        # if self.turn == WHITE:
        #     single_moves = pawns << 9 & ~self.occupied
        # else:
        #     single_moves = pawns >> 9 & ~self.occupied
        #
        # single_moves &= to_mask
        #
        # # Generate single pawn moves.
        # for to_square in scan_reversed(single_moves):
        #     from_square = to_square + (9 if self.turn == BLACK else -9)
        #     yield Move(from_square, to_square)

    def _generate_evasions(self, king, checkers, from_mask=BB_ALL, to_mask=BB_ALL):
        sliders = checkers & self.rooks

        attacked = 0
        try:
            for checker in scan_reversed(sliders):
                attacked |= BB_RAYS[king][checker] & ~BB_SQUARES[checker]
        except IndexError as e:
            print(checker)
            
            
        if BB_SQUARES[king] & from_mask:
            for to_square in scan_reversed(BB_KING_ATTACKS[king] & ~self.occupied_co[self.turn] & ~attacked & to_mask):
                yield Move(king, to_square)

        checker = msb(checkers)
        if BB_SQUARES[checker] == checkers:
            # Capture or block a single checker.
            target = BB_BETWEEN[king][checker] | checkers

            for move in self.generate_pseudo_legal_moves(~self.kings & from_mask, target & to_mask):
                yield move

    def is_attacked_by(self, color, square):
        """
        Checks if the given side attacks the given square.

        Pinned pieces still count as attackers. Pawns that can be captured
        en passant are **not** considered attacked.
        """
        return bool(self.attackers_mask(color, square))

    def _is_safe(self, king, blockers, move):
        if move.from_square == king:
            return not self.is_attacked_by(not self.turn, move.to_square)
        else:
            return not blockers & BB_SQUARES[move.from_square] or BB_RAYS[move.from_square][move.to_square] & \
                   BB_SQUARES[king]

    def generate_legal_moves(self, from_mask=BB_ALL, to_mask=BB_ALL):
        """
        生成当前的可行走法, 具体的先检查“将”或“帅”的位置，检查是否被将军，然后分别处理。
        现在generate_pseudo_legal_moves用法还不清楚。
        :param from_mask:
        :param to_mask:
        :return:
        """
        if self.is_variant_end():
            return

        # king_mask = self.kings & self.occupied_co[self.turn]
        # if king_mask:
        #     king = msb(king_mask)
        #     blockers = False  # self._slider_blockers(king)
        #     checkers = self.attackers_mask(not self.turn, king)
        #     if checkers:
        #         # 当前被将军
        #         for move in self._generate_evasions(king, checkers, from_mask, to_mask):
        #             if self._is_safe(king, blockers, move):
        #                 logger.debug(f'Move: {move}')
        #                 yield move
        #     else:
        #         # 当前未被将军
        #         for move in self.generate_pseudo_legal_moves(from_mask, to_mask):
        #             if self._is_safe(king, blockers, move):
        #                 logger.debug(f'Move: {move}')
        #                 yield move
        # else:
        for move in self.generate_pseudo_legal_moves(from_mask, to_mask):
            if not self.is_king_face_king(move):
                logger.debug(f'Move: {move}')
                yield move

    def is_game_over(self, claim_draw=False):
        """
        Checks if the game is over due to
        :func:`checkmate <chess.Board.is_checkmate()>`,
        :func:`stalemate <chess.Board.is_stalemate()>`,
        :func:`insufficient material <chess.Board.is_insufficient_material()>`,
        the :func:`seventyfive-move rule <chess.Board.is_seventyfive_moves()>`,
        :func:`fivefold repetition <chess.Board.is_fivefold_repetition()>`
        or a :func:`variant end condition <chess.Board.is_variant_end()>`.

        The game is not considered to be over by
        :func:`threefold repetition <chess.Board.can_claim_threefold_repetition()>`
        or the :func:`fifty-move rule <chess.Board.can_claim_fifty_moves()>`,
        unless *claim_draw* is given.
        """
        # Seventyfive-move rule.
        if self.is_seventyfive_moves():
            return True

        # Stalemate or checkmate.
        if not any(self.generate_legal_moves()):
            return True

        return False

    def can_claim_threefold_repetition(self):
        return False

    def result(self, claim_draw=False):
        """
        Gets the game result.

        ``1-0``, ``0-1`` or ``1/2-1/2`` if the
        :func:`game is over <chess.Board.is_game_over()>`. Otherwise, the
        result is undetermined: ``*``.
        """

        # Checkmate.
        if self.my_checkmate():
            return "0-1" if self.turn == WHITE else "1-0"

        # Draw claimed.
        # if claim_draw:  # and self.can_claim_draw():
        #     return "1/2-1/2"

        # Seventyfive-move rule or fivefold repetition.
        if self.is_seventyfive_moves():  # or self.is_fivefold_repetition():
            return "1/2-1/2"

        # # Insufficient material.
        # if self.is_insufficient_material():
        # 	return "1/2-1/2"

        # Stalemate.
        if not any(self.generate_legal_moves()):
            return "1/2-1/2"

        # Undetermined.
        return "*"

    def is_check(self):
        """Returns if the current side to move is in check."""
        king = self.king(self.turn)
        return king is not None and self.is_attacked_by(not self.turn, king)
    
    def my_checkmate(self):
        king = self.king(self.turn)
        return king is None
        
    def is_checkmate(self):
        """Checks if the current position is a checkmate."""
        if not self.is_check():
            return False

        return not any(self.generate_legal_moves())

    def is_seventyfive_moves(self):
        """
        Since the 1st of July 2014, a game is automatically drawn (without
        a claim by one of the players) if the half-move clock since a capture
        or pawn move is equal to or grather than 150. Other means to end a game
        take precedence.
        """
        if self.halfmove_clock >= 150:
            return True
        return False

    @staticmethod
    def _replace_num(s):
        for i in range(1, 10):
            s = s.replace(str(i), i * ' ')
        return s

    def __str__(self):
        """
        'rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR w - - 0 1'
        :return:
        """

        builder = [f"{''.join([' '] + FILE_NAMES)}\n"]
        fen = self.fen()
        fen = fen[:fen.find(' ')].split('/')
        for i, row in enumerate(fen):
            r = list(Board._replace_num(row))
            builder.append(f"{''.join([RANK_NAMES[i]] + r)}\n")

        return "".join(builder)

    def is_capture(self, move):
        """Checks if the given pseudo-legal move is a capture."""
        return bool(BB_SQUARES[move.to_square] & self.occupied_co[not self.turn])

    def is_zeroing(self, move):
        """Checks if the given pseudo-legal move is a capture or pawn move."""
        # return bool(
        #     BB_SQUARES[move.from_square] & self.pawns or BB_SQUARES[move.to_square] & self.occupied_co[not self.turn])
        return bool(BB_SQUARES[move.to_square] & self.occupied_co[not self.turn])

    def push(self, move):
        """
        Updates the position with the given move and puts it onto the
        move stack.

        >>> import chess
        >>>
        >>> board = chess.Board()
        >>>
        >>> Nf3 = chess.Move.from_uci("g1f3")
        >>> board.push(Nf3)  # Make the move

        >>> board.pop()  # Unmake the last move
        Move.from_uci('g1f3')

        Null moves just increment the move counters, switch turns and forfeit
        en passant capturing.

        :warning: Moves are not checked for legality.
        """
        # Remember game state.
        self.stack.append(_BoardState(self))
        self.move_stack.append(move)

        # move = self._to_chess960(move)

        # Reset en passant square.
        # ep_square = self.ep_square
        # self.ep_square = None

        # Increment move counters.
        self.halfmove_clock += 1
        if self.turn == BLACK:
            self.fullmove_number += 1

        # On a null move, simply swap turns and reset the en passant square.
        if not move:
            self.turn = not self.turn
            return

        # Drops.
        if move.drop:
            self._set_piece_at(move.to_square, move.drop, self.turn)
            self.turn = not self.turn
            return

        # Zero the half-move clock.
        if self.is_zeroing(move):
            self.halfmove_clock = 0

        from_bb = BB_SQUARES[move.from_square]
        # to_bb = BB_SQUARES[move.to_square]

        # promoted = self.promoted & from_bb
        piece_type = self._remove_piece_at(move.from_square)
        capture_square = move.to_square
        captured_piece_type = self.piece_type_at(capture_square)

        # Update castling rights.
        # self.castling_rights = self.clean_castling_rights() & ~to_bb & ~from_bb
        # if piece_type == KING and not promoted:
        #     if self.turn == WHITE:
        #         self.castling_rights &= ~BB_RANK_1
        #     else:
        #         self.castling_rights &= ~BB_RANK_8
        # elif captured_piece_type == KING and not self.promoted & to_bb:
        #     if self.turn == WHITE and square_rank(move.to_square) == 7:
        #         self.castling_rights &= ~BB_RANK_8
        #     elif self.turn == BLACK and square_rank(move.to_square) == 0:
        #         self.castling_rights &= ~BB_RANK_1

        # Handle special pawn moves.
        if piece_type == PAWN:
            diff = move.to_square - move.from_square

            if diff == 16 and square_row(move.from_square) == 1:
                self.ep_square = move.from_square + 8
            elif diff == -16 and square_row(move.from_square) == 6:
                self.ep_square = move.from_square - 8
            # elif move.to_square == ep_square and abs(diff) in [7, 9] and not captured_piece_type:
            #     # Remove pawns captured en passant.
            #     down = -8 if self.turn == WHITE else 8
            #     capture_square = ep_square + down
            #     captured_piece_type = self._remove_piece_at(capture_square)

        # Promotion.
        # if move.promotion:
        #     promoted = True
        #     piece_type = move.promotion

        # Castling.
        # castling = piece_type == KING and self.occupied_co[self.turn] & to_bb
        # if castling:
        #     a_side = square_file(move.to_square) < square_file(move.from_square)
        #
        #     self._remove_piece_at(move.from_square)
        #     self._remove_piece_at(move.to_square)
        #
        #     if a_side:
        #         self._set_piece_at(C1 if self.turn == WHITE else C8, KING, self.turn)
        #         self._set_piece_at(D1 if self.turn == WHITE else D8, ROOK, self.turn)
        #     else:
        #         self._set_piece_at(G1 if self.turn == WHITE else G8, KING, self.turn)
        #         self._set_piece_at(F1 if self.turn == WHITE else F8, ROOK, self.turn)

        # Put the piece on the target square.
        # if not castling and piece_type:
        if piece_type:
            # was_promoted = self.promoted & to_bb
            self._set_piece_at(move.to_square, piece_type, self.turn)

            # if captured_piece_type:
            #     self._push_capture(move, capture_square, captured_piece_type, was_promoted)

        # Swap turn.
        self.turn = not self.turn


class _BoardState(object):

    def __init__(self, board: Board):
        self.pawns = board.pawns
        self.horses = board.horses
        self.elephants = board.elephants
        self.rooks = board.rooks
        self.advisers = board.advisers
        self.kings = board.kings
        self.cannons = board.cannons

        self.occupied_w = board.occupied_co[WHITE]
        self.occupied_b = board.occupied_co[BLACK]
        self.occupied = board.occupied

        self.turn = board.turn
        self.halfmove_clock = board.halfmove_clock
        self.fullmove_number = board.fullmove_number


class PseudoLegalMoveGenerator(object):

    def __init__(self, board):
        self.board = board

    def __bool__(self):
        return any(self.board.generate_pseudo_legal_moves())

    __nonzero__ = __bool__

    def count(self):
        # List conversion is faster than iterating.
        return len(list(self))

    def __iter__(self):
        return self.board.generate_pseudo_legal_moves()

    def __contains__(self, move):
        return self.board.is_pseudo_legal(move)

    def __repr__(self):
        builder = []

        for move in self:
            if self.board.is_legal(move):
                builder.append(self.board.san(move))
            else:
                builder.append(self.board.uci(move))

        sans = ", ".join(builder)

        return "<PseudoLegalMoveGenerator at {0} ({1})>".format(hex(id(self)), sans)


class LegalMoveGenerator(object):

    def __init__(self, board):
        self.board = board

    def __bool__(self):
        return any(self.board.generate_legal_moves())

    __nonzero__ = __bool__

    def count(self):
        # List conversion is faster than iterating.
        return len(list(self))

    def __iter__(self):
        return self.board.generate_legal_moves()

    def __contains__(self, move):
        return self.board.is_legal(move)

    def __repr__(self):
        sans = ", ".join(self.board.san(move) for move in self)
        return "<LegalMoveGenerator at {0} ({1})>".format(hex(id(self)), sans)
