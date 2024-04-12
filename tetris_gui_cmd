import curses
from time import time
from itertools import product
from tetris_logic import Tetris


UP = 450
LEFT = 452
RIGHT = 454
DOWN = 456

KEYS = [UP, DOWN, LEFT, RIGHT, 'z', 'x']

BORDER = '■'
BLOCK = '□'

class TetrisTerminalGui:
    
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
            rows[y][x] = BLOCK
        rows[0] = [BORDER] * width
        rows[-1] = [BORDER] * width
        
        
        for x, y in product(range(1, width-1), range(1, height-1)):
            if (board[y-1][x-1]):
                rows[y][x] = BLOCK
                
        
        for i, row in enumerate(rows):
            screen.addstr(i, 0, ''.join(row))
    
    
    def game_loop(self):
        
        self.screen.timeout(0)
        prev_time = time()
        
        while True:
            level = self.game.score//5 + 1
            t = 0.8 - (level-1)**0.007 # Time between game ticks
            
            current_time = time()
            if current_time - prev_time > t:
                prev_time = current_time
                if self.game.check_y_collision():
                    if at_bottom:
                        self.game.board.place_block(self.game.current_block)
                        self.game.current_block = self.game.get_new_shape()
                    else:
                        at_bottom = True                    
                else:
                    self.game.move_down()
            
            ch = self.screen.getch()
            if ((ch != -1)):
                print(ch)
                self.handle_keyboard_input(ch)
                at_bottom = False
                if (ch == 456):
                    prev_time = time()
            
            self.render(self.screen)
            self.screen.refresh()
                
                
        

            
def main(screen):
    
    gui = TetrisTerminalGui(screen)
    gui.game_loop()
    
    
if __name__ == '__main__':
    curses.wrapper(main)