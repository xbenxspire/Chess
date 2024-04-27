# Author: Benjamin Pierce
# GitHub username: xbenxspire
# Date: 07MAR2024
# Description: ChessVar class manages a variation of chess that includes standard chess rules and introduces
# fairy pieces with unique movement rules. The class is responsible for initializing the game state, handling turns,
# and validating moves, including the placement of fairy pieces onto the board.


# definitions of constants for ease of use
WHITE, BLACK = 'white', 'black'
PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING, FALCON, HUNTER = 'P', 'R', 'N', 'B', 'Q', 'K', 'F', 'H'
BOARD_SIZE = 8


# helper function to convert algebraic notation into row and column
def algebraic_to_index(self, square):
    """Convert algebraic chess notation to row and column indexes."""
    col = ord(square[0]) - ord('a')
    row = 8 - int(square[1])
    return row, col


class ChessVar:
    """Represents variation of chess with special rules and fairy pieces."""

    def __init__(self):
        """Initialize chess board, set the current player and game state."""
        self._board = Board()
        self._current_player = 'white'
        self._game_state = 'UNFINISHED'
        self._captured_pieces = {'white': [], 'black': []}
        self._eligible_fairy_pieces = {'white': [], 'black': []}

    def get_game_state(self):
        """Return current state of the game."""
        return self._game_state

    def make_move(self, from_square, to_square):
        """Attempt to make a move on the board and return True if successful."""
        if self._game_state != 'UNFINISHED':
            return False
        if not self._board.move_piece(from_square, to_square, self._current_player):
            return False
        captured_piece = self._board.get_piece_at(to_square)
        if captured_piece and captured_piece.color != self._current_player:
            self._captured_pieces[self._current_player].append(captured_piece)
            self._board.remove_piece(to_square)
            if captured_piece.type in ['Q', 'R', 'B', 'N']:
                self._eligible_fairy_pieces[self._current_player].append(
                    'F' if 'F' not in self._eligible_fairy_pieces[self._current_player] else 'H')
        if self._board.is_king_captured(self._opposite_color(self._current_player)):
            self._game_state = 'WHITE_WON' if self._current_player == 'white' else 'BLACK_WON'
        self._switch_player()
        return True

    def enter_fairy_piece(self, piece_type, square):
        """Enter a fairy piece onto the board if conditions are met."""
        if self._game_state != 'UNFINISHED':
            return False
        if piece_type not in self._eligible_fairy_pieces[self._current_player]:
            return False
        if not self._board.place_fairy_piece(piece_type, square, self._current_player):
            return False
        self._switch_player()
        return True

    def _switch_player(self):
        """Switch turns between players."""
        self._current_player = 'black' if self._current_player == 'white' else 'white'

    def _opposite_color(self, color):
        """Get opposite color."""
        return 'black' if color == 'white' else 'white'


def initialize_board():
    board = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    # place rooks, knights, bishops, queens, kings
    for color, row in [(WHITE, 0), (BLACK, 7)]:
        placement = [Rook(color), Knight(color), Bishop(color), Queen(color),
                     King(color), Bishop(color), Knight(color), Rook(color)]
        for col, piece in enumerate(placement):
            board[row][col] = piece
        # place pawns
        for col in range(BOARD_SIZE):
            board[row + (1 if color == WHITE else -1)][col] = Pawn(color)
    return board


class Board:
    """Manages game board for ChessVar."""

    def __init__(self):
        self._grid = initialize_board()

    def place_piece(self, piece, square):
        row, col = self.algebraic_to_index(square)
        self._grid[row][col] = piece

    def get_piece_at(self, square):
        row, col = self.algebraic_to_index(square)
        return self._grid[row][col]

    def remove_piece(self, square):
        row, col = self.algebraic_to_index(square)
        self._grid[row][col] = None

    def move_piece(self, from_square, to_square, player):
        from_row, from_col = self.algebraic_to_index(from_square)
        to_row, to_col = self.algebraic_to_index(to_square)
        piece = self.get_piece_at(from_square)
        if piece and piece.color == player and piece.is_legal_move(from_row, from_col, to_row, to_col, self._grid):
            self.place_piece(piece, to_square)
            self.remove_piece(from_square)
            return True
        return False

    def can_place_fairy_piece(self, piece_type, square, player, captured_pieces):
        if square not in ('a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1',
                          'a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8'):
            return False
        if self.get_piece_at(square) is not None:
            return False
        if player == WHITE and piece_type.islower():
            return False
        if player == BLACK and piece_type.isupper():
            return False
        required_captures = 1 if piece_type.upper() == 'F' else 2
        return len(captured_pieces[player]) >= required_captures

    def place_fairy_piece(self, piece_type, square, player):
        piece_class = Falcon if piece_type.upper() == 'F' else Hunter
        self.place_piece(piece_class(player), square)

    def is_king_captured(self, color):
        """Check if the king of the given color is captured."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self._grid[row][col]
                if piece and piece.piece_type == KING and piece.color == color:
                    return False
        return True

    def algebraic_to_index(self, square):
        """Convert algebraic chess notation to row and column indexes."""
        col = ord(square[0]) - ord('a')
        row = 8 - int(square[1])
        return row, col


class ChessPiece:
    """Base class for a chess piece."""

    def __init__(self, color):
        self.color = color
        self.piece_type = None  # This will be set by each subclass.

    def is_legal_move(self, from_row, from_col, to_row, to_col, board):
        """Determine if legal move."""
        raise NotImplementedError("Must be implemented by subclass.")


class Pawn(ChessPiece):
    """
    Pawn class.
    """

    def __init__(self, color):
        super().__init__(color)
        self.piece_type = PAWN

    def is_legal_move(self, from_row, from_col, to_row, to_col, board):
        direction = 1 if self.color == WHITE else -1
        start_row = 1 if self.color == WHITE else 6
        if from_col == to_col:  # Moving forward
            if (from_row + direction == to_row and board[to_row][to_col] is None) or \
                    (from_row == start_row and from_row + direction * 2 == to_row and
                     board[from_row + direction][from_col] is None and board[to_row][to_col] is None):
                return True
        elif abs(from_col - to_col) == 1 and from_row + direction == to_row:  # Capturing diagonally
            target_piece = board[to_row][to_col]
            return target_piece is not None and target_piece.color != self.color
        return False


class Rook(ChessPiece):
    """
    Rook class.
    """

    def __init__(self, color):
        super().__init__(color)
        self.piece_type = ROOK

    def is_legal_move(self, from_row, from_col, to_row, to_col, board):
        if from_col == to_col or from_row == to_row:
            return self._is_straight_path_clear(from_row, from_col, to_row, to_col, board)
        return False


class Knight(ChessPiece):
    """
    Knight class.
    """

    def __init__(self, color):
        super().__init__(color)
        self.piece_type = KNIGHT

    def is_legal_move(self, from_row, from_col, to_row, to_col, board):
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        return (row_diff, col_diff) == (1, 2) or (row_diff, col_diff) == (2, 1)


class Bishop(ChessPiece):
    """
    Bishop class.
    """

    def __init__(self, color):
        super().__init__(color)
        self.piece_type = BISHOP

    def is_legal_move(self, from_row, from_col, to_row, to_col, board):
        if abs(from_row - to_row) == abs(from_col - to_col):
            return self._is_diagonal_path_clear(from_row, from_col, to_row, to_col, board)
        return False


class Queen(ChessPiece):
    """
    Queen class.
    """

    def __init__(self, color):
        super().__init__(color)
        self.piece_type = QUEEN

    def is_legal_move(self, from_row, from_col, to_row, to_col, board):
        if from_row == to_row or from_col == to_col:
            return self._is_straight_path_clear(from_row, from_col, to_row, to_col, board)
        if abs(from_row - to_row) == abs(from_col - to_col):
            return self._is_diagonal_path_clear(from_row, from_col, to_row, to_col, board)
        return False


class King(ChessPiece):
    """
    King class.
    """

    def __init__(self, color):
        super().__init__(color)
        self.piece_type = KING

    def is_legal_move(self, from_row, from_col, to_row, to_col, board):
        row_diff = abs(from_row - to_row)
        col_diff = abs(from_col - to_col)
        return (row_diff <= 1 and col_diff <= 1) and not (row_diff == 0 and col_diff == 0)


class Falcon(ChessPiece):
    """
    Falcon class, which is a fairy piece that moves forward like a bishop and backward like a rook.
    """

    def __init__(self, color):
        super().__init__(color)
        self.piece_type = FALCON

    def is_legal_move(self, from_row, from_col, to_row, to_col, board):
        forward_move = to_row > from_row if self.color == WHITE else to_row < from_row
        if forward_move:
            return abs(from_row - to_row) == abs(from_col - to_col) and \
                   self._is_diagonal_path_clear(from_row, from_col, to_row, to_col, board)
        else:
            return (from_row == to_row or from_col == to_col) and \
                   self._is_straight_path_clear(from_row, from_col, to_row, to_col, board)


class Hunter(ChessPiece):
    """
    Hunter class, which is a fairy piece that moves forward like a rook and backward like a bishop.
    """

    def __init__(self, color):
        super().__init__(color)
        self.piece_type = HUNTER

    def is_legal_move(self, from_row, from_col, to_row, to_col, board):
        forward_move = to_row > from_row if self.color == WHITE else to_row < from_row
        if forward_move:
            return (from_row == to_row or from_col == to_col) and \
                   self._is_straight_path_clear(from_row, from_col, to_row, to_col, board)
        else:
            return abs(from_row - to_row) == abs(from_col - to_col) and \
                   self._is_diagonal_path_clear(from_row, from_col, to_row, to_col, board)


class Board:
    """
    Manages game board for ChessVar.
    """

    def __init__(self):
        self._grid = self.initialize_board()

    def _initialize_board(self):
        board = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        # place rooks, knights, bishops, queens, kings
        for color, row in [(WHITE, 0), (BLACK, 7)]:
            placement = [Rook(color), Knight(color), Bishop(color), Queen(color),
                         King(color), Bishop(color), Knight(color), Rook(color)]
            for col, piece in enumerate(placement):
                board[row][col] = piece
            # place pawns
            for col in range(BOARD_SIZE):
                board[row + (1 if color == WHITE else -1)][col] = Pawn(color)
        return board

    def place_piece(self, piece, square):
        row, col = algebraic_to_index(square)
        self.grid[row][col] = piece

    def get_piece_at(self, square):
        row, col = algebraic_to_index(square)
        return self.grid[row][col]

    def remove_piece(self, square):
        row, col = algebraic_to_index(square)
        self.grid[row][col] = None

    def move_piece(self, from_square, to_square, player):
        from_row, from_col = algebraic_to_index(from_square)
        to_row, to_col = algebraic_to_index(to_square)
        piece = self.get_piece_at(from_square)
        if piece and piece.color == player and piece.is_legal_move(from_row, from_col, to_row, to_col, self.grid):
            self.place_piece(piece, to_square)
            self.remove_piece(from_square)
            return True
        return False

    def can_place_fairy_piece(self, piece_type, square, player, captured_pieces):
        if square not in ('a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1',
                          'a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8'):
            return False
        if self.get_piece_at(square) is not None:
            return False
        if player == WHITE and piece_type.islower():
            return False
        if player == BLACK and piece_type.isupper():
            return False
        required_captures = 1 if piece_type.upper() == 'F' else 2
        return len(captured_pieces[player]) >= required_captures

    def place_fairy_piece(self, piece_type, square, player):
        piece_class = Falcon if piece_type.upper() == 'F' else Hunter
        self.place_piece(piece_class(player), square)

    def is_king_captured(self, color):
        """Check if the king of the given color is captured."""
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self._grid[row][col]
                if piece and piece.piece_type == KING and piece.color == color:
                    return False
        return True


def is_path_clear(from_row, from_col, to_row, to_col, board):
    """
    Check if the path is clear for move to be made. This method works for straight and diagonal moves.
    """
    row_step = 1 if to_row > from_row else -1 if to_row < from_row else 0
    col_step = 1 if to_col > from_col else -1 if to_col < from_col else 0
    row, col = from_row + row_step, from_col + col_step

    while (row, col) != (to_row, to_col):
        if board[row][col] is not None:
            return False
        row += row_step
        col += col_step
    return True
