class MorrisGameEngine:
    def __init__(self, board_state=None, pieces_in_hand=(9, 9), ancestor_state=None):
        self.board = board_state if board_state else ['.' for _ in range(24)]
        self.player1_remaining, self.player2_remaining = pieces_in_hand
        self.ancestor = ancestor_state
        
        self._connections = {
            0: [1, 9], 1: [0, 2, 4], 2: [1, 14], 
            3: [4, 10], 4: [1, 3, 5, 7], 5: [4, 13],
            6: [7, 11], 7: [4, 6, 8], 8: [7, 12],
            9: [0, 10, 21], 10: [3, 9, 11, 18], 11: [6, 10, 15],
            12: [8, 13, 17], 13: [5, 12, 14, 20], 14: [2, 13, 23],
            15: [11, 16], 16: [15, 17, 19], 17: [12, 16],
            18: [10, 19], 19: [16, 18, 20, 22], 20: [13, 19],
            21: [9, 22], 22: [19, 21, 23], 23: [14, 22]
        }
        
        self._winning_rows = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [9, 10, 11], [12, 13, 14], [15, 16, 17],
            [18, 19, 20], [21, 22, 23],

            [0, 9, 21], [3, 10, 18], [6, 11, 15],
            [1, 4, 7], [16, 19, 22], [8, 12, 17],
            [5, 13, 20], [2, 14, 23]
        ]

    def is_position_empty(self, pos):
        return self.board[pos] == '.'
    
    def available_positions(self):
        return [pos for pos, value in enumerate(self.board) if value == '.']
    
    def player_positions(self, player):
        return [pos for pos, value in enumerate(self.board) if value == player]
    
    def available_moves(self, player):
        result = []
        
        for start_pos in self.player_positions(player):
            for end_pos in self._connections[start_pos]:
                if self.is_position_empty(end_pos):
                    result.append((start_pos, end_pos))
        
        
        return result
    
    def forms_mill(self, position, player):
        for row in self._winning_rows:
            if position in row and all(self.board[pos] == player for pos in row):
                return True
        return False
    
    def removable_pieces(self, opponent):
        opponent_positions = self.player_positions(opponent)
        
        free_pieces = []
        for pos in opponent_positions:
            if not any(all(self.board[p] == opponent for p in row) 
                       for row in self._winning_rows if pos in row):
                free_pieces.append(pos)
        
        return free_pieces if free_pieces else opponent_positions
    
    def add_piece(self, position, player):
        """Place a new piece on the board during placement phase."""
        new_board = self.board.copy()
        new_board[position] = player
        
        new_remaining1, new_remaining2 = self.player1_remaining, self.player2_remaining
        if player == 'x':
            new_remaining1 -= 1
        else:
            new_remaining2 -= 1
        
        return MorrisGameEngine(new_board, (new_remaining1, new_remaining2), self)
    
    def relocate_piece(self, from_pos, to_pos, player):
        new_board = self.board.copy()
        new_board[from_pos] = '.'
        new_board[to_pos] = player
        return MorrisGameEngine(new_board, 
                               (self.player1_remaining, self.player2_remaining), 
                               self)
    
    def capture_piece(self, position, state=None):
        state_to_modify = state if state else self
        new_board = state_to_modify.board.copy()
        new_board[position] = '.'
        return MorrisGameEngine(new_board, 
                               (state_to_modify.player1_remaining, 
                                state_to_modify.player2_remaining), 
                               self.ancestor)
    
    def calculate_score(self):
        if self.player1_remaining > 0 or self.player2_remaining > 0:
            return self._evaluate_placement_stage()
        else:
            return self._evaluate_movement_stage()
    
    def _evaluate_placement_stage(self):
        player1_count = self.board.count('x')
        player2_count = self.board.count('o')
        
        player1_mills = self._count_completed_mills('x')
        player2_mills = self._count_completed_mills('o')
        
        player1_potential = self._count_potential_mills('x')
        player2_potential = self._count_potential_mills('o')
        
        player1_options = len(self.available_positions()) if self.player1_remaining > 0 else 0
        player2_options = len(self.available_positions()) if self.player2_remaining > 0 else 0
        
        return (
            4 * (player1_count - player2_count) +
            6 * (player1_mills - player2_mills) +
            3 * (player1_potential - player2_potential) +
            (player1_options - player2_options)
        )
    
    def _evaluate_movement_stage(self):
        player1_count = self.board.count('x')
        player2_count = self.board.count('o')
        
        if player1_count < 3:
            return -1000 
        if player2_count < 3:
            return 1000  
        
        player1_mills = self._count_completed_mills('x')
        player2_mills = self._count_completed_mills('o')
        
        player1_mobility = len(self.available_moves('x'))
        player2_mobility = len(self.available_moves('o'))
        
        if player1_mobility == 0:
            return -1000
        if player2_mobility == 0:
            return 1000
        
        return (
            4 * (player1_count - player2_count) +
            6 * (player1_mills - player2_mills) +
            (player1_mobility - player2_mobility)
        )
    
    def _count_completed_mills(self, player):
        mill_count = 0
        counted = set()
        
        for row in self._winning_rows:
            row_key = tuple(sorted(row))
            if row_key not in counted and all(self.board[pos] == player for pos in row):
                mill_count += 1
                counted.add(row_key)
        
        return mill_count
    
    def _count_potential_mills(self, player):
        potential = 0
        
        for row in self._winning_rows:
            player_pieces = sum(1 for pos in row if self.board[pos] == player)
            empty_spots = sum(1 for pos in row if self.board[pos] == '.')
            
            if player_pieces == 2 and empty_spots == 1:
                potential += 1
        
        return potential
    
    def generate_successor_states(self, player):
        result = []
        opponent = 'o' if player == 'x' else 'x'
        
        if self.board.count(player) <= 2:
            return result
        
        if (player == 'x' and self.player1_remaining > 0) or (player == 'o' and self.player2_remaining > 0):
            for pos in self.available_positions():
                new_state = self.add_piece(pos, player)
                
                if new_state.forms_mill(pos, player):
                    for remove_pos in new_state.removable_pieces(opponent):
                        result.append(new_state.capture_piece(remove_pos))
                else:
                    result.append(new_state)
                    
        else:
            for from_pos, to_pos in self.available_moves(player):
                new_state = self.relocate_piece(from_pos, to_pos, player)
                
                if new_state.forms_mill(to_pos, player):
                    for remove_pos in new_state.removable_pieces(opponent):
                        result.append(new_state.capture_piece(remove_pos))
                else:
                    result.append(new_state)
                    
        return result
    
    def search_minimax(self, depth, max_player):
        if depth == 0:
            return self.calculate_score(), self
        
        current_player = 'x' if max_player else 'o'
        next_states = self.generate_successor_states(current_player)
        
        if not next_states:
            return -1000 if max_player else 1000, self
        
        best_score = float('-inf') if max_player else float('inf')
        best_state = None
        
        for state in next_states:
            score, _ = state.search_minimax(depth - 1, not max_player)
            
            if max_player and score > best_score:
                best_score = score
                best_state = state
            elif not max_player and score < best_score:
                best_score = score
                best_state = state
                
        return best_score, best_state
    
    def search_alphabeta(self, depth, alpha, beta, max_player):
        if depth == 0:
            return self.calculate_score(), self
        
        current_player = 'x' if max_player else 'o'
        next_states = self.generate_successor_states(current_player)
        
        if not next_states:
            return -1000 if max_player else 1000, self
        
        best_state = None
        
        if max_player:
            value = float('-inf')
            for state in next_states:
                child_value, _ = state.search_alphabeta(depth - 1, alpha, beta, False)
                if child_value > value:
                    value = child_value
                    best_state = state
                alpha = max(alpha, value)
                if beta <= alpha:
                    break 
        else:
            value = float('inf')
            for state in next_states:
                child_value, _ = state.search_alphabeta(depth - 1, alpha, beta, True)
                if child_value < value:
                    value = child_value
                    best_state = state
                beta = min(beta, value)
                if beta <= alpha:
                    break  
                    
        return value, best_state
    
    def find_optimal_move(self, search_type, search_depth):
        if search_type == "MinMax":
            score, best_state = self.search_minimax(search_depth, True)
        elif search_type == "AlphaBeta":
            score, best_state = self.search_alphabeta(search_depth, float('-inf'), float('inf'), True)
        else:
            raise ValueError("Unknown search algorithm. Use 'MinMax' or 'AlphaBeta'")
        
        return best_state, score


def convert_string_to_board(input_str):
    board = list(input_str.strip())
    
    board = board[:24]  
    board.extend(['.'] * (24 - len(board))) 
    
    return board


def run_analysis(board_string, pieces_remaining, algorithm, depth):
    board = convert_string_to_board(board_string)
    
    game = MorrisGameEngine(board, pieces_remaining)
    
    best_move, score = game.find_optimal_move(algorithm, depth)

    print("Starting position:")
    print(game.display())
    print("\nBest move found:")
    print(best_move.display())
    print(f"\nEvaluated score: {score}")
    print("\nRaw board state:")
    print(''.join(best_move.board))
    
    return best_move


if __name__ == "__main__":
    sample_board = '.....o..x..oxo..x.oxo.x.'
    remaining = (0, 0)  
    search_algorithm = "AlphaBeta"
    search_depth = 5
    
    game = MorrisGameEngine(convert_string_to_board(sample_board), remaining)
    best_move, score = game.find_optimal_move(search_algorithm, search_depth)

    print("\nRaw board state:")
    print(''.join(best_move.board))