from random import shuffle
from copy import deepcopy


SHAPES = {
    'I': [(0, 0), (1, 0), (2, 0), (3, 0)],  # Long piece
    'J': [(1, 0), (1, 1), (1, 2), (0, 2)],
    'L': [(0, 0), (0, 1), (0, 2), (1, 2)],
    'O': [(0, 0), (0, 1), (1, 0), (1, 1)],  # Square
    'S': [(1, 0), (2, 0), (0, 1), (1, 1)],
    'T': [(0, 1), (1, 1), (2, 1), (1, 0)],
    'Z': [(0, 0), (1, 0), (1, 1), (2, 1)]
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
    
    def __init__(self, block, collision_coords):
        self.block = block
        self.collision_coords = collision_coords
        
        
    def ___str__(self):
        return f'Collision for block {self.block.shape_name} at coordinates {self.collision_coords}.'
        
        
class Coord:
    
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
    
    # TODO: Fix rotation algorithm (rotate about origin)
    
    def __init__(self, shape_name):
        self.shape_name = shape_name # Name of shape type.
        self.base_coords = Coord(SHAPES[shape_name]) # Base coordinates defining the shape.
        self.coords = self.base_coords # Actual location on game board.
        
        
    def rotate_clockwise(self):
        base_coords = self.base_coords
        rotated_coords = [(-y, x) for x, y in base_coords]
        self.base_coords = rotated_coords
                    
        self.coords += Coord(rotated_coords) - Coord(base_coords)
        
    
    def rotate_anticlockwise(self):
        base_coords = self.base_coords
        rotated_coords =  [(y, -x) for x, y in base_coords]
        self.base_coords = rotated_coords            
        
        self.coords += Coord(rotated_coords) - Coord(base_coords)
        
        
    def get_block_length(self):
        """Gets the length of the block in the y direction.

        Returns:
            _type_: _description_
        """
        y = [y for _, y in self.coords]
        return abs(min(y) - max(y))
    
    
    def __repr__(self):
        return self.shape_name
        



class Board:
    
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        
        
    def place_block(self, block):
        """Places a block onto the game board.
           Assumes collision has been checked beforehand.

        Args:
            block (_type_): _description_
        """
        for x, y in block.coords:
            # if self.board[y][x] == 1:
            #     raise CollisionError(block, (x, y))
            self.board[y][x] = 1
        
        
    def clear(self):
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        
    def clear_line(self, line_number):
        self.board[line_number] = [0 for _ in self.width]
        



class Tetris:
    
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
        if len(self.shape_bag) == 0:
            self.generate_new_bag()
        shape_name = self.shape_bag.pop()
        new_block = Block(shape_name)
        for _ in range(5):
            new_block.coords += Coord(X_RIGHT)
        return new_block
    
    
    def generate_new_bag(self):
        self.shape_bag = list(SHAPES.keys())
        shuffle(self.shape_bag)
        
        
    def check_x_collision(self, check_left, is_current_block=True, block=None):
        check_block = self.current_block if is_current_block else block
        coords = check_block.coords
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
    
    
    def check_y_collision(self, is_current_block=True, block=None):
        check_block = self.current_block if is_current_block else block
        coords = check_block.coords + Coord(Y_DOWN)
        board = self.board
        for x, y in coords:
            
            # Check floor collision.
            if y >= self.height:
                return True
            
            # Check block collision.
            if board.board[y][x]:
                return True
            
        return False
    
    
    def move_left(self, is_current_block=True, block=None):
        move_block = self.current_block if is_current_block else block
        if not self.check_x_collision(True, is_current_block, block):
            move_block.coords += Coord(X_LEFT)
            
    
    def move_right(self, is_current_block=True, block=None):
        move_block = self.current_block if is_current_block else block
        if not self.check_x_collision(False, is_current_block, block):
            move_block.coords += Coord(X_RIGHT)
            
    
    def move_down(self, is_current_block=True, block=None):
        move_block = self.current_block if is_current_block else block
        if not self.check_y_collision(is_current_block, block):
            move_block.coords += Coord(Y_DOWN)
            
            
    def hard_drop(self):
        while (not self.check_y_collision()):
            self.move_down()
        self.board.place_block(self.current_block)
        self.current_block = self.get_new_shape()
    
    
    def check_line_clear(self):
        return sorted([i for i, row in enumerate(self.board.board) if all(row)])
    
    
    def clear_line(self, line_number):
        self.board.board = self.board.board[:line_number] + self.board.board[line_number+1:]
    
    
    def pad_line(self):
        """Function to pad lines when a line is cleared"""
        self.board.board.insert(0, [0]*self.width)
            
    
    def get_ghost_block(self):
        ghost = deepcopy(self.current_block)
        while (not self.check_y_collision(False, ghost)):
            self.move_down(False, ghost)
        return ghost
            