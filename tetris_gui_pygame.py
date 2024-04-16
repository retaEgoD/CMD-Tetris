import pygame
from pygame import mixer, font
from pygame.transform import scale
from pathlib import Path
from tetris_logic import Tetris
from itertools import product

################## POSITIONS AND SCALING ##################

SCALE = 1.5
BLOCK_SIZE = 30*SCALE
BLOCK_SCALE = (BLOCK_SIZE, BLOCK_SIZE)
PIECE_SIZE = 120*SCALE
PIECE_SCALE = (PIECE_SIZE, PIECE_SIZE)
BACKGROUND_SCALE = (400*SCALE, 800*SCALE)
SIDE_BACKGROUND_SCALE = (200*SCALE, 200*SCALE)
QUEUE_SPACING = 100

WIDTH, HEIGHT = 800*SCALE, 800*SCALE
CORE_WIDTH, CORE_HEIGHT = 400*SCALE, 800*SCALE
GAME_WIDTH, GAME_HEIGHT = 300*SCALE, 600*SCALE
SIDE_WIDTH = 200*SCALE
BOARD_TOP_LEFT, BOARD_TOP_RIGHT = (50*SCALE+SIDE_WIDTH, 100*SCALE), (50*SCALE+SIDE_WIDTH, 400*SCALE)
BOARD_BOTTOM_LEFT, BOARD_BOTTOM_RIGHT = (50*SCALE+SIDE_WIDTH, 100*SCALE), (350*SCALE+SIDE_WIDTH, 400*SCALE)


################## MISC SETTINGS ##################

WHITE = (255, 255, 255)
FPS = 60
MOVE_DOWN_EVENT = pygame.USEREVENT + 1
MUSIC_CHANGE_LEVEL_1 = 5
MUSIC_CHANGE_LEVEL_2 = 11
mixer.init()
font.init()

################## ASSET LOADING ##################

# Graphics
BOARD_BACKGROUND = scale(pygame.image.load(Path("Assets/Backgrounds")/'Background.png'), BACKGROUND_SCALE)
BORDER = scale(pygame.image.load(Path("Assets/Backgrounds")/'Border_transparent.png'), BACKGROUND_SCALE)
SIDE_BACKGROUND = scale(pygame.image.load(Path("Assets/Backgrounds")/'Pattern01.png'), SIDE_BACKGROUND_SCALE)

BLOCK_GRAPHICS = {
    "I": scale(pygame.image.load(Path("Assets/Pieces")/'I_Block.png'), BLOCK_SCALE),
    "J": scale(pygame.image.load(Path("Assets/Pieces")/'J_Block.png'), BLOCK_SCALE),
    "L": scale(pygame.image.load(Path("Assets/Pieces")/'L_Block.png'), BLOCK_SCALE),
    "O": scale(pygame.image.load(Path("Assets/Pieces")/'O_Block.png'), BLOCK_SCALE),
    "S": scale(pygame.image.load(Path("Assets/Pieces")/'S_Block.png'), BLOCK_SCALE),
    "Z": scale(pygame.image.load(Path("Assets/Pieces")/'Z_Block.png'), BLOCK_SCALE),
    "T": scale(pygame.image.load(Path("Assets/Pieces")/'T_Block.png'), BLOCK_SCALE)
}
PIECE_GRAPHICS = {
    "J": scale(pygame.image.load(Path("Assets/Pieces")/'J_Piece.png'), PIECE_SCALE),
    "I": scale(pygame.image.load(Path("Assets/Pieces")/'I_Piece.png'), PIECE_SCALE),
    "L": scale(pygame.image.load(Path("Assets/Pieces")/'L_Piece.png'), PIECE_SCALE),
    "O": scale(pygame.image.load(Path("Assets/Pieces")/'O_Piece.png'), PIECE_SCALE),
    "S": scale(pygame.image.load(Path("Assets/Pieces")/'S_Piece.png'), PIECE_SCALE),
    "Z": scale(pygame.image.load(Path("Assets/Pieces")/'Z_Piece.png'), PIECE_SCALE),
    "T": scale(pygame.image.load(Path("Assets/Pieces")/'T_Piece.png'), PIECE_SCALE)
}
GHOST = scale(pygame.image.load(Path("Assets/Pieces")/'ghost.png'), BLOCK_SCALE)


# Music
TETRIS_A = Path("Assets/Music")/'tetris_a.ogg'
TETRIS_B = Path("Assets/Music")/'tetris_b.ogg'
GOD_SHATTERING_STAR = Path("Assets/Music")/'GOD_SHATTERING_STAR.ogg'

# Sounds
SOUNDS = {
    "MOVE_X_SOUND": mixer.Sound(str(Path("Assets/Sounds")/'move_x.ogg')),
    "MOVE_Y_SOUND": mixer.Sound(str(Path("Assets/Sounds")/'move_y.ogg')),
    "ROTATE_SOUND": mixer.Sound(str(Path("Assets/Sounds")/'rotate.ogg')),
    "HOLD_SOUND": mixer.Sound(str(Path("Assets/Sounds")/'hold.ogg')),
    "HARD_DROP_SOUND": mixer.Sound(str(Path("Assets/Sounds")/'hard_drop.ogg')),
    "SOFT_DROP_SOUND": mixer.Sound(str(Path("Assets/Sounds")/'soft_drop.ogg')),
    "LEVEL_UP_SOUND": mixer.Sound(str(Path("Assets/Sounds")/'level_up.ogg'))
}

CLEAR_SOUNDS = {
    1: mixer.Sound(str(Path("Assets/Sounds")/'clear_single.ogg')),
    2: mixer.Sound(str(Path("Assets/Sounds")/'clear_double.ogg')),
    3: mixer.Sound(str(Path("Assets/Sounds")/'clear_triple.ogg')),
    4: mixer.Sound(str(Path("Assets/Sounds")/'HOLY_SHIT.ogg'))
}

for sound in SOUNDS.values():
    sound.set_volume(0.2)
for sound in CLEAR_SOUNDS.values():
    sound.set_volume(0.2)

# Fonts
FONT_BIG = font.Font(Path("Assets/Fonts")/'Viga-Regular.ttf', 60)
FONT_SMALL = font.Font(Path("Assets/Fonts")/'Viga-Regular.ttf', 40)


# aseteroid.move_ip(random.randint(-1, 1), random.randint(-1, 1)) Screen shake?


class TetrisPyGame:
    
    # TODO: Game over, make controls not shit, soft drop locks weirdly.
    
    def __init__(self):
        self.game = Tetris()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TETRIS, BABY")


    def draw_window(self, shape, level):
        
        shape_name, coords = shape
        top_left_x, top_left_y = BOARD_TOP_LEFT
        
        # Backgrounds
        self.window.blit(BOARD_BACKGROUND, (SIDE_WIDTH, 0))
        for block in coords:
            self.window.blit(BLOCK_GRAPHICS[shape_name], (block.x + top_left_x, block.y + top_left_y))
        for y in range(4):
            self.window.blit(SIDE_BACKGROUND, (0, SIDE_WIDTH*y))
            self.window.blit(SIDE_BACKGROUND, (SIDE_WIDTH + CORE_WIDTH, SIDE_WIDTH*y))
        
        
        # Blocks
        board = self.game.board.board
        for x, y in product(range(self.game.width), range(self.game.height)):
            if board[y][x]:
                self.window.blit(BLOCK_GRAPHICS[board[y][x]], 
                                 (top_left_x + x*BLOCK_SIZE, top_left_y + y*BLOCK_SIZE))
        for x, y in self.game.get_ghost_block().coords:
            self.window.blit(GHOST, (top_left_x + x*BLOCK_SIZE, top_left_y + y*BLOCK_SIZE))
        
        # Hold and queue blocks
        if (self.game.held_block != None):
            self.window.blit(PIECE_GRAPHICS[self.game.held_block.shape_name], (50, 120))
        for i, piece in enumerate(self.game.queue):
            self.window.blit(PIECE_GRAPHICS[piece.shape_name], (SIDE_WIDTH + CORE_WIDTH + 50, (BLOCK_SIZE+QUEUE_SPACING)*i + 100))
        
        # Border to go over shapes
        self.window.blit(BORDER, (SIDE_WIDTH, 0))
        
        # Text
        level_text = FONT_BIG.render(f'LEVEL {level}', True, WHITE)
        hold_text = FONT_SMALL.render('ON HOLD', True, WHITE)
        queue_text = FONT_BIG.render('QUEUE', True, WHITE)
        self.window.blit(level_text, (40, 40))
        if (self.game.held_block != None):
            self.window.blit(hold_text, (40, 100))
        self.window.blit(queue_text, (SIDE_WIDTH + CORE_WIDTH + 40, 40))
            
            
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
        mixer.music.load(TETRIS_A)
        mixer.music.play(3)
        mixer.music.set_volume(0.1)
        music_ticker = None
        level = 1
        
        while run:
            
            prev_level = level
            level = self.game.get_current_level()
            if (prev_level != level):
                SOUNDS["LEVEL_UP_SOUND"].play()
            
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
                
                
            if (music_ticker == 250 and prev_music_change == 1):
                mixer.music.load(TETRIS_B)
                mixer.music.play(3)
                
            if (music_ticker == 250 and prev_music_change == 2):
                mixer.music.load(GOD_SHATTERING_STAR)
                mixer.music.play(3)
            
            
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
                    if (at_bottom and clock_2 == 48):
                        # Place and lock block
                        self.game.place_block()
                        SOUNDS["SOFT_DROP_SOUND"].play()
                        at_bottom = False
                        
                    elif (self.game.check_y_collision(self.game.current_block)):
                        # Block is touching floor or another block
                        at_bottom = True
                        
                    else:
                        # Just move block down by one
                        self.game.move_down(self.game.current_block)
                
                
                if (event.type == pygame.KEYDOWN):
                    if (event.key == pygame.K_UP):
                        self.game.hard_drop()
                        SOUNDS["HARD_DROP_SOUND"].play()
                    if (event.key == pygame.K_z):
                        self.game.current_block.rotate(self.game.width, self.game.height, self.game.board.board, False)
                        SOUNDS["ROTATE_SOUND"].play()
                    if (event.key == pygame.K_x):
                        self.game.current_block.rotate(self.game.width, self.game.height, self.game.board.board, True)
                        SOUNDS["ROTATE_SOUND"].play()
                    if (event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]):
                        self.game.hold_block()
                        SOUNDS["HOLD_SOUND"].play()
                    at_bottom = False
                    
                    if (event.key == pygame.K_ESCAPE):
                        pygame.event.post(pygame.QUIT)
                
                if (event.type == pygame.QUIT):
                    run = False
                    
            
            ################# EVENT LOOP END #################        
            
            keys_pressed = pygame.key.get_pressed()
            if (clock_2 % 4 == 0):
                if (keys_pressed[pygame.K_LEFT]):
                    self.game.move_x(self.game.current_block, True)
                    SOUNDS["MOVE_X_SOUND"].play()
                    at_bottom = False
                if (keys_pressed[pygame.K_RIGHT]):
                    self.game.move_x(self.game.current_block, False)
                    SOUNDS["MOVE_X_SOUND"].play()
                    at_bottom = False
            if (clock_2 % 2 == 0):
                if (keys_pressed[pygame.K_DOWN]):
                    self.game.move_down(self.game.current_block)  
                    pygame.time.set_timer(MOVE_DOWN_EVENT, int(t))
                    SOUNDS["MOVE_Y_SOUND"].play()
                    at_bottom = False
                    
            cleared_lines = self.game.get_cleared_lines()
            
            if len(cleared_lines) > 0:
                self.game.clear_lines(cleared_lines)
                CLEAR_SOUNDS[len(cleared_lines)].play()
            
            self.draw_window(shape, level)
                    
        pygame.quit()


def main():
    gui = TetrisPyGame()
    gui.game_loop()
    
    
    
if __name__ == "__main__":
    main()