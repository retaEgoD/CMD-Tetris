from random import shuffle
from copy import deepcopy
from math import log10


SHAPES = {
    'I': [(-2, 0), (-1, 0), (0, 0), (1, 0)],  # Long piece
    'J': [(-1, 1), (-1, 0), (0, 0), (1, 0)],
    'L': [(0, -1), (0, 0), (0, 1), (1, 1)],
    'O': [(-1, -1), (-1, 0), (0, -1), (0, 0)],  # Square
    'S': [(0, -1), (1, -1), (-1, 0), (0, 0)],
    'T': [(-1, 0), (0, 0), (1, 0), (0, -1)],
    'Z': [(-1, -1), (0, -1), (0, 0), (1, 0)]
}


SCORES = {
    'SINGLE': 1,
    'DOUBLE': 3,
    'TRIPLE': 5,
    'TETRIS': 8,
    'TETRIS B2B': 12
}


GAME_WIDTH = 10
GAME_HEIGHT = 20
BASE_TIME_INTERVAL = 0.8
MOVE_INTERVAL_DECREASE_RATE = 0.01
QUEUE_LENGTH = 5

X_LEFT = [(-1, 0)]*4
X_RIGHT = [(1, 0)]*4
Y_UP = [(0, -1)]*4
Y_DOWN = [(0, 1)]*4
STARTING_PAD = [(5, 3)] * 4


class CollisionError(Exception):
    """
    Exception raised when a collision occurs.
    
    Attributes:
        block (Block): The block that caused the collision.
        collision_coords (Coord): The coordinates where the collision occurred.
    """
    
    def __init__(self, block, collision_coords):
        self.block = block
        self.collision_coords = collision_coords
        
        
    def ___str__(self):
        return f'Collision for block {self.block.shape_name} at coordinates {self.collision_coords}.'
        
        
class Coord(tuple):
    """
    Represents a set of coordinates.
    
    Attributes:
        coords (list): A list of coordinates.
    """
    
    def __new__(cls, coords):
        return super().__new__(cls, coords)
        
    def __add__(self, other):
        return Coord([(x[0]+y[0], x[1]+y[1]) for x, y in zip(self, other)])
    
    def __sub__(self, other):
        return Coord([(x[0]-y[0], x[1]-y[1]) for x, y in zip(self, other)])
    
    def __repr__(self):
        return str(list(self))[1:-1]




class Block:
    """
    Represents a block in Tetris.
    
    Attributes:
        shape_name (str): The name of the shape type.
        base_coords (Coord): The base coordinates defining the shape.
        coords (Coord): The actual location on the board.
    """
    
    def __init__(self, shape_name):
        self.shape_name = shape_name
        self.base_coords = Coord(SHAPES[shape_name])
        self.coords = self.base_coords
        
    
    def rotate(self, max_x, max_y, board, is_clockwise):
        """
        Rotates the block clockwise.
        """
        if self.shape_name != 'O':
            base_coords = self.base_coords
            rotated_coords = [(-y, x) for x, y in base_coords] if is_clockwise else [(y, -x) for x, y in base_coords]
            self.base_coords = rotated_coords
            self.coords += Coord(rotated_coords) - Coord(base_coords)
            
            while any([x < 0 for x, _ in self.coords]):
                self.coords += Coord(X_RIGHT)
            while any([x >= max_x for x, _ in self.coords]):
                self.coords += Coord(X_LEFT)
            while any([y < 0 for _, y in self.coords]):
                self.coords += Coord(Y_DOWN)
            while any([(y >= max_y or board[y][x]) for x, y in self.coords]): # Causes crashes, index error
                self.coords += Coord(Y_UP)
    
    
    def __repr__(self):
        return str((self.shape_name, self.coords))
        



class Board:
    """
    Represents the board.
    
    Attributes:
        width (int): The width of the board.
        height (int): The height of the board.
        board (list): A 2D list representing the board.
    """
    
    def __init__(self, width=GAME_WIDTH, height=GAME_HEIGHT):
        self.width = width
        self.height = height
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        
        
    def add_block(self, block):
        """
        Adds a block onto the board.
        
        Args:
            block (Block): The block to place.
        """
        for x, y in block.coords:
            if self.board[y][x] != 0:
                raise CollisionError(block, (x, y))
            self.board[y][x] = block.shape_name
        
        
    def clear(self):
        """
        Clears the board.
        """
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
    
    
    def clear_line(self, line_number):
        """
        Clears a line from the board.

        Args:
            line_number (int): The number of the line to clear.
        """
        self.board.pop(line_number)
    
    
    def pad_line(self):
        """
        Pads the board with an empty line at the top.
        """
        self.board.insert(0, [0 for _ in range(self.width)])
        



class Tetris:
    """
    Represents the of Tetris.
    
    Attributes:
        score (int): The current score.
        width (int): The width of the board.
        height (int): The height of the board.
        board (Board): The board.
        shape_bag (list): A list of shape names.
        current_block (Block): The current block.
    """
    
    # TODO: Add queue
    
    def __init__(self, width=GAME_WIDTH, height=GAME_HEIGHT):
        self.score = 0
        self.width = width
        self.height = height+4
        self.board = Board(width, height+4)
        self.shape_bag = list(SHAPES.keys())
        shuffle(self.shape_bag)
        self.current_block = self.get_new_shape()
        self.queue = []
        for _ in range(QUEUE_LENGTH):
            self.queue.append(self.get_new_shape())
        self.held_block = None
        self.just_held = False
        self.prev_clear = 0
        
        
    def get_new_shape(self):
        """
        Gets a new shape from the shape bag.
        
        Returns:
            Block: The new block.
        """
        if len(self.shape_bag) == 0:
            self.generate_new_bag()
        shape_name = self.shape_bag.pop()
        new_block = Block(shape_name)
        new_block.coords += Coord(STARTING_PAD)
        
        return new_block
    
    
    def generate_new_bag(self):
        """
        Generates a new shape bag.
        """
        self.shape_bag = list(SHAPES.keys())
        shuffle(self.shape_bag)
        
        
    def pop_from_queue(self):
        """
        Pops the first element from the block queue and adds another to it.
        """
        self.queue.append(self.get_new_shape())
        self.current_block = self.queue.pop(0)
        
        
        
    def check_x_collision(self, check_left, block):
        """
        Checks if there is a collision on the x-axis.

        Args:
            check_left (bool): Whether to check for collision on the left side.
            block (Block): The block to check.

        Returns:
            bool: True if there is a collision, False otherwise.
        """
        coords = block.coords
        direction = Coord(X_LEFT) if check_left else Coord(X_RIGHT)
        coords += direction
        
        # Check wall collision and block collision
        if (any([y < 0 for _, y in coords])):
            return any([(x < 0 or x >= self.width) for x, _ in coords])
        return any([(x < 0 or x >= self.width or self.board.board[y][x]) for x, y in coords])
    
    
    def check_y_collision(self, block):
        """
        Checks if there is a collision on the y-axis.

        Args:
            block (Block): The block to check.

        Returns:
            bool: True if there is a collision, False otherwise.
        """
        coords = block.coords + Coord(Y_DOWN)
        
        return any([((y >= 0) and (y >= self.height or self.board.board[y][x])) for x, y in coords])
    
    
    def move_x(self, block, is_move_left):
        """
        Moves the block in the x-axis.

        Args:
            block (Block): The block to move. Defaults to None.
            is_move_left (bool): Whether to the left.
        """
        direction = Coord(X_LEFT) if is_move_left else Coord(X_RIGHT)
        if not self.check_x_collision(is_move_left, block):
            block.coords += direction
            
    
    def move_down(self, block):
        """
        Moves the block down.

        Args:
            block (Block): The block to move.
        """
        if not self.check_y_collision(block):
            block.coords += Coord(Y_DOWN)
            
            
    def hard_drop(self):
        """
        Drops the current block as far as possible without colliding with other blocks or the floor.
        """
        while (not self.check_y_collision(self.current_block)):
            self.move_down(self.current_block)
        self.place_block()
    
    
    def get_cleared_lines(self):
        """
        Gets the list of lines cleared, if any.

        Returns:
            list: A list of line numbers that are cleared.
        """
        return sorted([i for i, row in enumerate(self.board.board) if all(row)])
    
    
    def check_cleared_lines(self):
        """
        Checks if any lines have been cleared.

        Returns:
            bool: Whether any lines have been cleared.
        """
        return len(self.get_cleared_lines()) > 0
        
    
    def clear_lines(self, cleared_lines):
        """
        Clears full lines on the game board and adds score to the game score according to the score map.

        Args:
            cleared_lines: The indices of the cleared lines.
        """
        score_map = {1: SCORES['SINGLE'], 2: SCORES['DOUBLE'], 3: SCORES['TRIPLE'], 4: SCORES['TETRIS']}
        if (len(cleared_lines) == 4 and self.prev_clear >= 4):
            self.score += SCORES['TETRIS B2B']
        else:
            self.score += score_map[len(cleared_lines)]
        
        if (4 <= self.prev_clear and len(cleared_lines) == 4):
            self.prev_clear += 1
        else:
            self.prev_clear = len(cleared_lines)
            
        for line in cleared_lines:
            self.board.clear_line(line)
            self.board.pad_line()
            
    
    def get_ghost_block(self):
        """
        Gets the ghost block, which is the block that would be created if the current block were to be dropped as far as possible.

        Returns:
            Block: The ghost block.
        """
        ghost = deepcopy(self.current_block)
        while (not self.check_y_collision(ghost)):
            self.move_down(ghost)
        return ghost
    
    
    def get_current_level(self):
        """
        Returns the current level of the game based on the score.
        
        The level is calculated by dividing the score by 5 and adding 1.
        
        Returns:
            int: The current level of the game.
        """
        return self.score//10 + 1
    
    
    def get_move_time_interval(self):
        """
        Returns the time interval between each move based on the current level.
        
        The time interval decreases as the level increases.
        
        Returns:
            float: The time interval between each move.
        """
        level = self.get_current_level()
        return max(0.001, (BASE_TIME_INTERVAL - (level-1)*MOVE_INTERVAL_DECREASE_RATE)**(level-1))
    
    
    def get_lock_time_interval(self):
        """
        Returns the time interval for locking a block in place.

        Returns:
            float: The time interval when locking a block.
        """
        level = self.get_current_level()
        return BASE_TIME_INTERVAL - log10(0.2*level+0.8)
        # return BASE_TIME_INTERVAL - log10(0.25*level+0.75)
        
    
    
    def place_block(self):
        """
        Places the current block on the board and gets a new block.
        
        This function is used to place the block on the board when it reaches the bottom.
        """
        self.board.add_block(self.current_block)
        self.pop_from_queue()
        self.just_held = False
        
        
    def hold_block(self):
        """
        Holds the current block and gets a new block.
        If there is already a held block, it swaps the held block with the current block.
        """
        if (not self.just_held):
            hold = Block(self.current_block.shape_name)
            hold.coords += Coord(STARTING_PAD)
            if self.held_block == None:
                self.pop_from_queue()
            else:
                self.current_block = self.held_block
            self.held_block = hold
            self.just_held = True
            
            
    def check_game_over(self):
        