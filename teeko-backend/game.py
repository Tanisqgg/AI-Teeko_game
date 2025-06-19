import copy
import random


class TeekoPlayer:
    """ An object representation for an AI game player for the game Teeko.
    """
    board = [[' ' for j in range(5)] for i in range(5)]
    pieces = ['b', 'r']

    def __init__(self):
        """ Initializes a TeekoPlayer object by randomly selecting red or black as its
        piece color.
        """
        self.my_piece = random.choice(self.pieces)
        self.opp = self.pieces[0] if self.my_piece == self.pieces[1] else self.pieces[1]

    def run_challenge_test(self):
        """ Set to True if you would like to run gradescope against the challenge AI!
        Leave as False if you would like to run the gradescope tests faster for debugging.
        You can still get full credit with this set to False
        """
        return True

    def succ(self, state):
        """
        Drop phase (<8 pieces): add piece; move phase: slide one piece.
        Return list of successors.
        """

        successors = []
        # count the filled spaces. non-empty
        non_empty = 0
        for row in state:
            for cell in row:
                if cell != ' ':
                    non_empty += 1

        drop_phase = non_empty < 8

        if drop_phase:
            for r in range(5):
                for c in range(5):
                    if state[r][c] == ' ':
                        new_state = copy.deepcopy(state)
                        new_state[r][c] = self.my_piece
                        successors.append(([(r, c)], new_state))
        else:
            # move phase. possible relocation
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for r in range(5):
                for c in range(5):
                    if state[r][c] == self.my_piece:
                        for dr, dc in directions:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < 5 and 0 <= nc < 5 and state[nr][nc] == ' ':
                                new_state = copy.deepcopy(state)
                                new_state[r][c] = ' '
                                new_state[nr][nc] = self.my_piece
                                successors.append(([(nr, nc), (r, c)], new_state))

        return successors


    def make_move(self, state):
        """ Selects a (row, col) space for the next move. You may assume that whenever
        this function is called, it is this player's turn to move.

        Args:
            state (list of lists): should be the current state of the game as saved in
                this TeekoPlayer object. Note that this is NOT assumed to be a copy of
                the game state and should NOT be modified within this method (use
                place_piece() instead). Any modifications (e.g. to generate successors)
                should be done on a deep copy of the state.

                In the "drop phase", the state will contain less than 8 elements which
                are not ' ' (a single space character).

        Return:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

        Note that without drop phase behavior, the AI will just keep placing new markers
            and will eventually take over the board. This is not a valid strategy and
            will earn you no points.
        """

        best_score = -float('inf')
        best_move = None
        depth = 3
        for move, s in self.succ(state):
            score = self.min_value(s, depth - 1)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def heuristic_game_value(self, state):
        # will hold the cords for r/c/d
        score = 0.0
        lines = []
        for r in range(5):
            for c in range(2):
                lines.append([(r, c + i) for i in range(4)]) # horizontal
                lines.append([(c + i, r) for i in range(4)]) # vertical

        # diagonals
        for r in range(2):
            for c in range(2):
                lines.append([(r + i, c + i) for i in range(4)]) # \
                lines.append([(r + 3 - i, c + i) for i in range(4)]) # /

        squares = []
        for r in range(4):
            for c in range(4):
                squares.append([(r,c), (r+1,c), (r,c+1), (r+1,c+1)])

        for line in lines:
            my_count = opp_count = 0
            for r, c in line:
                if state[r][c] == self.my_piece:
                    my_count += 1
                elif state[r][c] == self.opp:
                    opp_count += 1
            if my_count > 0 and opp_count == 0:
                score += (my_count / 4)
            elif opp_count > 0 and my_count == 0:
                score -= (opp_count / 4)
        return max(-1.0, min(1.0, score))

    def max_value(self, state, depth):
        """
        Return the minimax value at remaining depth.
        If depth==0, return game_value or heuristic.
        """
        v = self.game_value(state)
        if v != 0 or depth == 0:
            return v or self.heuristic_game_value(state)
        v = -float('inf')
        for move, s in self.succ(state):
            v = max(v, self.min_value(s, depth - 1))
        return v

    def min_value(self, state, depth):
        """
        Return the minimax min‐node value at remaining depth.
        If depth==0, return game_value or heuristic.
        """
        v = self.game_value(state)
        if v != 0 or depth == 0:
            return v or self.heuristic_game_value(state)
        v = float('inf')
        for move, s in self.succ(state):
            v = min(v, self.max_value(s, depth - 1))
        return v

    def opponent_move(self, move):
        """ Validates the opponent's next move against the internal board representation.
        You don't need to touch this code.

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.
        """
        # validate input
        if len(move) > 1:
            source_row = move[1][0]
            source_col = move[1][1]
            if source_row != None and self.board[source_row][source_col] != self.opp:
                self.print_board()
                print(move)
                raise Exception("You don't have a piece there!")
            if abs(source_row - move[0][0]) > 1 or abs(source_col - move[0][1]) > 1:
                self.print_board()
                print(move)
                raise Exception('Illegal move: Can only move to an adjacent space')
        if self.board[move[0][0]][move[0][1]] != ' ':
            raise Exception("Illegal move detected")
        # make move
        self.place_piece(move, self.opp)

    def place_piece(self, move, piece):
        """ Modifies the board representation using the specified move and piece

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

                This argument is assumed to have been validated before this method
                is called.
            piece (str): the piece ('b' or 'r') to place on the board
        """
        if len(move) > 1:
            self.board[move[1][0]][move[1][1]] = ' '
        self.board[move[0][0]][move[0][1]] = piece

    def print_board(self):
        """ Formatted printing for the board """
        for row in range(len(self.board)):
            line = str(row)+": "
            for cell in self.board[row]:
                line += cell + " "
            print(line)
        print("   A B C D E")

    def game_value(self, state):
        """ Checks the current board status for a win condition

        Args:
        state (list of lists): either the current state of the game as saved in
            this TeekoPlayer object, or a generated successor state.

        Returns:
            int: 1 if this TeekoPlayer wins, -1 if the opponent wins, 0 if no winner
        """
        # check horizontal wins
        for row in state:
            for i in range(2):
                if row[i] != ' ' and row[i] == row[i+1] == row[i+2] == row[i+3]:
                    return 1 if row[i]==self.my_piece else -1

        # check vertical wins
        for col in range(5):
            for i in range(2):
                if state[i][col] != ' ' and state[i][col] == state[i+1][col] == state[i+2][col] == state[i+3][col]:
                    return 1 if state[i][col]==self.my_piece else -1

        # check \ diagonal wins
        for r in range(2):
            for c in range(2):
                if state[r][c] != ' ' and state[r][c] == state[r + 1][c + 1] == state[r + 2][c + 2] == state[r + 3][
                    c + 3]:
                    return 1 if state[r][c] == self.my_piece else -1
        # check / diagonal wins
        for r in range(3, 5):
            for c in range(2):
                if state[r][c] != ' ' and state[r][c] == state[r - 1][c + 1] == state[r - 2][c + 2] == state[r - 3][
                    c + 3]:
                    return 1 if state[r][c] == self.my_piece else -1
        # check box wins
        for r in range(4):
            for c in range(4):
                if state[r][c] != ' ' and state[r][c] == state[r][c + 1] == state[r + 1][c] == state[r + 1][c + 1]:
                    return 1 if state[r][c] == self.my_piece else -1

        return 0 # no winner yet

############################################################################
#
# THE FOLLOWING CODE IS FOR SAMPLE GAMEPLAY ONLY
#
############################################################################
def main():
    print('Hello, this is Samaritan')
    ai = TeekoPlayer()
    piece_count = 0
    turn = 0

    # drop phase
    while piece_count < 8 and ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved at "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                player_move = input("Move (e.g. B3): ")
                while player_move[0] not in "ABCDE" or player_move[1] not in "01234":
                    player_move = input("Move (e.g. B3): ")
                try:
                    ai.opponent_move([(int(player_move[1]), ord(player_move[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        piece_count += 1
        turn += 1
        turn %= 2

    # move phase - can't have a winner until all 8 pieces are on the board
    while ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved from "+chr(move[1][1]+ord("A"))+str(move[1][0]))
            print("  to "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                move_from = input("Move from (e.g. B3): ")
                while move_from[0] not in "ABCDE" or move_from[1] not in "01234":
                    move_from = input("Move from (e.g. B3): ")
                move_to = input("Move to (e.g. B3): ")
                while move_to[0] not in "ABCDE" or move_to[1] not in "01234":
                    move_to = input("Move to (e.g. B3): ")
                try:
                    ai.opponent_move([(int(move_to[1]), ord(move_to[0])-ord("A")),
                                    (int(move_from[1]), ord(move_from[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        turn += 1
        turn %= 2

    ai.print_board()
    if ai.game_value(ai.board) == 1:
        print("AI wins! Game over.")
    else:
        print("You win! Game over.")


if __name__ == "__main__":
    main()