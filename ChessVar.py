# Author: Benjamin Pierce
# GitHub username: xbenxspire
# Date: 07MAR2024
# Description: ChessVar class manages a variation of chess that includes standard chess rules and introduces
# fairy pieces with unique movement rules. The class is responsible for initializing the game state, handling turns,
# and validating moves, including the placement of fairy pieces onto the board.


class ChessVar:
    """
    Class to represent chess game that includes fairy pieces (Falcon and Hunter).

    Attributes:
        _board (list): Represents game board as 2D list.
        _turn (bool): Tracks current turn. True for white, False for black.
        _game_state (str): Holds current state of game ('UNFINISHED', 'WHITE_WON', or 'BLACK_WON').
        _captured_pieces (dict): Records captured pieces, with keys as 'white' and 'black', and values as sets
        of captured pieces.
        _fairy_pieces (dict): Tracks available fairy pieces for each player, with keys as 'white' and 'black',
        and values as sets of fairy piece types ('F', 'H').
    """

    def __init__(self):
        """
        Initializes ChessVar class with a board, turn, game state, captured pieces, and fairy pieces.
        """
        self._board = self._create_initial_board()
        self._turn = True  # True for white's turn, False for black's turn
        self._game_state = 'UNFINISHED'
        self._captured_pieces = {'white': set(), 'black': set()}
        self._fairy_pieces = {'white': {'F', 'H'}, 'black': {'f', 'h'}}

    def get_game_state(self):
        """
        Returns current state of the game.

        Returns:
            str: Current game state ('UNFINISHED', 'WHITE_WON', or 'BLACK_WON').
        """
        return self._game_state

    def make_move(self, from_square, to_square):
        """
        If move is legal, move piece from one square to another and update game state.

        Parameters:
            from_square (str): Algebraic notation of the square from which to move piece.
            to_square (str): Algebraic notation of the square to which to move piece.

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        if self._game_state != 'UNFINISHED':
            return False

        from_pos = self._convert_to_pos(from_square)
        to_pos = self._convert_to_pos(to_square)

        # ensure destination square is not occupied by same color piece
        if self._board[to_pos[0]][to_pos[1]] != '' and \
                self._board[from_pos[0]][from_pos[1]].isupper() == self._board[to_pos[0]][to_pos[1]].isupper():
            return False

        if not self._is_legal_move(from_pos, to_pos):
            return False

        # move piece, update board
        self._move_piece(from_pos, to_pos)
        self._switch_turns()
        self._check_game_over(to_pos)
        return True

    def enter_fairy_piece(self, piece_type, square):
        """
        Enters a fairy piece onto the board at the specified square if allowed.

        Parameters:
            piece_type (str): Type of fairy piece ('F', 'f', 'H', 'h') to place on the board.
            square (str): Algebraic notation of the square where to place fairy piece.

        Returns:
            bool: True if fairy piece was successfully placed, False otherwise.
        """
        current_color = 'white' if piece_type.isupper() else 'black'
        if (self._game_state != 'UNFINISHED' or
                not self._can_place_fairy_piece(piece_type, square) or
                piece_type not in self._fairy_pieces[current_color] or
                not self._is_square_empty(square)):
            return False

        pos = self._convert_to_pos(square)
        self._board[pos[0]][pos[1]] = piece_type
        self._fairy_pieces[current_color].remove(piece_type)
        self._switch_turns()
        return True

    def _is_square_empty(self, square):
        """
        Checks if given square is empty.

        Parameters:
            square (str): Algebraic notation of square to check.

        Returns:
            bool: True if square is empty, False otherwise.
        """
        pos = self._convert_to_pos(square)
        return self._board[pos[0]][pos[1]] == ''

    def _is_legal_move(self, from_pos, to_pos):
        """
        Checks if move is legal according to chess rules and game specifications.

        Parameters:
            from_pos (tuple): Tuple representing starting position of the move.
            to_pos (tuple): Tuple representing ending position of the move.

        Returns:
            bool: True if legal move, False otherwise.
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self._board[from_row][from_col]
        target_piece = self._board[to_row][to_col]

        if not piece or (piece.isupper() != self._turn):
            return False

        # add logic to handle each piece's legal moves
        if piece.lower() == 'p':  # pawn
            return self._is_legal_pawn_move(from_pos, to_pos, piece)
        elif piece.lower() == 'r':  # rook
            return self._is_straight_move(from_pos, to_pos) and self._path_is_clear(from_pos, to_pos)
        elif piece.lower() == 'n':  # knight
            return self._is_legal_knight_move(from_pos, to_pos)
        elif piece.lower() == 'b':  # bishop
            return self._is_diagonal_move(from_pos, to_pos) and self._path_is_clear(from_pos, to_pos)
        elif piece.lower() == 'q':  # queen
            return (self._is_straight_move(from_pos, to_pos) or self._is_diagonal_move(from_pos, to_pos)) and \
                   self._path_is_clear(from_pos, to_pos)
        elif piece.lower() == 'k':  # king
            return self._is_king_move(from_pos, to_pos)
        elif piece.lower() in 'fh':  # fairy pieces (falcon and hunter)
            return self._is_valid_fairy_piece_move(from_pos, to_pos, piece)

        return False  # if none of the above, move is illegal

    def _is_straight_move(self, from_pos, to_pos):
        """
        Check if move is along a file or rank.
        """
        return from_pos[0] == to_pos[0] or from_pos[1] == to_pos[1]

    def _is_diagonal_move(self, from_pos, to_pos):
        """
        Check if move is along a diagonal.
        """
        return abs(from_pos[0] - to_pos[0]) == abs(from_pos[1] - to_pos[1])

    def _is_legal_knight_move(self, from_pos, to_pos):
        """
        Check if the knight move is L-shaped.
        """
        row_diff = abs(from_pos[0] - to_pos[0])
        col_diff = abs(from_pos[1] - to_pos[1])
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def _is_king_move(self, from_pos, to_pos):
        """
        Check if the king moves only one square in any direction.
        """
        row_diff = abs(from_pos[0] - to_pos[0])
        col_diff = abs(from_pos[1] - to_pos[1])
        return (row_diff <= 1 and col_diff <= 1) and not (row_diff == 0 and col_diff == 0)

    def _is_valid_fairy_piece_move(self, from_pos, to_pos, piece):
        """
        Check if the move is valid for fairy pieces (Falcon and Hunter).
        Falcon moves forward like a bishop, backward like a rook.
        Hunter moves forward like a rook, backward like a bishop.
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        forward_move = to_row < from_row if piece.isupper() else to_row > from_row

        if piece.lower() == 'f':
            if forward_move:
                return self._is_diagonal_move(from_pos, to_pos) and self._path_is_clear(from_pos, to_pos)
            else:
                return self._is_straight_move(from_pos, to_pos) and self._path_is_clear(from_pos, to_pos)

        elif piece.lower() == 'h':
            if forward_move:
                return self._is_straight_move(from_pos, to_pos) and self._path_is_clear(from_pos, to_pos)
            else:
                return self._is_diagonal_move(from_pos, to_pos) and self._path_is_clear(from_pos, to_pos)

        return False

    def _path_is_clear(self, from_pos, to_pos):
        """
        Check if there are no pieces between from_pos and to_pos for rook, bishop, and queen moves.
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        row_step = 1 if to_row > from_row else -1 if to_row < from_row else 0
        col_step = 1 if to_col > from_col else -1 if to_col < from_col else 0

        current_row, current_col = from_row + row_step, from_col + col_step
        while (current_row, current_col) != to_pos:
            if self._board[current_row][current_col] != '':
                return False  # There is a piece blocking the path
            current_row += row_step
            current_col += col_step

        return True

    def _is_legal_pawn_move(self, from_pos, to_pos, piece):
        """
        Check if the pawn move is legal, including the initial double move and capturing moves.

        Parameters:
            from_pos (tuple): Starting position of pawn (row, column).
            to_pos (tuple): Intended destination of pawn (row, column).
            piece (str): Pawn piece being moved.

        Returns:
        bool: True if legal move, False otherwise.
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        direction = 1 if piece.islower() else -1  # pawns move up for white, down for black
        start_row = 6 if piece.isupper() else 1  # starting row depends on the pawn's color

        # ensure move is within bounds of board
        if not (0 <= to_row <= 7 and 0 <= to_col <= 7):
            return False

        # check for forward move
        if from_col == to_col:
            if (to_row - from_row) == direction and self._board[to_row][to_col] == '':
                return True
            if from_row == start_row and (to_row - from_row) == 2 * direction and \
                    self._board[to_row][to_col] == '' and self._board[from_row + direction][from_col] == '':
                return True

        # check for capturing move
        elif abs(from_col - to_col) == 1 and (to_row - from_row) == direction:
            if self._board[to_row][to_col] != '' and self._board[to_row][to_col].isupper() != piece.isupper():
                return True

        return False  # if none of the above, the pawn move is illegal

    def _move_piece(self, from_pos, to_pos):
        """
        Moves a piece on the board and updates captured pieces.
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self._board[from_row][from_col]

        # handle capture
        target_piece = self._board[to_row][to_col]
        if target_piece:
            self._captured_pieces['white' if target_piece.islower() else 'black'].add(target_piece)
            self._board[to_row][to_col] = ''  # remove captured piece from board

        # move piece
        self._board[to_row][to_col] = piece
        self._board[from_row][from_col] = ''

    def _switch_turns(self):
        """
        Switches turn between players.
        """
        self._turn = not self._turn

    def _check_game_over(self, pos):
        """
        Checks if game is over if a king is captured.
        """
        to_row, to_col = pos
        target_piece = self._board[to_row][to_col]
        if target_piece.lower() == 'k':
            self._game_state = 'BLACK_WON' if target_piece.isupper() else 'WHITE_WON'

    def _can_place_fairy_piece(self, piece_type, square):
        """
        Checks if fairy piece can be placed on board.
        """
        if not self._is_square_empty(square):
            return False

        current_color = 'white' if piece_type.isupper() else 'black'
        home_rank = '12' if current_color == 'white' else '78'
        if square[1] not in home_rank:
            return False

        lost_pieces = self._captured_pieces[current_color]
        allowed_pieces = {'F': ['Q', 'R', 'B', 'N'], 'H': ['Q', 'R', 'B', 'N']}
        if piece_type.islower():
            allowed_pieces = {k.lower(): [p.lower() for p in v] for k, v in allowed_pieces.items()}

        # checking if the player has lost at least one of the specific pieces
        has_lost_required_pieces = any(piece in lost_pieces for piece in allowed_pieces[piece_type])

        # check if the player has already placed one fairy piece. If true, they should have lost a second specific
        # piece to place the remaining one.
        already_placed = len(self._fairy_pieces[current_color]) < 2
        can_place_second = not already_placed or \
                           (already_placed and len([p for p in lost_pieces if p in allowed_pieces[piece_type]]) >= 2)

        return has_lost_required_pieces and can_place_second

    def _convert_to_pos(self, square):
        """
        Converts algebraic notation to board notation. Example: 'a1' -> (7, 0), 'b2' -> (6, 1), etc.
        """
        row = 8 - int(square[1])
        col = ord(square[0]) - ord('a')
        return (row, col)

    def _create_initial_board(self):
        """
        Creates initial board setup for the game.

        Returns:
             list: 2D list representing initial chess board.
        """
        # initial setup for standard chess pieces
        board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p' for _ in range(8)],
            ['' for _ in range(8)],
            ['' for _ in range(8)],
            ['' for _ in range(8)],
            ['' for _ in range(8)],
            ['P' for _ in range(8)],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        return board


def test_chess_var():
    game = ChessVar()

    # test pawn and knight moves
    assert game.make_move('e2', 'e4')  # pawn moves two spaces forward
    assert game.make_move('e7', 'e5')  # opponent's pawn moves two spaces forward
    assert game.make_move('g1', 'f3')  # knight moves
    assert game.make_move('b8', 'c6')  # opponent's knight moves

    # test illegal move (attempting to move opponent's piece)
    assert not game.make_move('e5', 'e4')

    game._switch_turns()  # manually switch turn for testing

    # test capturing a piece
    assert game.make_move('e5', 'd4')  # pawn captures

    # test fairy piece movement rules and entering the game
    game._captured_pieces['white'].update({'N', 'B'})  # white has lost a knight and bishop
    assert not game.enter_fairy_piece('F', 'e2')  # cannot place falcon because not on home rank
    assert game.enter_fairy_piece('F', 'd1')  # place falcon on an empty square at home rank

    # test game over by capturing the king
    assert game.make_move('d1', 'a4')  # falcon moves like a rook (backward for white)
    assert game.make_move('e8', 'e7')  # opponent moves king
    assert game.make_move('a4', 'a8')  # falcon captures king, ending game

    game_state = game.get_game_state()
    assert game_state == 'WHITE_WON', f"Expected game state to be 'WHITE_WON', got {game_state}"

    # attempt illegal self-capture
    assert not game.make_move('d2', 'd2'), "Should not be able to move to the same square"

    # pawn's initial double move and illegal subsequent double move
    game = ChessVar()
    assert game.make_move('e2', 'e4'), "Pawn initial double move should be legal"
    assert not game.make_move('e4', 'e6'), "Pawn subsequent double move should be illegal"

    # attempting to capture a piece of the same color
    game = ChessVar()
    game.make_move('e2', 'e4')
    game.make_move('e7', 'e5')
    game.make_move('d2', 'd4')
    assert not game.make_move('e4', 'd4'), "Should not be able to capture own pawn"

    # capturing the king should end game
    game = ChessVar()
    game.make_move('e2', 'e4')
    game.make_move('e7', 'e5')
    game.make_move('f1', 'c4')
    game.make_move('d7', 'd6')
    assert game.make_move('c4', 'f7'), "Capturing the king should be legal"
    assert game.get_game_state() == 'WHITE_WON', "Game state should be 'WHITE_WON' after king is captured"

    # turn switching logic
    game = ChessVar()
    assert game.make_move('e2', 'e4'), "White's first move should be legal"
    assert not game.make_move('e4', 'e5'), "White should not be able to move twice in a row"

    print("All tests passed.")


# call test function
if __name__ == '__main__':
    test_chess_var()
