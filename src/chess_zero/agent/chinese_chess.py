#
# This is a model simplify and modify the python-chess api
# so that it can operate chinese chess
#

COLORS = [WHITE, BLACK] = [True, False]
COLOR_NAMES = ["black", "white"]

PIECE_TYPES = [PAWN, HORSE, ELEPHANT, ROOK, ADVISOR, KING, CANNON] = range(1, 9)
PIECE_SYMBOLS = ["", "p", "h", "e", "r", "a", "k", "c"]
PIECE_NAMES = ["", "pawn", "horse", "elephant", "rook", "advisor", "king", "cannon"]

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


def square_file(square):
	"""Gets the file index of the square where ``0`` is the a file."""
	return square % 9


def square_rank(square):
	"""Gets the rank index of the square where ``0`` is the first rank."""
	return square / 9


def square_name(square):
	"""Gets the name of the square, like ``a3``."""
	return FILE_NAMES[square_file(square)] + RANK_NAMES[square_rank(square)]


def square_distance(a, b):
	"""
	Gets the distance (i.e., the number of king steps) from square *a* to *b*.
	"""
	return max(abs(square_file(a) - square_file(b)), abs(square_rank(a) - square_rank(b)))


def square_mirror(square):
	"""Mirrors the square vertically."""
	return (square / 9) * 9 + (9 - (square % 9))


SQUARES_180 = [square_mirror(sq) for sq in SQUARES]
SQUARE_NAMES = [square_name(sq) for sq in SQUARES]

BB_VOID = 0
BB_ALL = 0x3ffffffffffffffffffffff
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
	return square in [3, 4, 5, 12, 13, 14, 21, 22, 23]


def _king_black_limit(square):
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


BB_HORSE_ATTACKS = [_sliding_attacks(sq, BB_ALL, [19, 17, 11, 7, -19, -17, -11, -7]) for sq in SQUARES]
BB_KING_ATTACKS = [[_sliding_attacks(sq, BB_ALL, [9, 1, -9, -1], _king_white_limit) for sq in SQUARES],
					[_sliding_attacks(sq, BB_ALL, [9, 1, -9, -1], _king_black_limit) for sq in SQUARES]]
BB_ELEPHANT_ATTACKS = [[_sliding_attacks(sq, BB_ALL, [20, 16, -20, -16], _elephant_white_limit) for sq in SQUARES],
						[_sliding_attacks(sq, BB_ALL, [20, 16, -20, -16], _elephant_black_limit) for sq in SQUARES]]
BB_ADVISOR_ATTACKS = [[_sliding_attacks(sq, BB_ALL, [10, 8, -10, -8], _advisor_white_limit) for sq in SQUARES],
						[_sliding_attacks(sq, BB_ALL, [10, 8, -10, -8], _advisor_black_limit) for sq in SQUARES]]
BB_PAWN_ATTACKS = [[_sliding_attacks(sq, BB_ALL, [-1, 1, 9], _pawn_white_limit) for sq in SQUARES],
					[_sliding_attacks(sq, BB_ALL, [-1, 1, -9], _pawn_black_limit) for sq in SQUARES]]

BB_FILES = [
	BB_FILE_A,
	BB_FILE_B,
	BB_FILE_C,
	BB_FILE_D,
	BB_FILE_E,
	BB_FILE_F,
	BB_FILE_G,
	BB_FILE_H,
	BB_FILE_I
] = [0x201008040201008040201 << i for i in range(9)]
BB_RANKS = [
	BB_RANK_0,
	BB_RANK_1,
	BB_RANK_2,
	BB_RANK_3,
	BB_RANK_4,
	BB_RANK_5,
	BB_RANK_6,
	BB_RANK_7,
	BB_RANK_8,
	BB_RANK_9
] = [0x1ff << (9 * i) for i in range(10)]


def _edges(square):
	return (((BB_RANK_0 | BB_RANK_9) & ~BB_RANKS[square_rank(square)]) |
			((BB_FILE_A | BB_FILE_I) & ~BB_FILES[square_file(square)]))


def _carry_rippler(mask):
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
		
		mask = _sliding_attacks(square, 0, deltas) & ~_edges(square)
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
				rays_row.append((BB_DIAG_ATTACKS[a][0] & BB_DIAG_ATTACKS[b][0]) | bb_a | bb_b)
				between_row.append(
					BB_DIAG_ATTACKS[a][BB_DIAG_MASKS[a] & bb_b] & BB_DIAG_ATTACKS[b][BB_DIAG_MASKS[b] & bb_a])
			elif BB_RANK_ATTACKS[a][0] & bb_b:
				rays_row.append(BB_RANK_ATTACKS[a][0] | bb_a)
				between_row.append(
					BB_RANK_ATTACKS[a][BB_RANK_MASKS[a] & bb_b] & BB_RANK_ATTACKS[b][BB_RANK_MASKS[b] & bb_a])
			elif BB_FILE_ATTACKS[a][0] & bb_b:
				rays_row.append(BB_FILE_ATTACKS[a][0] | bb_a)
				between_row.append(
					BB_FILE_ATTACKS[a][BB_FILE_MASKS[a] & bb_b] & BB_FILE_ATTACKS[b][BB_FILE_MASKS[b] & bb_a])
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
			raise ValueError("expected uci string to be of length 4 or 5: {0}".format(repr(ucci)))
	
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
		self.pawns = BB_A3 | BB_C3 | BB_E3 | BB_G3 | BB_I3 | BB_A6 | BB_C6 | BB_E6 | BB_G6 | BB_I6
		self.horse = BB_B0 | BB_H0 | BB_B9 | BB_H9
		self.elephant = BB_C0 | BB_G0 | BB_C9 | BB_G9
		self.rooks = BB_CORNERS
		self.advisor = BB_D0 | BB_F0 | BB_D9 | BB_F9
		self.kings = BB_E0 | BB_E9
		self.cannon = BB_B2 | BB_H2 | BB_B7 | BB_H7
		
		self.promoted = BB_VOID
		
		self.occupied_co[WHITE] = BB_RANK_0 | BB_B2 | BB_H2 | BB_A3 | BB_C3 | BB_E3 | BB_G3 | BB_I3
		self.occupied_co[BLACK] = BB_RANK_9 | BB_B7 | BB_H7 | BB_A6 | BB_C6 | BB_E6 | BB_G6 | BB_I6
		self.occupied = self.occupied_co[WHITE] | self.occupied_co[BLACK]
	
	def reset_board(self):
		self._reset_board()
	
	def _clear_board(self):
		self.pawns = BB_VOID
		self.horse = BB_VOID
		self.elephant = BB_VOID
		self.rooks = BB_VOID
		self.advisor = BB_VOID
		self.kings = BB_VOID
		self.cannon = BB_VOID
		
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
		"""Gets the piece type at the given square."""
		mask = BB_SQUARES[square]
		
		if not self.occupied & mask:
			return None
		elif self.pawns & mask:
			return PAWN
		elif self.horse & mask:
			return HORSE
		elif self.elephant & mask:
			return ELEPHANT
		elif self.rooks & mask:
			return ROOK
		elif self.advisor & mask:
			return ADVISOR
		elif self.kings & mask:
			return KING
		elif self.cannon & mask:
			return CANNON
	
	def board_fen(self, promoted=False):
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
			
			if BB_SQUARES[square] & BB_FILE_I:
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
			self.horse ^= mask
		elif piece_type == ELEPHANT:
			self.elephant ^= mask
		elif piece_type == ROOK:
			self.rooks ^= mask
		elif piece_type == ADVISOR:
			self.advisor ^= mask
		elif piece_type == KING:
			self.kings ^= mask
		elif piece_type == CANNON:
			self.cannon ^= mask
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
			self.horse |= mask
		elif piece_type == ELEPHANT:
			self.elephant |= mask
		elif piece_type == ROOK:
			self.rooks |= mask
		elif piece_type == ADVISOR:
			self.advisor |= mask
		elif piece_type == KING:
			self.kings |= mask
		elif piece_type == CANNON:
			self.cannon |= mask
		
		self.occupied ^= mask
		self.occupied_co[color] ^= mask
		
		if promoted:
			self.promoted ^= mask
	
	def _set_board_fen(self, fen):
		# Ensure the FEN is valid.
		rows = fen.split("/")
		if len(rows) != 10:
			raise ValueError("expected 10 rows in position part of fen: {0}".format(repr(fen)))
		
		# Validate each row.
		for row in rows:
			field_sum = 0
			previous_was_digit = False
			
			for c in row:
				if c in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
					if previous_was_digit:
						raise ValueError("two subsequent digits in position part of fen: {0}".format(repr(fen)))
					field_sum += int(c)
					previous_was_digit = True
				elif c.lower() in ["p", "n", "b", "r", "q", "k"]:
					field_sum += 1
					previous_was_digit = False
				else:
					raise ValueError("invalid character in position part of fen: {0}".format(repr(fen)))
			
			if field_sum != 9:
				raise ValueError("expected 9 columns per row in position part of fen: {0}".format(repr(fen)))
		
		# Clear the board.
		self._clear_board()
		
		# Put pieces on the board.
		square_index = 0
		for c in fen:
			if c in ["1", "2", "3", "4", "5", "6", "7", "8"]:
				square_index += int(c)
			elif c.lower() in ["p", "h", "e", "r", "a", "k", "c"]:
				piece = Piece.from_symbol(c)
				self._set_piece_at(SQUARES_180[square_index], piece.piece_type, piece.color)
				square_index += 1
	
	def king(self, color):
		"""
		Finds the king square of the given side. Returns ``None`` if there
		is no king of that color.

		In variants with king promotions, only non-promoted kings are
		considered.
		"""
		king_mask = self.occupied_co[color] & self.kings & ~self.promoted
		if king_mask:
			return msb(king_mask)


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
		BaseBoard.__init__(self, None)
		
		self.chess960 = chess960
		
		self.pseudo_legal_moves = PseudoLegalMoveGenerator(self)
		self.legal_moves = LegalMoveGenerator(self)
		
		self.move_stack = []
		self.stack = []
		
		self.turn = WHITE
		self.halfmove_clock = 0
		self.fullmove_number = 1
		
		if fen is None:
			self.clear()
		elif fen == type(self).starting_fen:
			self.reset()
		else:
			self.set_fen(fen)
	
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
			self.epd(shredder=shredder, en_passant=en_passant, promoted=promoted),
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
		
		epd.append(self.board_fen(promoted=promoted))
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
			raise ValueError("fen string should consist of 6 parts: {0}".format(repr(fen)))
		
		# Check that the turn part is valid.
		if not parts[1] in ["w", "b"]:
			raise ValueError("expected 'w' or 'b' for turn part of fen: {0}".format(repr(fen)))
		
		# Check that the half-move part is valid.
		if int(parts[4]) < 0:
			raise ValueError("half-move clock can not be negative: {0}".format(repr(fen)))
		
		# Check that the full-move number part is valid.
		# 0 is allowed for compability, but later replaced with 1.
		if int(parts[5]) < 0:
			raise ValueError("full-move number must be positive: {0}".format(repr(fen)))
		
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
			raise ValueError("illegal uci: {0} in {1}".format(repr(ucci), self.fen()))
		
		return move
	
	def push_uci(self, ucci):
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
		bb_square = BB_SQUARES[square]
		
		if bb_square & self.pawns:
			if bb_square & self.occupied_co[WHITE]:
				return BB_PAWN_ATTACKS[WHITE][square]
			else:
				return BB_PAWN_ATTACKS[BLACK][square]
		elif bb_square & self.horse:
			return BB_HORSE_ATTACKS[square]
		elif bb_square & self.kings:
			if bb_square & self.occupied_co[WHITE]:
				return BB_KING_ATTACKS[WHITE][square]
			else:
				return BB_KING_ATTACKS[BLACK][square]
		elif bb_square & self.elephant:
			if bb_square & self.occupied_co[WHITE]:
				return BB_ELEPHANT_ATTACKS[WHITE][square]
			else:
				return BB_ELEPHANT_ATTACKS[BLACK][square]
		elif bb_square & self.advisor:
			if bb_square & self.occupied_co[WHITE]:
				return BB_ADVISOR_ATTACKS[WHITE][square]
			else:
				return BB_ADVISOR_ATTACKS[BLACK][square]
		else:
			attacks = 0
			if bb_square & self.rooks:
				attacks |= (BB_RANK_ATTACKS[square][BB_RANK_MASKS[square] & self.occupied] | BB_FILE_ATTACKS[square][
					BB_FILE_MASKS[square] & self.occupied])
			return attacks
	
	def attackers_mask(self, color, square):
		return self._attackers_mask(color, square, self.occupied)
	
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
		
		## i dont know why split into tow part
		## and i commit the PAWN one
		
		# # Handle pawn moves.
		# if piece == PAWN:
		# 	return move in self.generate_pseudo_legal_moves(from_mask, to_mask)
		
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
			if move not in self._generate_evasions(king, checkers, BB_SQUARES[move.from_square], BB_SQUARES[move.to_square]):
				return True
		
		# return not self._is_safe(king, self._slider_blockers(king), move)
		return not self._is_safe(king, False, move)
	
	def is_legal(self, move):
		return not self.is_variant_end() and self.is_pseudo_legal(move) and not self.is_into_check(move)
	
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
	
	def generate_pseudo_legal_moves(self, from_mask=BB_ALL, to_mask=BB_ALL):
		our_pieces = self.occupied_co[self.turn]
		
		# Generate piece moves.
		non_pawns = our_pieces & ~self.pawns & from_mask
		for from_square in scan_reversed(non_pawns):
			moves = self.attacks_mask(from_square) & ~our_pieces & to_mask
			for to_square in scan_reversed(moves):
				yield Move(from_square, to_square)
		
		# The remaining moves are all pawn moves.
		pawns = self.pawns & self.occupied_co[self.turn] & from_mask
		if not pawns:
			return
		
		# Generate pawn captures.
		capturers = pawns
		for from_square in scan_reversed(capturers):
			targets = (BB_PAWN_ATTACKS[self.turn][from_square] & self.occupied_co[not self.turn] & to_mask)
			
			for to_square in scan_reversed(targets):
				if square_rank(to_square) in [0, 9]:
					yield Move(from_square, to_square, ROOK)
				else:
					yield Move(from_square, to_square)
		
		# Prepare pawn advance generation.
		if self.turn == WHITE:
			single_moves = pawns << 9 & ~self.occupied
		else:
			single_moves = pawns >> 9 & ~self.occupied
		
		single_moves &= to_mask
		
		# Generate single pawn moves.
		for to_square in scan_reversed(single_moves):
			from_square = to_square + (9 if self.turn == BLACK else -9)
			
			if square_rank(to_square) in [0, 9]:
				yield Move(from_square, to_square, ROOK)
			else:
				yield Move(from_square, to_square)
	
	def _generate_evasions(self, king, checkers, from_mask=BB_ALL, to_mask=BB_ALL):
		sliders = checkers & self.rooks
		
		attacked = 0
		for checker in scan_reversed(sliders):
			attacked |= BB_RAYS[king][checker] & ~BB_SQUARES[checker]
		
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
		if self.is_variant_end():
			return
		
		king_mask = self.kings & self.occupied_co[self.turn]
		if king_mask:
			king = msb(king_mask)
			blockers = False  # self._slider_blockers(king)
			checkers = self.attackers_mask(not self.turn, king)
			if checkers:
				for move in self._generate_evasions(king, checkers, from_mask, to_mask):
					if self._is_safe(king, blockers, move):
						yield move
			else:
				for move in self.generate_pseudo_legal_moves(from_mask, to_mask):
					if self._is_safe(king, blockers, move):
						yield move
		else:
			for move in self.generate_pseudo_legal_moves(from_mask, to_mask):
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
	
	def result(self, claim_draw=False):
		"""
		Gets the game result.

		``1-0``, ``0-1`` or ``1/2-1/2`` if the
		:func:`game is over <chess.Board.is_game_over()>`. Otherwise, the
		result is undetermined: ``*``.
		"""
		
		# Checkmate.
		if self.is_checkmate():
			return "0-1" if self.turn == WHITE else "1-0"
		
		# Draw claimed.
		if claim_draw:		# and self.can_claim_draw():
			return "1/2-1/2"
		
		# Seventyfive-move rule or fivefold repetition.
		if self.is_seventyfive_moves():		# or self.is_fivefold_repetition():
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


class PseudoLegalMoveGenerator(object):
	
	def __init__(self, board):
		self.board = board


class LegalMoveGenerator(object):
	
	def __init__(self, board):
		self.board = board