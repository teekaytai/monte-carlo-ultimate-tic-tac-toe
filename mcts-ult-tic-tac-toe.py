import math
from operator import attrgetter
import random
from time import perf_counter

# Note: Least significant bit of board represents top left corner, 3 consecutive bits represent a row
EMPTY_BOARD = 0b000000000
FULL_BOARD = 0b111111111

# Convert board indices to locations
BOARD_LOCATION = ['top left', 'top', 'top right', 'left', 'centre', 'right', 'bottom left', 'bottom', 'bottom right']

# Convert bits to their indices
LOG2 = {
    0b1: 0,
    0b10: 1,
    0b100: 2,
    0b1000: 3,
    0b10000: 4,
    0b100000: 5,
    0b1000000: 6,
    0b10000000: 7,
    0b100000000: 8
}


class Game:
    __slots__ = 'my_global_board', 'opp_global_board', 'my_boards', 'opp_boards', 'board_spaces_counts', \
                'curr_board_index', 'my_turn', 'is_over', 'result', '_untried_moves'

    LINES = [0b111000000, 0b000111000, 0b000000111, 0b100100100, 0b010010010, 0b001001001, 0b100010001, 0b001010100]

    def __init__(self, my_global_board=EMPTY_BOARD, opp_global_board=EMPTY_BOARD, my_boards=None, opp_boards=None,
                 board_spaces_counts=None, curr_board_index=-1, my_turn=True, is_over=False, result=None):
        self.my_global_board = my_global_board
        self.opp_global_board = opp_global_board
        self.my_boards = my_boards or [EMPTY_BOARD] * 9
        self.opp_boards = opp_boards or [EMPTY_BOARD] * 9
        self.board_spaces_counts = board_spaces_counts or [9] * 9
        self.curr_board_index = curr_board_index
        self.my_turn = my_turn
        self.is_over = is_over
        self.result = result
        self._untried_moves = None


    def get_unvisited_game(self):
        if self.is_over:
            # Game is already over, no need to look for untried moves
            return None, None
        move = self.untried_moves.pop()
        game_clone = self.clone()
        game_clone.play_move(move)
        
        return game_clone, move


    @property
    def untried_moves(self):
        if self._untried_moves is None:
            self._untried_moves = self.get_possible_moves()

        return self._untried_moves


    @untried_moves.setter
    def untried_moves(self, untried_moves):
        self._untried_moves = untried_moves


    # Play game to the end with random moves on copy of game
    def play_out(self):
        game_clone = self.clone()
        while not game_clone.is_over:
            random_move = game_clone.play_out_policy()
            game_clone.play_move(random_move)

        return game_clone.result
    

    # Create new game object with stats of self
    def clone(self):
        return Game(self.my_global_board, self.opp_global_board, self.my_boards[:], self.opp_boards[:], self.board_spaces_counts[:],
                    self.curr_board_index, self.my_turn, self.is_over, self.result)

        
    # Return a list of every possible move
    def get_possible_moves(self):
        possible_moves = []
        if self.curr_board_index == -1:
            possible_board_indices = [i for i, count in enumerate(self.board_spaces_counts) if count != 0]
        else:
            possible_board_indices = [self.curr_board_index]
        
        for i in possible_board_indices:
            empty_spaces = (self.my_boards[i] | self.opp_boards[i]) ^ FULL_BOARD
            while empty_spaces:
                cell_bit = empty_spaces & ((empty_spaces-1) ^ FULL_BOARD)
                possible_moves.append((i, cell_bit))
                empty_spaces &= empty_spaces - 1
        
        return possible_moves


    # Randomly select a possible move
    def play_out_policy(self):
        board_index = self.curr_board_index
        if board_index == -1:
            # Select random board
            board_index = random.choices(range(9), weights=self.board_spaces_counts)[0]
        
        # Return a single randomly chosen bit from chosen board
        empty_spaces = (self.my_boards[board_index] | self.opp_boards[board_index]) ^ FULL_BOARD
        random_index = random.randint(1, self.board_spaces_counts[board_index])
        for i in range(random_index - 1):
            empty_spaces &= empty_spaces - 1
        empty_spaces &= (empty_spaces - 1) ^ FULL_BOARD

        return board_index, empty_spaces


    # Update this game's state by playing move. If game over, set result to 1 for my win, 0 for opp win or 0.5 for draw
    def play_move(self, move):
        board_index, cell_bit = move
        if self.my_turn:
            self.my_boards[board_index], self.my_global_board = self.fill_cell(self.my_boards[board_index], self.my_global_board, board_index, cell_bit)
        else:
            self.opp_boards[board_index], self.opp_global_board = self.fill_cell(self.opp_boards[board_index], self.opp_global_board, board_index, cell_bit)
        
        if self.is_over:
            return
        
        next_board_index = LOG2[cell_bit]
        if self.board_spaces_counts[next_board_index] == 0:
            next_board_index = -1
        self.curr_board_index = next_board_index
    

    def fill_cell(self, player_board, player_global_board, board_index, cell_bit):
        self.my_turn = not self.my_turn
        board_completed = False  # Whether the small board has a line of 3 or has it been completely filled
        self.board_spaces_counts[board_index] -= 1
        if self.board_spaces_counts[board_index] == 0:
            board_completed = True
        
        player_board |= cell_bit
        if self.line_of_three(player_board):
            board_completed = True
            player_global_board |= 0b1 << board_index
            self.board_spaces_counts[board_index] = 0
            
            if self.line_of_three(player_global_board):
                self.is_over = True
                self.result = 1 if player_global_board & self.my_global_board else 0
                return player_board, player_global_board

        if board_completed and not any(self.board_spaces_counts):
            # All smaller boards completed but no line of 3, need to count smaller board wins
            self.is_over = True
            my_wins = 0
            n = self.my_global_board
            while n:
                n &= n - 1
                my_wins += 1
            opp_wins = 0
            n = self.opp_global_board
            while n:
                n &= n - 1
                opp_wins += 1
            
            if my_wins != opp_wins:
                self.result = 1 if my_wins > opp_wins else 0
            else:
                self.result = 0.5
        
        return player_board, player_global_board


    def line_of_three(self, board):
        return any(board & line == line for line in Game.LINES)

    
    def check_valid_player_move(self, row, col):
        if row < 0 or row >= 9 or col < 0 or col >= 9:
            return False, 'Row and column numbers should be between 0 and 8.'

        board_index, cell_bit = Game.row_col_to_board_cell(row, col)
        
        if board_index != self.curr_board_index and self.curr_board_index != -1:
            correct_board_location = BOARD_LOCATION[self.curr_board_index]
            return False, 'Next move must be played in the ' + correct_board_location + ' board.'

        if self.board_spaces_counts[board_index] == 0:
            return False, 'Local board is already completed.'
        
        if self.my_boards[board_index] & cell_bit or self.opp_boards[board_index] & cell_bit:
            return False, 'Cell is already occupied.'
        
        return True, ''


    @staticmethod
    def row_col_to_board_cell(row, col):
        board_index = 3 * (row//3) + col//3
        cell_bit = 0b1 << (3 * (row%3) + col%3)
        return board_index, cell_bit
    

    @staticmethod
    def board_cell_to_row_col(board_index, cell_bit):
        cell = LOG2[cell_bit]
        row = 3 * (board_index//3) + cell//3
        col = 3 * (board_index%3) + cell%3
        return row, col


    def __str__(self):
        matrix = [[[[' '] * 3 for _ in range(3)] for _ in range(3)] for _ in range(3)]
        for i, board in enumerate(self.my_boards):
            mat = matrix[i // 3][i % 3]
            for b in range(9):
                if board & (1 << b):
                    mat[b // 3][b % 3] = 'O'
        
        for i, board in enumerate(self.opp_boards):
            mat = matrix[i // 3][i % 3]
            for b in range(9):
                if board & (1 << b):
                    mat[b // 3][b % 3] = 'X'

        for i, global_row in enumerate(matrix):
            single_rows = []
            for r in range(3):
                row_string = '|'.join('|'.join(local_row) for local_row in map(lambda board: board[r], global_row))
                single_rows.append(str(3 * i + r) + ' ' + row_string)
            matrix[i] = '\n  -+-+-|-+-+-|-+-+-\n'.join(single_rows)

        return '  0 1 2 3 4 5 6 7 8\n' + '\n  -----+-----+-----\n'.join(matrix)

    

class Node:
    __slots__ = 'game', 'parent', 'move', 'fully_expanded', 'children', 'visits', 'wins'

    def __init__(self, game, parent=None, move=None):
        self.game = game
        self.parent = parent
        self.move = move
        self.fully_expanded = False
        self.children = []
        self.visits = 0
        self.wins = 0
    

    def is_root(self):
        return self.parent == None

    
    def get_unvisited_child(self):
        game_child, move_played = self.game.get_unvisited_game()
        if game_child is None:
            # Node is terminal node
            self.fully_expanded = True
            return None
        node_child = Node(game_child, self, move_played)
        self.children.append(node_child)
        if not self.game.untried_moves:
            self.fully_expanded = True
        return node_child


    def play_out(self):
        # Simulate game to end using random moves, return result
        return self.game.play_out()


    def update_stats(self, result):
        self.visits += 1
        if not self.game.my_turn:
            self.wins += result
        else:
            self.wins += 1 - result



def monte_carlo_tree_search(root, timer_start, time_limit):
    iterations = 0
    t = perf_counter() - timer_start
    while t < time_limit:
        leaf_node = traverse(root) # leaf = either an unvisited node or a terminal node
        backpropagate(leaf_node, leaf_node.play_out())
        iterations += 1
        t = perf_counter() - timer_start
    
    return max(root.children, key=attrgetter('visits')), iterations


def traverse(node):
    while node.fully_expanded:
        if not node.children:
            # Node is terminal
            return node
        node = max(node.children, key=uct)
    return node.get_unvisited_child() or node  # in case no children are present i.e. node is terminal


def backpropagate(node, result):
    node.update_stats(result)
    if node.is_root():
        return
    backpropagate(node.parent, result)


# Upper Confidence Bound applied to trees - balances exploitation and exploration
# Note: Exploration parameter c set to sqrt(2), higher means more exploration
def uct(node):
    return (node.wins / node.visits) + math.sqrt(2 * math.log(node.parent.visits) / node.visits)


def play_tic_tac_toe(time_per_turn):
    real_game = Game()  # Actual game state
    real_game_node = Node(real_game)  # Node representing actual game state

    opp_row, opp_col = yield real_game

    while True:
        if opp_row != -1:
            board_index, cell_bit = Game.row_col_to_board_cell(opp_row, opp_col)
            opp_move = (board_index, cell_bit)
            new_node = next((node for node in real_game_node.children if node.move == opp_move), None)
            if new_node is not None:
                # Reuse node from simulation previously
                real_game_node = new_node
                real_game = real_game_node.game
                real_game_node.parent = None
            else:
                # New state not yet explored, play move onto real_game
                if real_game.my_turn:
                    # Only needed on first turn if opponent moves first
                    real_game.my_turn = False
                real_game.play_move(opp_move)
                real_game.untried_moves = None  # Remember to clear untried moves of previous state
                real_game_node = Node(real_game)

        yield real_game

        timer_start = perf_counter()

        chosen_move = None

        if opp_row == -1:
            # If making first move, fix move as (row 4, col 4) to avoid having to try all 81 squares
            real_game.play_move((4, 0b000010000))
            _, iterations = monte_carlo_tree_search(real_game_node, timer_start, time_per_turn)
            # print('n =', str(iterations), end='\n\n')
            chosen_move = (4, 4)
        else:
            best_node, iterations = monte_carlo_tree_search(real_game_node, timer_start, time_per_turn)
            board_index, cell_bit = best_node.move
            move_row, move_col = Game.board_cell_to_row_col(board_index, cell_bit)
            # print('n =', str(iterations), end='\n\n')
            # print(*(f'{Game.board_cell_to_row_col(*child.move)}\nWins: {child.wins} Visits: {child.visits}\n' for child in real_game_node.children), sep='\n')
            chosen_move = (move_row, move_col)

            real_game = best_node.game
            real_game_node = best_node
            real_game_node.parent = None
        
        opp_row, opp_col = yield chosen_move, real_game



# Play Ultimate Tic Tac Toe in terminal
if __name__ == '__main__':    
    player_input = None
    while player_input not in ['Y', 'N', 'YES', 'NO']:
        player_input = input('Would you like to go first? (Y/N): ').upper()
    player_turn = player_input == 'Y' or player_input == 'YES'
    
    difficulty = 0
    while difficulty < 1 or difficulty > 8:
        try:
            difficulty = int(input('Select a difficulty from 1-8 (8 being the hardest): '))
        except ValueError:
            pass
    
    time_per_turn = [0.01, 0.05, 0.1, 0.5, 1, 2, 3, 5][difficulty - 1]
    game_generator = play_tic_tac_toe(time_per_turn)
    
    game_state = next(game_generator)
    
    print(game_state)  # Display empty board
    print()
    print('Input your moves as the row and column numbers separated by a space. Top left corner is 0 0, top right corner is 0 8.\n')

    if not player_turn:  # AI makes first move
        game_generator.send((-1, -1))

    while not game_state.is_over:
        if player_turn:
            move_valid = False
            while not move_valid:
                next_board_location = BOARD_LOCATION[game_state.curr_board_index] if game_state.curr_board_index != -1 else 'any'
                print('Next board:', next_board_location)
                player_input = input('Your move: ')
                print()
                try:
                    row, col = map(int, player_input.split())
                    move_valid, error_msg = game_state.check_valid_player_move(row, col)
                    if not move_valid:
                        print(error_msg)
                        print()
                except:
                    print('Please input your move as the row and column numbers separated by a space. Top left corner is 0 0, top right corner is 0 8.\n')

            game_state = game_generator.send((row, col))
        else:
            ai_move, game_state = next(game_generator)
            print('AI move:', *ai_move)
            print()

        print(game_state)
        print('\n')
        player_turn = not player_turn
    
    game_generator.close()
    print(['You won! Great job!', "It's a draw!", "AI won! Better luck next time!"][int(game_state.result * 2)])
