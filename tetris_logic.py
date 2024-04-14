from random import shuffle
from copy import deepcopy

WIDTH = 10
HEIGHT = 20

SHAPES = {
    'I': [(-2, 0), (-1, 0), (0, 0), (1, 0)],  # Long piece
    'J': [(0, -1), (0, 0), (0, 1), (-1, 1)],
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

X_LEFT = [(-1, 0)]*4
X_RIGHT = [(1, 0)]*4
Y_DOWN = [(0, 1)]*4


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
        
        
class Coord:
    """
    Represents a set of coordinates.
    
    Attributes:
        coords (list): A list of coordinates.
    """
    
    def __init__(self, coords):
        self.coords = coords
        
    
    def __iter__(self):
        return iter(self.coords)        
    
    
    def __repr__(self):
        return str(self.coords)[1:-1]
    
    
    def __add__(self, coords_2):
        new_coords = [(coord_1[0]+coord_2[0], coord_1[1]+coord_2[1]) for coord_1, coord_2 in zip(self.coords, coords_2)]
        return Coord(new_coords)
    
    def __sub__(self, coords_2):
        new_coords = [(coord_1[0]-coord_2[0], coord_1[1]-coord_2[1]) for coord_1, coord_2 in zip(self.coords, coords_2)]
        return Coord(new_coords)




class Block:
    """
    Represents a block in the game.
    
    Attributes:
        shape_name (str): The name of the shape type.
        base_coords (Coord): The base coordinates defining the shape.
        coords (Coord): The actual location on the game board.
    """
    
    def __init__(self, shape_name):
        self.shape_name = shape_name # Name of shape type.
        self.base_coords = Coord(SHAPES[shape_name]) # Base coordinates defining the shape.
        self.coords = self.base_coords # Actual location on game board.
        
        
    def rotate_clockwise(self, max_x):
        """
        Rotates the block clockwise.
        """
        base_coords = self.base_coords
        rotated_coords = [(-y, x) for x, y in base_coords]
        self.base_coords = rotated_coords
                    
        self.coords += Coord(rotated_coords) - Coord(base_coords)
        while any([x < 0 for x, _ in self.coords]):
            self.coords += Coord(X_RIGHT)
        while any([x >= max_x for x, _ in self.coords]):
            self.coords += Coord(X_LEFT)
        
    
    def rotate_anticlockwise(self, max_x):
        """
        Rotates the block anticlockwise.
        """
        base_coords = self.base_coords
        rotated_coords =  [(y, -x) for x, y in base_coords]
        self.base_coords = rotated_coords            
        
        self.coords += Coord(rotated_coords) - Coord(base_coords)
        while any([x < 0 for x, _ in self.coords]):
            self.coords += Coord(X_RIGHT)
        while any([x >= max_x for x, _ in self.coords]):
            self.coords += Coord(X_LEFT)
        
        
    def get_block_length(self):
        """
        Gets the length of the block in the y direction.

        Returns:
            int: The length of the block.
        """
        y = [y for _, y in self.coords]
        return abs(min(y) - max(y))
    
    
    def __repr__(self):
        return str((self.shape_name, self.coords))
        



class Board:
    """
    Represents the game board.
    
    Attributes:
        width (int): The width of the board.
        height (int): The height of the board.
        board (list): A 2D list representing the board.
    """
    
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        
        
    def place_block(self, block):
        """
        Places a block onto the game board.
        
        Args:
            block (Block): The block to place.
        """
        for x, y in block.coords:
            if self.board[y][x] == 1:
                raise CollisionError(block, (x, y))
            self.board[y][x] = 1
        
        
    def clear(self):
        """
        Clears the board.
        """
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        



class Tetris:
    """
    Represents the game of Tetris.
    
    Attributes:
        score (int): The current score.
        width (int): The width of the board.
        height (int): The height of the board.
        board (Board): The game board.
        shape_bag (list): A list of shape names.
        current_block (Block): The current block.
    """
    
    # TODO: Add hold and queue
    
    def __init__(self, width=10, height=20):
        self.score = 0
        self.width = width
        self.height = height
        self.board = Board(width, height)
        self.shape_bag = list(SHAPES.keys())
        shuffle(self.shape_bag)
        self.current_block = self.get_new_shape()
        
        
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
        for _ in range(5):
            new_block.coords += Coord(X_RIGHT)
        for _ in range(2):
            new_block.coords += Coord(Y_DOWN)
        return new_block
    
    
    def generate_new_bag(self):
        """
        Generates a new shape bag.
        """
        self.shape_bag = list(SHAPES.keys())
        shuffle(self.shape_bag)
        
        
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
        if check_left:
            coords += Coord(X_LEFT)
        else:
            coords += Coord(X_RIGHT)
            
        board = self.board
        for x, y in coords:
            
            # Check wall collision.
            if x < 0 or x >= self.width:
                return True
            
            # Check block collision.
            if board.board[y][x]:
                return True
            
        return False
    
    
    def check_y_collision(self, block):
        """
        Checks if there is a collision on the y-axis.

        Args:
            block (Block): The block to check.

        Returns:
            bool: True if there is a collision, False otherwise.
        """
        coords = block.coords + Coord(Y_DOWN)
        board = self.board
        for x, y in coords:
            print(x, y)
            # Check floor collision.
            if y >= self.height:
                return True
            
            # Check block collision.
            if board.board[y][x]:
                return True
            
        return False
    
    
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
        self.board.place_block(self.current_block)
        self.current_block = self.get_new_shape()
    
    
    def check_line_clear(self):
        """
        Checks if any lines are cleared.

        Returns:
            list: A list of line numbers that are cleared.
        """
        return sorted([i for i, row in enumerate(self.board.board) if all(row)])
    
    
    def clear_line(self, line_number):
        """
        Clears a line from the board.

        Args:
            line_number (int): The number of the line to clear.
        """
        self.board.board.pop(line_number)
    
    
    def pad_line(self):
        """
        Pads the board with an empty line at the top.
        """
        self.board.board.insert(0, [0 for _ in range(self.width)])
            
    
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
            