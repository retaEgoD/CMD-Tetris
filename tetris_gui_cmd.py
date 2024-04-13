import curses
from time import time
from itertools import product
from tetris_logic import Tetris, SCORES


UP = 450
LEFT = 452
RIGHT = 454
DOWN = 456

KEYS = [UP, DOWN, LEFT, RIGHT, 'z', 'x']

BORDER = '■'
BLOCK = '□'

class TetrisTerminalGui:
    
    # TODO: fix block locking timing
    
    def __init__(self, screen):
        self.game = Tetris()
        self.screen = screen
        
        
    def handle_keyboard_input(self, ch):
        if (ch == curses.KEY_LEFT or ch == LEFT):
            self.game.move_left()
        if (ch == curses.KEY_RIGHT or ch == RIGHT):
            self.game.move_right()
        if (ch == curses.KEY_UP or ch == UP):
            self.game.hard_drop()
        if (ch == curses.KEY_DOWN or ch == DOWN):
            self.game.move_down()
        if (ch == ord('z')):
            self.game.current_block.rotate_anticlockwise()
        if (ch == ord('x')):
            self.game.current_block.rotate_clockwise()
            
        
            
    def render(self, screen):
        
        width = self.game.width + 2
        height = self.game.height + 2
        board = self.game.board.board
        
        rows = [[BORDER if ((i == 0) or (i == width-1)) else ' ' for i in range(width)] for _ in range(height)]
        for x, y in self.game.current_block.coords:
            if (x >= 0) and (y >= 0):
                rows[y+1][x+1] = BLOCK
        rows[0] = [BORDER] * width
        rows[-1] = [BORDER] * width
        
        
        for x, y in product(range(1, width-1), range(1, height-1)):
            if (board[y-1][x-1]):
                rows[y][x] = BLOCK
                
        for x, y in self.game.get_ghost_block().coords:
            rows[y+1][x+1] = BORDER
                
        
        for i, row in enumerate(rows):
            screen.addstr(i, 0, ''.join(row))
    
    
    def game_loop(self):
        
        # TODO: Fix bug when clearing 2+ lines
        
        self.screen.timeout(0)
        prev_time = time()
        at_bottom = False
        prev_tetris = False
        
        while True:
            if self.game.score > 1:
                print()
                [print(x) for x in self.game.board.board]
                
            level = self.game.score//5 + 1
            t = 0.8 - (level-1)**0.007 # Time between game ticks
            
            current_time = time()
            if current_time - prev_time > t:
                prev_time = current_time
                
                if at_bottom:
                    # Place and lock block
                    self.game.board.place_block(self.game.current_block)
                    self.game.current_block = self.game.get_new_shape()               
                    
                elif self.game.check_y_collision():
                    # Block is touching floor or another block
                    at_bottom = True
                    
                else:
                    # Just move block down by one
                    self.game.move_down()
            
            ch = self.screen.getch()
            if ((ch != -1)):
                self.handle_keyboard_input(ch)
                at_bottom = False
                if (ch == DOWN):
                    prev_time = time()
                    
            cleared_lines = self.game.check_line_clear()
            no_cleared = len(cleared_lines)
            if no_cleared > 0:
                match no_cleared:
                    case 1:
                        self.game.score += SCORES['SINGLE']
                        self.game.clear_line(cleared_lines[0])
                        self.game.pad_line()
                        prev_tetris = False
                    case 2:
                        self.game.score += SCORES['DOUBLE']
                        for line in cleared_lines:
                            self.game.clear_line(line)
                            self.game.pad_line()
                        prev_tetris = False
                    case 3:
                        self.game.score += SCORES['TRIPLE']
                        for line in cleared_lines:
                            self.game.clear_line(line)
                            self.game.pad_line()
                        prev_tetris = False
                    case 4:
                        if prev_tetris:
                            self.game.score += SCORES['TETRIS B2B']
                        else:
                            self.game.score += SCORES['TETRIS']
                        for line in cleared_lines:
                            self.game.clear_line(line)
                            self.game.pad_line()
                        prev_tetris = True
                [print(x) for x in self.game.board.board]
            
            self.render(self.screen)
            self.screen.refresh()
                
                
        

            
def main(screen):
    
    gui = TetrisTerminalGui(screen)
    gui.game_loop()
    
    
if __name__ == '__main__':
    curses.wrapper(main)