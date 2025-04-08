"""
Module: SearchToolBox
Purpose: Implements the AI agent for Checkers using the Minimax algorithm with Alpha-Beta Pruning.
"""

import math
from GameBoard import GameBoard

class CheckersAI:
    def __init__(self, GameInstance):
        """Initialize the AI agent with the given GameBoard instance."""
        self.GameInstance = GameInstance
        # Counters for analytics:
        self.NumberNodesExpanded = 0
        self.NumberNodesPruned = 0
        self.MaxRecursionDepth = 0  # Track maximum recursion depth reached
        self.LastMoveOrdering = ""  # Store summary of last move ordering

    def Minimax(self, State, Depth, Alpha, Beta, IsMaximizing, CurrentDepth=0):
        """
        Minimax algorithm with Alpha-Beta Pruning.
        Returns a tuple: (EvaluationScore, BestMove)
        Also updates self.MaxRecursionDepth with the maximum recursion depth reached.
        """
        # Update maximum recursion depth (proxy for space complexity)
        self.MaxRecursionDepth = max(self.MaxRecursionDepth, CurrentDepth)

        if Depth == 0 or self.IsTerminal(State):
            return self.Evaluate(State), None

        BestMove = None
        if IsMaximizing:
            MaxEval = -math.inf
            Moves = self.GetPossibleMoves(State, 'B')
            # Order moves: for maximizing, sort by heuristic descending.
            if Moves:
                Moves = sorted(Moves, key=lambda move: self.Evaluate(self.ApplyMove(State, move)), reverse=True)
                # Store ordering summary (first 3 moves) as a string.
                self.LastMoveOrdering = "Max Order (first 3): " + ", ".join(str(move) for move in Moves[:3])
                print("Maximizing move ordering (first 3):", Moves[:3])
            else:
                Moves = []
            for Move in Moves:
                self.NumberNodesExpanded += 1
                Eval, _ = self.Minimax(self.ApplyMove(State, Move), Depth - 1, Alpha, Beta, False, CurrentDepth + 1)
                if Eval > MaxEval:
                    MaxEval = Eval
                    BestMove = Move
                Alpha = max(Alpha, Eval)
                if Beta <= Alpha:
                    self.NumberNodesPruned += 1
                    break
            return MaxEval, BestMove
        else:
            MinEval = math.inf
            Moves = self.GetPossibleMoves(State, 'W')
            # Order moves: for minimizing, sort by heuristic ascending.
            if Moves:
                Moves = sorted(Moves, key=lambda move: self.Evaluate(self.ApplyMove(State, move)))
                self.LastMoveOrdering = "Min Order (first 3): " + ", ".join(str(move) for move in Moves[:3])
                print("Minimizing move ordering (first 3):", Moves[:3])
            else:
                Moves = []
            for Move in Moves:
                self.NumberNodesExpanded += 1
                Eval, _ = self.Minimax(self.ApplyMove(State, Move), Depth - 1, Alpha, Beta, True, CurrentDepth + 1)
                if Eval < MinEval:
                    MinEval = Eval
                    BestMove = Move
                Beta = min(Beta, Eval)
                if Beta <= Alpha:
                    self.NumberNodesPruned += 1
                    break
            return MinEval, BestMove

    def IsTerminal(self, State):
        """Return True if the game is over (one side has no pieces left)."""
        if not isinstance(State, list):
            return True
        WhiteExists = any(Cell in ('W', 'WK') for Row in State for Cell in Row)
        BlackExists = any(Cell in ('B', 'BK') for Row in State for Cell in Row)
        return not (WhiteExists and BlackExists)

    def Evaluate(self, State):
        """
        Evaluation function that calculates a score based on piece count.
        Kings are weighted more heavily.
        """
        Value = 0
        for Row in State:
            for Cell in Row:
                if Cell == 'W':
                    Value -= 1
                elif Cell == 'B':
                    Value += 1
                elif Cell == 'WK':
                    Value -= 1.5
                elif Cell == 'BK':
                    Value += 1.5
        return Value

    def GetPossibleMoves(self, State, Player):
        """
        Generate all legal moves for the given Player.
        Returns moves as tuples:
          (StartingMoveLocationRow, StartingMoveLocationCol, TargetingMoveLocationRow, TargetingMoveLocationCol)
        Capture moves (jumps) are mandatory.
        """
        Moves = []
        JumpMoves = []
        for Row in range(8):
            for Col in range(8):
                Piece = State[Row][Col]
                if Piece == Player or (len(Piece) == 2 and Piece.endswith("K") and Piece[0] == Player):
                    if len(Piece) == 2 and Piece.endswith("K"):
                        NormalDirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                        JumpDirs = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
                    else:
                        if Player == 'B':
                            NormalDirs = [(1, -1), (1, 1)]
                            JumpDirs = [(2, -2), (2, 2)]
                        else:  # Player == 'W'
                            NormalDirs = [(-1, -1), (-1, 1)]
                            JumpDirs = [(-2, -2), (-2, 2)]
                    
                    for dR, dC in NormalDirs:
                        NewRow = Row + dR
                        NewCol = Col + dC
                        if 0 <= NewRow < 8 and 0 <= NewCol < 8 and State[NewRow][NewCol] == '.':
                            Moves.append((Row, Col, NewRow, NewCol))
                    for dR, dC in JumpDirs:
                        NewRow = Row + dR
                        NewCol = Col + dC
                        MidRow = Row + dR // 2
                        MidCol = Col + dC // 2
                        if 0 <= NewRow < 8 and 0 <= NewCol < 8 and State[NewRow][NewCol] == '.':
                            MidPiece = State[MidRow][MidCol]
                            if MidPiece != '.' and MidPiece[0] != Player:
                                JumpMoves.append((Row, Col, NewRow, NewCol))
        # If any capture moves exist, return those (they are mandatory).
        if JumpMoves:
            return JumpMoves
        return Moves

    def ApplyMove(self, State, Move):
        """
        Return a new board state after applying the given Move.
        Handles capturing (removes jumped piece) and king promotion.
        """
        StartingMoveLocationRow, StartingMoveLocationCol, TargetingMoveLocationRow, TargetingMoveLocationCol = Move
        NewState = [Row[:] for Row in State]
        Piece = NewState[StartingMoveLocationRow][StartingMoveLocationCol]
        NewState[TargetingMoveLocationRow][TargetingMoveLocationCol] = Piece
        NewState[StartingMoveLocationRow][StartingMoveLocationCol] = '.'
        if abs(TargetingMoveLocationRow - StartingMoveLocationRow) == 2:
            MidRow = (StartingMoveLocationRow + TargetingMoveLocationRow) // 2
            MidCol = (StartingMoveLocationCol + TargetingMoveLocationCol) // 2
            NewState[MidRow][MidCol] = '.'
        if Piece == 'B' and TargetingMoveLocationRow == 7:
            NewState[TargetingMoveLocationRow][TargetingMoveLocationCol] = 'BK'
        elif Piece == 'W' and TargetingMoveLocationRow == 0:
            NewState[TargetingMoveLocationRow][TargetingMoveLocationCol] = 'WK'
        return NewState
