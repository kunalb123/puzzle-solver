PROMPT = '''
This puzzle solver is for the month/day of the year puzzle

Puzzle is of the shape:
Jan     Feb     Mar     Apr     May     Jun
Jul     Aug     Sep     Oct     Nov     Dec
1       2       3       4       5       6       7
8       9       10      11      12      13      14
15      16      17      18      19      20      21
22      23      24      25      26      27      28
29      30      31

The objective is to use eight distinctly shaped puzzle
pieces to cover all spots on the board except for a 
particular date. 

These are the pieces:
1a.         2b.         3c.         4d. 
x x         x           x x         x
x           x           x x         x x
x x         x x x       x x         x x

5e.         6f.         7g.         8h.
x           x             x x       x
x x         x             x         x
  x         x x         x x         x
  x         x                       x x

'''

BOARD = [
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', None],
    ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', None],
    ['1', '2', '3', '4', '5', '6', '7'],
    ['8', '9', '10', '11', '12', '13', '14'],
    ['15', '16', '17', '18', '19', '20', '21'],
    ['22', '23', '24', '25', '26', '27', '28'],
    ['29', '30', '31', None, None, None, None]
]

PIECES = {
    'a': [(0,0), (0,1), (1,0), (2,0), (2,1)],
    'b': [(0,0), (1,0), (2,0), (2,1), (2,2)],
    'c': [(0,0), (0,1), (1,0), (1,1), (2,0), (2,1)],
    'd': [(0,0), (1,0), (1,1), (2,0), (2,1)],
    'e': [(0,0), (1,0), (1,1), (2,1), (3,1)],
    'f': [(0,0), (1,0), (2,0), (2,1), (3,0)],
    'g': [(0,1), (0,2), (1,1), (2,1), (2,0)],
    'h': [(0,0), (1,0), (2,0), (3,0), (3,1)]
}

class PuzzlePiece:
    '''
    shape points are a list of points that define how the piece fits in space.
    EX: 
    shape_points = [(0,0), (1,0), (1,1)]
    is puzzle piece:
    x       <- row zero
    x x     <- row one
    '''
    def __init__(self, shape_points):
        self.shape_points = shape_points

    # brings all points to non-negative on both axis while preserving shape
    def scale_points(self, points):
        scaled = [(x,y) for x, y in points]
        min_x = min([x for x,_ in scaled])
        min_y = min([y for _,y in scaled])
        if min_x < 0:
            scaled = [(x+abs(min_x), y) for x, y in scaled]
        if min_y < 0:
            scaled = [(x, y+abs(min_y)) for x, y in scaled]
        return scaled

    # returns points rotated 90 degrees (all scaled to be at non-negative axis)
    def get_90_degree_clockwise_rotation(self, points):
        rotated_not_scaled = [(y, -x) for x, y in points]
        return self.scale_points(rotated_not_scaled)
    
    # returns points flipped across vertical axis (all scaled to be at non-negative axis)
    def get_flipped_piece(self, points):
        # note that x and y are not the axis we are using, we use row col where row is vertical
        # increasing downwards and col is horizontal increasing right
        flipped_not_scaled = [(x, -y) for x, y in points]
        return self.scale_points(flipped_not_scaled)

    # returns all the orientations (8) in space for this puzzle piece
    def get_orientations(self):
        orientations = [self.shape_points]
        # get rotations
        for i in range(3):
            rotated = self.get_90_degree_clockwise_rotation(orientations[-1])
            orientations.append(rotated)
        
        # get flipped rotations
        orientations.append(self.get_flipped_piece(orientations[0]))
        for i in range(3):
            rotated = self.get_90_degree_clockwise_rotation(orientations[-1])
            orientations.append(rotated)

        return orientations


class Board:

    def __init__(self, board, month, day):
        self.board = board
        month_found = False
        for r in range(2):
            for c in range(len(BOARD[0])):
                if self.board[r][c] == month:
                    self.board[r][c] = None
                    month_found = True

        if not month_found: raise Exception(f'month invalid: {month}') 

        day_found = False
        for r in range(2, len(BOARD)):
            for c in range(len(BOARD[0])):
                if self.board[r][c] == day:
                    self.board[r][c] = None
                    day_found = True

        if not day_found: raise Exception(f'day invalid: {day}')
        self.month = month
        self.day = day
    
    def print(self):
        print(f'Board for {self.month} {self.day}:')
        for row in self.board:
            formatted_row = '\t'.join([e if e is not None else 'None' for e in row])
            print(formatted_row)

    def get_free_point(self):
        # suboptimal way of getting free point 
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] is not None and self.board[r][c] not in PIECES:
                    return r,c
        return None

    def can_add_to_board(self, puzzle_piece_points):
        for r, c in puzzle_piece_points:
            try:
                if self.board[r][c] is None or self.board[r][c] in PIECES or r < 0 or c < 0:
                    return False
            except: return False
        return True
    
    def can_remove_from_board(self, puzzle_piece_points, id):
        for r, c in puzzle_piece_points:
            try: 
                if self.board[r][c] != id: return False
            except: return False
        return True

    def add_to_board(self, puzzle_piece_points, id):
        if self.can_add_to_board(puzzle_piece_points):
            for r, c in puzzle_piece_points:
                self.board[r][c] = id
        else: raise Exception('cannot add to board')

    def remove_from_board(self, puzzle_piece_points, id):
        if self.can_remove_from_board(puzzle_piece_points, id):
            for r, c in puzzle_piece_points:
                self.board[r][c] = '.'
        else: raise Exception('remove error')


class CalendarPuzzle:

    def __init__(self, month, day):
        import copy
        self.board = Board(copy.deepcopy(BOARD), month, day)
        self.pieces = {id: PuzzlePiece(points).get_orientations() for id, points in PIECES.items()}
        
    def add_r_c_to_points(self, points, r, c):
        return [(x+r, y+c) for x,y in points]
    
    def adjust_piece_to_zero_zero(self, piece_points, origin_index):
        r_shift = -piece_points[origin_index][0]
        c_shift = -piece_points[origin_index][1]
        return [(r_shift+r, c_shift+c) for r,c in piece_points]

    def solve(self):
        available_pieces = set(self.pieces.keys())
        return self.backtrack(available_pieces)

    def backtrack(self, available_pieces):
        free_point = self.board.get_free_point()
        if free_point is None:
            return self.board
        
        for available_piece in available_pieces:
            curr_available_pieces = available_pieces.copy()
            curr_available_pieces.remove(available_piece)
            for orientation in self.pieces[available_piece]:
                for i in range(len(orientation)):
                    try:
                        adjusted_pointss = self.adjust_piece_to_zero_zero(orientation, i)
                        adjusted_points = self.add_r_c_to_points(
                            adjusted_pointss, free_point[0], free_point[1])
                        self.board.add_to_board(adjusted_points, available_piece)
                        success_board = self.backtrack(curr_available_pieces)
                        if success_board is not None:
                            return success_board
                        self.board.remove_from_board(adjusted_points, available_piece)
                    except Exception as e: 
                        # print('excepted', e)
                        pass 
            curr_available_pieces.add(available_piece)
        return None

if __name__ == '__main__':
    import time
    print(PROMPT)
    month = input('Pick a date from {Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec}: ').capitalize()
    day = input('Pick a day of the month (1-31): ')
    start = time.time()
    calendar_puzzle = CalendarPuzzle(month, day)
    solution = calendar_puzzle.solve()
    if solution is None:
        print('something wrong')
    else:
        print('solved board:')
        solution.print()
    print('time taken', time.time() - start)