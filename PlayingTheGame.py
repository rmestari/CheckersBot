"""
Module: PlayingTheGame
Purpose: Controls the game flow between the human user and the AI agent.
         Handles user input, enforces chain-captures, checks win conditions,
         and integrates analytics tracking for each move (integrated directly into this class).
"""

import time
from GameBoard import GameBoard
from SearchToolBox import CheckersAI

class PlayCheckers:
    def __init__(self):
        """Initialize the game session with integrated analytics tracking."""
        self.Game = GameBoard()
        self.AI = CheckersAI(self.Game)
        self.CurrentPlayer = "human"  # Human (White) moves first.
        # Integrated analytics tracking variables:
        self.MovesMade = 0
        self.StatesExplored = 0
        self.PrunedStates = 0
        self.TimeTaken = []  # List of time durations for AI moves

    # Analytics tracking methods:
    def TrackMove(self):
        """Increment the count of moves made."""
        self.MovesMade += 1

    def TrackSearch(self, Expanded, Pruned):
        """Record the number of search states expanded and pruned for an AI move."""
        self.StatesExplored += Expanded
        self.PrunedStates += Pruned

    def TrackTime(self, StartTime, EndTime):
        """Record the time taken for an AI move."""
        self.TimeTaken.append(EndTime - StartTime)

    def GenerateReport(self):
        """Return a dictionary with cumulative performance analytics."""
        AverageTime = (sum(self.TimeTaken) / len(self.TimeTaken)) if self.TimeTaken else 0
        return {
            "Total Moves": self.MovesMade,
            "States Explored": self.StatesExplored,
            "Pruned States": self.PrunedStates,
            "Average AI Move Time": AverageTime
        }

    # Game flow methods:
    def HumanMove(self, StartingMoveLocationRow, StartingMoveLocationCol,
                  TargetingMoveLocationRow, TargetingMoveLocationCol):
        """
        Execute the human move.
        If the move is a capture and additional jumps are available from the landing square,
        the same piece remains selected for a chain capture.
        """
        if self.Game.MovePiece(StartingMoveLocationRow, StartingMoveLocationCol,
                               TargetingMoveLocationRow, TargetingMoveLocationCol, 'W'):
            self.TrackMove()  # Track human move
            # Check for chain jump; if available, do not switch turn.
            if abs(TargetingMoveLocationRow - StartingMoveLocationRow) == 2 and \
               self.Game.CanCaptureFrom(TargetingMoveLocationRow, TargetingMoveLocationCol, 'W'):
                print("Chain jump available. Continue moving the same piece.")
                return True  # Remain on human turn.
            if self.CheckWinner():
                return True
            self.CurrentPlayer = "ai"
            time.sleep(1)  # Simulate AI thinking delay.
            self.AIMove()
            return True
        else:
            print("Invalid human move. Please try again.")
            return False

    def AIMove(self):
        """Have the AI select and execute its move, updating analytics and reporting move ordering gain."""
        if self.CurrentPlayer == "ai":
            start_time = time.time()
            _, BestMove = self.AI.Minimax(self.Game.Board, Depth=3, 
                                          Alpha=-float("inf"), Beta=float("inf"), 
                                          IsMaximizing=True)
            end_time = time.time()
            self.TrackMove()  # Count the AI move
            self.TrackSearch(self.AI.NumberNodesExpanded, self.AI.NumberNodesPruned)
            self.TrackTime(start_time, end_time)
            
            # Compute ordering gain: percentage of nodes pruned out of nodes expanded.
            ordering_gain = 0
            if self.AI.NumberNodesExpanded > 0:
                ordering_gain = (self.AI.NumberNodesPruned / self.AI.NumberNodesExpanded) * 100
            
            print(f"AI Move Analytics → Expanded: {self.AI.NumberNodesExpanded}, "
                  f"Pruned: {self.AI.NumberNodesPruned}, "
                  f"Time: {end_time - start_time:.3f} sec, "
                  f"MaxRecursionDepth: {self.AI.MaxRecursionDepth}, "
                  f"Ordering Gain: {ordering_gain:.1f}%")
            print("Move ordering used:", self.AI.LastMoveOrdering)
            
            if BestMove:
                (StartingMoveLocationRow, StartingMoveLocationCol,
                 TargetingMoveLocationRow, TargetingMoveLocationCol) = BestMove
                self.Game.MovePiece(StartingMoveLocationRow, StartingMoveLocationCol,
                                    TargetingMoveLocationRow, TargetingMoveLocationCol, 'B')
            if self.CheckWinner():
                return
            self.CurrentPlayer = "human"

    def CheckWinner(self):
        """
        Check if the game is over.
        Returns True if one side has no pieces left.
        """
        Board = self.Game.Board
        WhiteExists = any(Cell in ('W', 'WK') for Row in Board for Cell in Row)
        BlackExists = any(Cell in ('B', 'BK') for Row in Board for Cell in Row)
        if not WhiteExists:
            print("Black wins!")
            return True
        elif not BlackExists:
            print("White wins!")
            return True
        return False

    def DisplayBoard(self):
        """Display the current board state to the console."""
        for Row in self.Game.Board:
            print(" ".join(Row))
        print("\n")
