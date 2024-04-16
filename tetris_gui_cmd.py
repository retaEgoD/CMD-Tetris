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
            self.game.move_x(self.game.current_block, True)
        if (ch == curses.KEY_RIGHT or ch == RIGHT):
            self.game.move_x(self.game.current_block, False)
        if (ch == curses.KEY_UP or ch == UP):
            self.game.hard_drop()
        if (ch == curses.KEY_DOWN or ch == DOWN):
            self.game.move_down(self.game.current_block)
        if (ch == ord('z')):
            self.game.current_block.rotate(self.game.width, self.game.height, self.game.board.board, False)
        if (ch == ord('x')):
            self.game.current_block.rotate(self.game.width, self.game.height, self.game.board.board, True)
            
        
            
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
        
        
        self.screen.timeout(0)
        prev_time = time()
        at_bottom = False
        
        while True:
                
            t = self.game.get_time_interval()
            
            current_time = time()
            if current_time - prev_time > t:
                prev_time = current_time
                
                if at_bottom:
                    # Place and lock block
                    self.game.place_block()
                    at_bottom = False
                    
                elif self.game.check_y_collision(self.game.current_block):
                    # Block is touching floor or another block
                    at_bottom = True
                    
                else:
                    # Just move block down by one
                    self.game.move_down(self.game.current_block)
            
            ch = self.screen.getch()
            if ((ch != -1)):
                self.handle_keyboard_input(ch)
                at_bottom = False
                if (ch == DOWN):
                    prev_time = time()
                    
            cleared_lines = self.game.get_cleared_lines()
            
            if len(cleared_lines) > 0:
                self.game.clear_lines(cleared_lines)
            
            self.render(self.screen)
            self.screen.refresh()
                
                
        

            
def main(screen):
    
    gui = TetrisTerminalGui(screen)
    gui.game_loop()
    
    
if __name__ == '__main__':
    curses.wrapper(main)