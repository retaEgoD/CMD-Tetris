from random import shuffle

SHAPES = {
    'I': [(0, 0), (1, 0), (2, 0), (3, 0)],  # Long piece
    'J': [(1, 0), (1, 1), (1, 2), (0, 2)],
    'L': [(0, 0), (0, 1), (0, 2), (1, 2)],
    'O': [(0, 0), (0, 1), (1, 0), (1, 1)],  # Square
    'S': [(1, 0), (2, 0), (0, 1), (1, 1)],
    'T': [(0, 1), (1, 1), (2, 1), (1, 0)],
    'Z': [(0, 0), (1, 0), (1, 1), (2, 1)]
}


class CollisionError(Exception):
    
    def __init__(self, block, collision_coords):
        self.block = block
        self.collision_coords = collision_coords
        
        
    def ___str__(self):
        return f'Collision for block {self.bolck.shape_name} at coordinates {self.collision_coords}.'
        
        
class Coord:
    
    def __init__(self, coords):
        self.coords = coords
        
    
    def __iter__(self):
        return iter(self.coords)
    
    
    def __next__(self):
        
    
    
    def __repr__(self):
        return str(self.coords)[1:-1]
    
    
    def __add__(self, coords_2):
        new_coords = [(coord_1[0]+coord_2[0], coord_1[1]+coord_2[1]) for coord_1, coord_2 in zip(self.coords, coords_2)]
        return Coord(new_coords)
    

class Block:
    
    def __init__(self, shape_name):
        self.shape_name = shape_name
        self.shape_coords = Coord(SHAPES[shape_name])
        
        
    def rotate_clockwise(self):
        base_coords = Coord(SHAPES[self.shape_name])
        rotated_coords = [(-y, x) for x, y in base_coords]
        
        # while any([x < 0 for x, _ in rotated_coords]):
        #     rotated_coords = [(x + 1, y) for x, y in rotated_coords]
            
        self.shape_coords += Coord(rotated_coords) - Coord(base_coords)
        
    
    def rotate_anticlockwise(self):
        base_coords = Coord(SHAPES[self.shape_name])
        rotated_coords =  [(y, -x) for x, y in self.shape_coords]
        
        # while any([y < 0 for _, y in rotated_coords]):
        #     rotated_coords = [(x, y + 1) for x, y in rotated_coords]
            
        self.shape_coords = Coord(rotated_coords) - Coord(base_coords)
        
        
    def get_block_length(self):
        """Gets the length of the block in the y direction.

        Returns:
            _type_: _description_
        """
        y = [y for _, y in self.shape_coords]
        return abs(min(y) - max(y))
        
        
class Board:
    
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.board = [[0 for _ in width] for _ in height + 3] # Height + 3 since longest a piece can be with only one block on screen is long piece.
        
        
    def place_block(self, block):
        """Places a block onto the game board.
           Assumes collision has been checked beforehand.

        Args:
            block (_type_): _description_
        """
        coords = block.shape_coords
        for x, y in block.shape_coords:
            if self.board[y][x] == 1:
                
            self.board()
        
        
    def clear(self):
        self.board = [[0 for _ in self.width] for _ in self.height + 3]
        
        
    def clear_line(self, line_number):
        self.board[line_number] = [0 for _ in self.width]
        
        
class Tetris:
    
    def __init__(self):
        self.shape_bag = list(SHAPES.keys())
        shuffle(self.shape_bag)
        
        
    def get_new_shape(self):
        if len(self.shape_bag) == 0:
            self.generate_new_bag()
        shape_name = self.shape_bag.pop()
        return Block(shape_name)
    
    
    def generate_new_bag(self):
        self.shape_bag = list(SHAPES.keys())
        shuffle(self.shape_bag)