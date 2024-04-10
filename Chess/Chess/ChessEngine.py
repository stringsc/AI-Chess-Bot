# Responsible for storing information about the current state of a chess game.
# Also, responsible for determining valid moves at the current state. Will also keep a move log"

class GameState():
    def __init__(self):
        # Board is an 8x8 2D List, each element of the list has 2 characters.
        # The first character represents the color of the piece, 'b' or 'w'.
        # The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N', 'P'.
        # "--" represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enPassantPossible = () # square for the square where enpassant capture is possible
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]


    # Takes a Move as a parameter and executes it 
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # log the move so we can undo it later or maybe display the log
        self.whiteToMove = not self.whiteToMove # swap players

        # Update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        
        #enpassant move
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # 2 square pawn advance
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.endCol)
        else:
            self.enPassantPossible = ()
        #enpassant capture
        if move.enPassant:
            self.board[move.startRow][move.endCol] = '--'

        # Pawn Promotion
        if move.isPawnPromotion:
            promotedPiece = input("Enter the piece you want to promote to (Q, R, B, N): ")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

        # Castle move
        updateCastleRights(move, self)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))




    # Undo the last move made
    def undoMove(self):
        if len(self.moveLog) != 0: # make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # switch turns back

            # Update the king's location if moved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            
            # Undo enpassant move
            if move.enPassant:
                self.board[move.endRow][move.endCol] = '--' #removes pawn in wrong square
                self.board[move.startRow][move.endCol] = move.pieceCaptured # puts the captured pawn back
                self.enPassantPossible = (move.endRow, move.endCol) #allows enpassant to occur next move
            # Undo a 2 square pawn advance -> makes enPassantPossible = () again
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()

            # Undo castling rights
            self.castleRightsLog.pop() # get rid of the new castle rights from the move we are undoing
            self.currentCastlingRight = CastleRights(self.castleRightsLog[-1].wks, self.castleRightsLog[-1].bks,
                                                     self.castleRightsLog[-1].wqs, self.castleRightsLog[-1].bqs)
    
            


    # Update the castle rights given the move
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: 
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

    # All moves considering checks
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck: # if in check, we must move the king
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves() 
                # to get out of check, we must block the check or move the king
                check = self.checks[0] # check information
                checkRow = check[0] # row of the checking piece
                checkCol = check[1] # col of the checking piece
                pieceChecking = self.board[checkRow][checkCol]
                #if knight, must capture knight or move king, other pieces can be blocked
                validSquares = []
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: # once you reach the checking piece, you can capture it
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else: # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: # not in check so all moves are fine
            moves = self.getAllPossibleMoves()
        return moves   


    
    # All moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0] 
                piece = self.board[r][c][1]
                if (self.whiteToMove and turn == 'w') or (not self.whiteToMove and turn == 'b'):
                    self.moveFunctions[piece](r, c, moves) # calls the appropriate move function based on the piece type
        return moves
    
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break


        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board)) # move one square up
                    if r == 6 and self.board[r-2][c] == "--": # move two squares up
                        moves.append(Move((r, c), (r-2, c), self.board))
                         
            if c-1 >= 0 and self.board[r-1][c-1][0] == 'b': # capture to the left
                if not piecePinned or pinDirection == (-1, -1):
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.isEmpassantMove:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove = True))

            if c+1 < 8 and self.board[r-1][c+1][0] == 'b': # capture to the right
                if not piecePinned or pinDirection == (-1, 1):
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else:
            if self.board[r+1][c] == "--": 
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))

            if c-1 >= 0 and self.board[r+1][c-1][0] == 'w':
                if not piecePinned or pinDirection == (1, -1):
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 < 8 and self.board[r+1][c+1][0] == 'w':
                if not piecePinned or pinDirection == (1, 1):
                    moves.append(Move((r, c), (r+1, c+1), self.board))

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != enemyColor: # not an ally piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))

                
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": # empty space
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # friendly piece
                            break
                else: # off board
                    break
    
    # Queen moves are just Rook and Bishop moves combined
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    # King moves are a bit tricky
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # not an ally piece
                    # place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    if allyColor == 'w': 
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
    
    def checkForPinsAndChecks(self):
        pins = []   
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        directions = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == (): # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: # 2nd allied piece, so no piece can block, so it's not pinned
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities here in this complex conditional
                        # 1. Orthogonally away from king and piece is a rook
                        # 2. Diagonally away from king and piece is a bishop
                        # 3. 1 square away diagonally from king and piece is a pawn
                        # 4. Any direction and piece is a queen
                        # 5. Any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: # enemy piece not applying check
                            break
                else: # off board
                    break

        # Check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks
    
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

                
class Move():

    # Maps keys to values
    # key : value

    # (row, col) : piece
    # (0, 0) : "bR"
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        
        # Pawn enpassant
        self.enPassant = enPassant
        if enPassant:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp' #capturing the pawn
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        chessdict = {'bR':'R', 'wR':'R', 'bB':'B', 
                     'wB':'B', 'bN':'N', 'wN':'N', 
                     'bQ':'Q', 'wQ':'Q', 'wK':'K', 
                     'bK':'K', '--':''}
        notation = ''
        if self.pieceCaptured == '--' and (self.pieceMoved != 'wp' and self.pieceMoved != 'bp'):
            ans = chessdict[self.pieceMoved]
            notation = ans + self.getRankFile(self.endRow, self.endCol)
        elif self.pieceCaptured == '--' and (self.pieceMoved == 'wp' or self.pieceMoved == 'bp'):
            notation = self.getRankFile(self.endRow, self.endCol) 
        elif self.pieceCaptured != '--':
            if self.pieceMoved != 'wp' and self.pieceMoved != 'bp':
                ans = chessdict[self.pieceMoved]
                notation = ans + 'X' + self.getRankFile(self.endRow, self.endCol)
            else:
                notation = self.pieceMoved + 'X' + self.getRankFile(self.endRow, self.endCol)
        return notation
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]