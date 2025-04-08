"""
Module: GameBoard
Purpose: Provides the board setup and methods for validating and executing moves in American Checkers.
"""

class GameBoard:
    def __init__(self):
        """Initialize the checkers board with 12 pieces per side placed on dark squares."""
        self.Board = self.CreateInitialBoard()

    def CreateInitialBoard(self):
        """Create an 8x8 board and place pieces on dark squares.
           Black pieces occupy rows 0-2; White pieces occupy rows 5-7.
        """
        Board = [['.' for _ in range(8)] for _ in range(8)]
        # Place Black pieces (they move first)
        for Row in range(3):
            for Col in range(8):
                if (Row + Col) % 2 == 1:
                    Board[Row][Col] = 'B'
        # Place White pieces
        for Row in range(5, 8):
            for Col in range(8):
                if (Row + Col) % 2 == 1:
                    Board[Row][Col] = 'W'
        return Board

    def AnyCaptureAvailable(self, Player):
        """
        Return True if any capture (jump) move is available for the specified Player.
        """
        for Row in range(8):
            for Col in range(8):
                Piece = self.Board[Row][Col]
                if Piece != '.' and Piece[0] == Player:
                    if len(Piece) == 2 and Piece.endswith("K"):
                        Directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                    else:
                        # For non-kings: Black moves downward; White moves upward.
                        Directions = [(1, -1), (1, 1)] if Player == 'B' else [(-1, -1), (-1, 1)]
                    for dR, dC in Directions:
                        TargetingMoveLocationRow = Row + 2 * dR
                        TargetingMoveLocationCol = Col + 2 * dC
                        MidRow = Row + dR
                        MidCol = Col + dC
                        if 0 <= TargetingMoveLocationRow < 8 and 0 <= TargetingMoveLocationCol < 8:
                            if self.Board[TargetingMoveLocationRow][TargetingMoveLocationCol] == '.':
                                MidPiece = self.Board[MidRow][MidCol]
                                if MidPiece != '.' and MidPiece[0] != Player:
                                    return True
        return False

    def CanCaptureFrom(self, CurrentRow, CurrentCol, Player):
        """
        Return True if the piece at (CurrentRow, CurrentCol) can perform a jump (capture).
        This helps implement chain captures.
        """
        Piece = self.Board[CurrentRow][CurrentCol]
        if Piece == '.' or Piece[0] != Player:
            return False
        if len(Piece) == 2 and Piece.endswith("K"):
            JumpDirs = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        else:
            # For non-king pieces: Black moves downward; White moves upward.
            JumpDirs = [(2, -2), (2, 2)] if Player == 'W' else [(-2, -2), (-2, 2)]
        for dR, dC in JumpDirs:
            NewRow = CurrentRow + dR
            NewCol = CurrentCol + dC
            MidRow = CurrentRow + dR // 2
            MidCol = CurrentCol + dC // 2
            if 0 <= NewRow < 8 and 0 <= NewCol < 8:
                if self.Board[NewRow][NewCol] == '.':
                    MidPiece = self.Board[MidRow][MidCol]
                    if MidPiece != '.' and MidPiece[0] != Player:
                        return True
        return False

    def IsValidMove(self, StartingMoveLocationRow, StartingMoveLocationCol,
                    TargetingMoveLocationRow, TargetingMoveLocationCol, Player):
        """
        Check if a move is valid based on American Checkers rules.
        Debug prints are included to trace the validation process.
        """
        Debug = False  # Set to True for verbose debugging.

        # Check if target is within bounds.
        if not (0 <= TargetingMoveLocationRow < 8 and 0 <= TargetingMoveLocationCol < 8):
            if Debug: print("Move rejected: destination out of bounds.")
            return False

        # Destination must be empty.
        if self.Board[TargetingMoveLocationRow][TargetingMoveLocationCol] != '.':
            if Debug: print("Move rejected: destination square is occupied.")
            return False

        Piece = self.Board[StartingMoveLocationRow][StartingMoveLocationCol]
        if Piece == '.':
            if Debug: print("Move rejected: no piece at StartingMoveLocation(%d,%d)." % (StartingMoveLocationRow, StartingMoveLocationCol))
            return False

        # Ensure the piece belongs to the Player.
        if Piece[0] != Player:
            if Debug: print("Move rejected: piece does not belong to %s." % Player)
            return False

        # Check if the piece is a king.
        IsKing = (len(Piece) == 2 and Piece.endswith("K"))
        if IsKing:
            AllowedDirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            if Debug: print("Piece is a king. Allowed directions:", AllowedDirs)
        else:
            AllowedDirs = [(1, -1), (1, 1)] if Player == 'B' else [(-1, -1), (-1, 1)]
            if Debug: print("Piece is not a king. Allowed directions:", AllowedDirs)

        dRow = TargetingMoveLocationRow - StartingMoveLocationRow
        dCol = TargetingMoveLocationCol - StartingMoveLocationCol
        MoveVector = (dRow, dCol)
        if Debug: print("Attempting move:", MoveVector)

        # Normal (non-capturing) move.
        if MoveVector in AllowedDirs:
            if self.AnyCaptureAvailable(Player):
                if Debug: print("Move rejected: a capture is available; non-capturing moves are not allowed.")
                return False
            if Debug: print("Non-capturing move accepted.")
            return True

        # Jump (capture) move: must move two squares diagonally.
        if (abs(dRow), abs(dCol)) == (2, 2):
            if not IsKing:
                AllowedJump = [(dr * 2, dc * 2) for dr, dc in AllowedDirs]
                if MoveVector not in AllowedJump:
                    if Debug: print("Move rejected: jump direction not allowed for non-king piece.")
                    return False
            MidRow = StartingMoveLocationRow + dRow // 2
            MidCol = StartingMoveLocationCol + dCol // 2
            MidPiece = self.Board[MidRow][MidCol]
            if MidPiece == '.' or MidPiece[0] == Player:
                if Debug: print("Move rejected: no opponent piece to capture.")
                return False
            if Debug: print("Capture move accepted.")
            return True

        if Debug: print("Move rejected: move pattern not recognized.")
        return False

    def MovePiece(self, StartingMoveLocationRow, StartingMoveLocationCol,
                  TargetingMoveLocationRow, TargetingMoveLocationCol, Player):
        """
        Execute a move if valid, remove any captured piece, and promote to king when needed.
        Returns True if the move is executed.
        """
        if self.IsValidMove(StartingMoveLocationRow, StartingMoveLocationCol,
                            TargetingMoveLocationRow, TargetingMoveLocationCol, Player):
            Piece = self.Board[StartingMoveLocationRow][StartingMoveLocationCol]
            self.Board[TargetingMoveLocationRow][TargetingMoveLocationCol] = Piece
            self.Board[StartingMoveLocationRow][StartingMoveLocationCol] = '.'
            # If the move is a capture, remove the captured piece.
            if abs(TargetingMoveLocationRow - StartingMoveLocationRow) == 2:
                MidRow = (StartingMoveLocationRow + TargetingMoveLocationRow) // 2
                MidCol = (StartingMoveLocationCol + TargetingMoveLocationCol) // 2
                self.Board[MidRow][MidCol] = '.'
            # Promote to king if the piece reaches the far side.
            if Piece == 'B' and TargetingMoveLocationRow == 7:
                self.Board[TargetingMoveLocationRow][TargetingMoveLocationCol] = 'BK'
                print("Black piece promoted to King at (%d,%d)" % (TargetingMoveLocationRow, TargetingMoveLocationCol))
            elif Piece == 'W' and TargetingMoveLocationRow == 0:
                self.Board[TargetingMoveLocationRow][TargetingMoveLocationCol] = 'WK'
                print("White piece promoted to King at (%d,%d)" % (TargetingMoveLocationRow, TargetingMoveLocationCol))
            return True
        return False
