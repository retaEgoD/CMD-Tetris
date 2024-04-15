import pygame
from pygame import mixer
from pygame.transform import scale
from pathlib import Path
from tetris_logic import Tetris
from itertools import product
import time

################## POSITIONS AND SCALING ##################
SCALE = 1.5
BLOCK_SIZE = 30*SCALE
BLOCK_SCALE = (BLOCK_SIZE, BLOCK_SIZE)
BACKGROUND_SCALE = (400*SCALE, 800*SCALE)

WIDTH, HEIGHT = 400*SCALE, 800*SCALE
GAME_WIDTH, GAME_HEIGHT = 300*SCALE, 600*SCALE
TOP_LEFT, TOP_RIGHT = (50*SCALE, 100*SCALE), (50*SCALE, 400*SCALE)
BOTTOM_LEFT, BOTTOM_RIGHT = (50*SCALE, 100*SCALE), (350*SCALE, 400*SCALE)


################## MISC SETTINGS ##################


WHITE = (255, 255, 255)
FPS = 60
MOVE_DOWN_EVENT = pygame.USEREVENT + 1
MUSIC_CHANGE_LEVEL_1 = 6
MUSIC_CHANGE_LEVEL_2 = 11

################## ASSET LOADING ##################

BACKGROUND = scale(pygame.image.load(Path("Assets/Backgrounds")/'Background.png'), BACKGROUND_SCALE)
BORDER = scale(pygame.image.load(Path("Assets/Backgrounds")/'Border_transparent.png'), BACKGROUND_SCALE)

BLOCK_GRAPHICS = {
    "I": scale(pygame.image.load(Path("Assets/Pieces")/'I_Block.png'), BLOCK_SCALE),
    "J": scale(pygame.image.load(Path("Assets/Pieces")/'J_Block.png'), BLOCK_SCALE),
    "L": scale(pygame.image.load(Path("Assets/Pieces")/'L_Block.png'), BLOCK_SCALE),
    "O": scale(pygame.image.load(Path("Assets/Pieces")/'O_Block.png'), BLOCK_SCALE),
    "S": scale(pygame.image.load(Path("Assets/Pieces")/'S_Block.png'), BLOCK_SCALE),
    "Z": scale(pygame.image.load(Path("Assets/Pieces")/'Z_Block.png'), BLOCK_SCALE),
    "T": scale(pygame.image.load(Path("Assets/Pieces")/'T_Block.png'), BLOCK_SCALE)
}
GHOST = scale(pygame.image.load(Path("Assets/Pieces")/'ghost.png'), BLOCK_SCALE)

TETRIS_A = Path("Assets/sounds")/'tetris_a.ogg'
TETRIS_B = Path("Assets/sounds")/'tetris_b.ogg'
GOD_SHATTERING_STAR = Path("Assets/sounds")/'GOD_SHATTERING_STAR.mp3'




class TetrisPyGame:
    
    # TODO: Add hold, queue, game over, make controls not shit.
    
    def __init__(self):
        self.game = Tetris()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TETRIS, BABY")


    def draw_window(self, shape):
        
        shape_name, coords = shape
        top_left_x, top_left_y = TOP_LEFT
        
        self.window.blit(BACKGROUND, (0, 0))
        for block in coords:
            self.window.blit(BLOCK_GRAPHICS[shape_name], (block.x + top_left_x, block.y + top_left_y))
            
        board = self.game.board.board
        for x, y in product(range(self.game.width), range(self.game.height)):
            if board[y][x]:
                self.window.blit(BLOCK_GRAPHICS[board[y][x]], 
                                 (top_left_x + x*BLOCK_SIZE, top_left_y + y*BLOCK_SIZE))
                
        for x, y in self.game.get_ghost_block().coords:
            self.window.blit(GHOST, (top_left_x + x*BLOCK_SIZE, top_left_y + y*BLOCK_SIZE))
            
        self.window.blit(BORDER, (0, 0))
            
            
        pygame.display.update()
        
        
    def get_pygame_block(self, block):
    
        coords = block.coords
        
        block_1 = pygame.Rect(coords[0][0]*BLOCK_SIZE, coords[0][1]*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        block_2 = pygame.Rect(coords[1][0]*BLOCK_SIZE, coords[1][1]*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        block_3 = pygame.Rect(coords[2][0]*BLOCK_SIZE, coords[2][1]*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        block_4 = pygame.Rect(coords[3][0]*BLOCK_SIZE, coords[3][1]*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        
        return (block.shape_name, (block_1, block_2, block_3, block_4))
        
        
    def game_loop(self):
        
        clock = pygame.time.Clock()
        clock_2 = 0
        t = self.game.get_time_interval()*1000
        prev_t = t
        at_bottom = False
        prev_music_change = None
        
        pygame.time.set_timer(MOVE_DOWN_EVENT, int(t))
        run = True
        mixer.init()
        mixer.music.load(TETRIS_A)
        mixer.music.play()
        mixer.music.set_volume(0.1)
        music_ticker = None
        
        while run:
            level = self.game.get_current_level()
            
            if (MUSIC_CHANGE_LEVEL_1 <= level < MUSIC_CHANGE_LEVEL_2  and prev_music_change != 1):
                prev_music_change = 1
                music_ticker = 0
                mixer.music.fadeout(5000)
                
                
            if (level >= MUSIC_CHANGE_LEVEL_2 and prev_music_change != 2):
                prev_music_change = 2
                music_ticker = 0
                mixer.music.fadeout(5000)
                
                
            if (music_ticker != None):
                music_ticker += 1
                
                
            if (music_ticker == 300 and prev_music_change == 1):
                mixer.music.load(TETRIS_B)
                mixer.music.play()
                
            if (music_ticker == 300 and prev_music_change == 2):
                mixer.music.load(GOD_SHATTERING_STAR)
                mixer.music.play()
            
            
            clock_2 += 1
            if (clock_2 == FPS):
                clock_2 = 0
            
            t = self.game.get_time_interval()*1000
            if (prev_t != t):
                prev_t = t
                pygame.time.set_timer(MOVE_DOWN_EVENT, int(t))
            
            shape = self.get_pygame_block(self.game.current_block)
            
            clock.tick(FPS)
            
            ################# EVENT LOOP #################
            
            for event in pygame.event.get():
                
                if (event.type == MOVE_DOWN_EVENT):
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
                
                
                if (event.type == pygame.KEYDOWN):
                    if (event.key == pygame.K_UP):
                        self.game.hard_drop()
                    if (event.key == pygame.K_z):
                        self.game.current_block.rotate(self.game.width, self.game.height, self.game.board.board, False)
                    if (event.key == pygame.K_x):
                        self.game.current_block.rotate(self.game.width, self.game.height, self.game.board.board, True)
                    at_bottom = False
                    
                    if (event.key == pygame.K_ESCAPE):
                        pygame.event.post(pygame.QUIT)
                
                if (event.type == pygame.QUIT):
                    run = False
                    
            
            ################# EVENT LOOP END #################        
            
            keys_pressed = pygame.key.get_pressed()
            if (clock_2 % 3 == 0):
                if (keys_pressed[pygame.K_LEFT]):
                    self.game.move_x(self.game.current_block, True)
                    at_bottom = False
                if (keys_pressed[pygame.K_RIGHT]):
                    self.game.move_x(self.game.current_block, False)
                    at_bottom = False
            if (clock_2 % 2 == 0):
                if (keys_pressed[pygame.K_DOWN]):
                    self.game.move_down(self.game.current_block)  
                    pygame.time.set_timer(MOVE_DOWN_EVENT, int(t))
                    at_bottom = False
                    
            cleared_lines = self.game.get_cleared_lines()
            
            if len(cleared_lines) > 0:
                self.game.clear_lines(cleared_lines)
            
            self.draw_window(shape)
                    
        pygame.quit()


def main():
    gui = TetrisPyGame()
    gui.game_loop()
    
    
    
if __name__ == "__main__":
    main()