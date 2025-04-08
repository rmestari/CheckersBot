"""
Module: CheckersGUI
Purpose: Implements a Tkinter-based graphical interface for the Checkers game.
         Displays the board, highlights kings with a "K" mark, processes mouse clicks,
         and shows live cumulative analytics including move ordering details.
         Also serves as the main entry point.
"""

import tkinter as tk
from PlayingTheGame import PlayCheckers

class CheckersGUI:
    def __init__(self, Master, GameSession):
        self.Master = Master
        self.GameSession = GameSession  
        self.Canvas = tk.Canvas(Master, width=400, height=400)
        self.Canvas.pack()
        # A label to display status: piece counts, win messages, live analytics, and move ordering details.
        self.StatusLabel = tk.Label(Master, text="Game in progress", font=("Arial", 14))
        self.StatusLabel.pack(pady=10)
        self.SelectedPiece = None
        self.DrawBoard()
        self.Canvas.bind("<Button-1>", self.OnClick)

    def DrawBoard(self):
        """Draw the checkers board and pieces, highlighting kings with a red 'K'."""
        self.Canvas.delete("all")
        for Row in range(8):
            for Col in range(8):
                Color = "white" if (Row + Col) % 2 == 0 else "gray"
                self.Canvas.create_rectangle(Col * 50, Row * 50, (Col + 1) * 50, (Row + 1) * 50, fill=Color)
                Piece = self.GameSession.Game.Board[Row][Col]
                if Piece in ('W', 'B', 'WK', 'BK'):
                    PieceColor = "white" if Piece[0] == 'W' else "black"
                    X1 = Col * 50 + 10
                    Y1 = Row * 50 + 10
                    X2 = (Col + 1) * 50 - 10
                    Y2 = (Row + 1) * 50 - 10
                    self.Canvas.create_oval(X1, Y1, X2, Y2, fill=PieceColor)
                    # If piece is a king, add a "K" mark.
                    if len(Piece) == 2 and Piece.endswith("K"):
                        self.Canvas.create_text((X1 + X2) // 2, (Y1 + Y2) // 2,
                                                text="K", font=("Arial", 16), fill="red")
        self.UpdateStatus()

    def UpdateStatus(self):
        """
        Update the status label to show current piece counts, win messages,
        live cumulative analytics, and the last move ordering details.
        """
        Board = self.GameSession.Game.Board
        WhitePieces = sum(Row.count('W') + Row.count('WK') for Row in Board)
        BlackPieces = sum(Row.count('B') + Row.count('BK') for Row in Board)
        StatusText = f"White: {WhitePieces} pieces   Black: {BlackPieces} pieces"
        if WhitePieces == 0:
            StatusText += " | Black wins!"
        elif BlackPieces == 0:
            StatusText += " | White wins!"
        # Retrieve cumulative analytics directly from the game session.
        stats = self.GameSession.GenerateReport()
        # Compute cumulative ordering gain: percentage of pruned nodes relative to expanded nodes.
        ordering_gain = 0
        if stats.get("States Explored", 0) > 0:
            ordering_gain = (stats.get("Pruned States", 0) / stats.get("States Explored", 0)) * 100
        AnalyticsText = (
            f"\nMoves: {stats['Total Moves']}   "
            f"Expanded: {stats['States Explored']}   "
            f"Pruned: {stats['Pruned States']}   "
            f"Avg AI Move Time: {stats['Average AI Move Time']:.3f}s   "
            f"Ordering Gain: {ordering_gain:.1f}%"
        )
        # Retrieve the last move ordering details from the AI.
        last_ordering = getattr(self.GameSession.AI, "LastMoveOrdering", "")
        self.StatusLabel.config(text=StatusText + AnalyticsText + "\n" + last_ordering)

    def OnClick(self, Event):
        """Handle mouse clicks for piece selection and move execution."""
        Row = Event.y // 50
        Col = Event.x // 50
        if self.SelectedPiece is None:
            # Select the piece if it belongs to the human (White).
            if self.GameSession.Game.Board[Row][Col] in ('W', 'WK'):
                self.SelectedPiece = (Row, Col)
        else:
            self.MovePiece(Row, Col)

    def MovePiece(self, NewRow, NewCol):
        """Execute the move from the selected piece to the target square."""
        StartingMoveLocationRow, StartingMoveLocationCol = self.SelectedPiece
        if self.GameSession.HumanMove(StartingMoveLocationRow, StartingMoveLocationCol, NewRow, NewCol):
            self.SelectedPiece = None
            self.DrawBoard()
            if "wins" not in self.StatusLabel.cget("text"):
                self.Master.after(1000, self.AIMove)
        else:
            # Invalid move: deselect the piece.
            self.SelectedPiece = None

    def AIMove(self):
        """Trigger the AI move and update the board."""
        self.GameSession.AIMove()
        self.DrawBoard()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Checkers Game")
    GameSession = PlayCheckers()
    gui = CheckersGUI(root, GameSession)
    root.mainloop()
