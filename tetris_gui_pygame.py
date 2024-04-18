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
LOGO_SIZE = (510*SCALE, 209*SCALE)

WIDTH, HEIGHT = 800*SCALE, 800*SCALE
CORE_WIDTH, CORE_HEIGHT = 400*SCALE, 800*SCALE
BOARD_WIDTH, BOARD_HEIGHT = 300*SCALE, 600*SCALE
SIDE_WIDTH = 200*SCALE
BOARD_TOP_LEFT = (50*SCALE+SIDE_WIDTH, 100*SCALE)


################## MISC SETTINGS ##################

BLINK_EVENT = pygame.USEREVENT + 1
MOVE_DOWN_EVENT = pygame.USEREVENT + 2
CLEAR_LINES_EVENT = pygame.USEREVENT + 3

WHITE = (255, 255, 255)
RED = (255, 0, 0)
FPS = 60
MUSIC_CHANGE_LEVEL_1 = 5
MUSIC_CHANGE_LEVEL_2 = 11
mixer.init()
font.init()


################## ASSET LOADING ##################


# Graphics
LOGO = scale(pygame.image.load(Path('Assets')/'pyTetris.png'), LOGO_SIZE)

BACKGROUNDS_PATH = Path("Assets/Backgrounds")
START_BACKGROUND = scale(pygame.image.load(BACKGROUNDS_PATH/'Start.png'), (WIDTH, HEIGHT))
BOARD_BACKGROUND = scale(pygame.image.load(BACKGROUNDS_PATH/'Background.png'), BACKGROUND_SCALE)
BORDER = scale(pygame.image.load(BACKGROUNDS_PATH/'Border_transparent.png'), BACKGROUND_SCALE)
SIDE_BACKGROUND = scale(pygame.image.load(BACKGROUNDS_PATH/'Pattern01.png'), SIDE_BACKGROUND_SCALE)


PIECE_GRAPHICS_PATH = Path("Assets/Pieces")
SHAPE_NAMES = ["I", "J", "L", "O", "S", "Z", "T"]
BLOCK_GRAPHICS = {shape: scale(pygame.image.load(PIECE_GRAPHICS_PATH/f'{shape}_Block.png'), BLOCK_SCALE) for shape in SHAPE_NAMES}
PIECE_GRAPHICS = {shape: scale(pygame.image.load(PIECE_GRAPHICS_PATH/f'{shape}_Piece.png'), PIECE_SCALE) for shape in SHAPE_NAMES}
GHOST = scale(pygame.image.load(PIECE_GRAPHICS_PATH/'ghost.png'), BLOCK_SCALE)


# Music
MUSIC_PATH = Path("Assets/Music")
TETRIS_A = MUSIC_PATH/'tetris_a.ogg'
TETRIS_B = MUSIC_PATH/'tetris_b.ogg'
GOD_SHATTERING_STAR = MUSIC_PATH/'GOD_SHATTERING_STAR.ogg'


# Sounds
SOUNDS_PATH = Path("Assets/Sounds")
SOUND_NAMES = ["MOVE_X_SOUND", "MOVE_Y_SOUND", "ROTATE_SOUND", "HOLD_SOUND", 
               "HARD_DROP_SOUND", "SOFT_DROP_SOUND", "LEVEL_UP_SOUND"]
SOUNDS = {sound: mixer.Sound(str(SOUNDS_PATH/f'{sound[:-6].lower()}.ogg')) for sound in SOUND_NAMES}

CLEAR_SOUNDS = {i: mixer.Sound(str(Path("Assets/Sounds")/f'clear_{i}.ogg')) for i in range(1, 5)}

for sound in SOUNDS.values():
    sound.set_volume(0.2)
for sound in CLEAR_SOUNDS.values():
    sound.set_volume(0.2)

# Fonts
FONT_PATH = Path("Assets/Fonts")
FONT_BIG = font.Font(FONT_PATH/'Viga-Regular.ttf', 60)
FONT_SMALL = font.Font(FONT_PATH/'Viga-Regular.ttf', 40)


# aseteroid.move_ip(random.randint(-1, 1), random.randint(-1, 1)) Screen shake?

class TetrisPyGameWindow:
    
    def __init__(self):
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.is_visible = True
        self.fade_in_stage = 255
    
    
    def draw_start_screen(self):
        self.window.blit(START_BACKGROUND, (0, 0))
        LOGO.set_alpha(255 - self.fade_in_stage)
        if self.fade_in_stage > 0:
            self.fade_in_stage -= 5
        self.window.blit(LOGO, (WIDTH//2 - LOGO_SIZE[0]//2, 200))
        start_text = FONT_SMALL.render("PRESS ANY BUTTON TO START", True, WHITE)
        if (self.is_visible and self.fade_in_stage == 0):
            self.window.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 800))
        
    def draw_backgrounds(self):
        self.window.blit(BOARD_BACKGROUND, (SIDE_WIDTH, 0))
        for y in range((int(CORE_HEIGHT/SIDE_WIDTH))):
            self.window.blit(SIDE_BACKGROUND, (0, SIDE_WIDTH*y))
            self.window.blit(SIDE_BACKGROUND, (SIDE_WIDTH + CORE_WIDTH, SIDE_WIDTH*y))
        
    
    def draw_board(self, current_block, ghost_block, board, width, height):
        shape_name, coords = current_block
        top_left_x, top_left_y = BOARD_TOP_LEFT
        
        # Blocks
        for block in coords:
            self.window.blit(BLOCK_GRAPHICS[shape_name], (block.x + top_left_x, block.y + top_left_y))
        for x, y in product(range(width), range(height)):
            if board[y][x]:
                self.window.blit(BLOCK_GRAPHICS[board[y][x]], 
                                 (top_left_x + x*BLOCK_SIZE, top_left_y + y*BLOCK_SIZE))
        for x, y in ghost_block.coords:
            self.window.blit(GHOST, (top_left_x + x*BLOCK_SIZE, top_left_y + y*BLOCK_SIZE))
            
        # Border to go over shapes
        self.window.blit(BORDER, (SIDE_WIDTH, 0))
        
        
    def draw_side_modules(self, held_block, queue, level):
        
        # Hold and queue blocks
        if (held_block != None):
            self.window.blit(PIECE_GRAPHICS[held_block.shape_name], (50, 120))
        for i, piece in enumerate(queue):
            self.window.blit(PIECE_GRAPHICS[piece.shape_name], (SIDE_WIDTH + CORE_WIDTH + 50, (BLOCK_SIZE+QUEUE_SPACING)*i + 100))
        
        # Text
        level_text = FONT_BIG.render(f'LEVEL {level}', True, WHITE)
        queue_text = FONT_BIG.render('NEXT:', True, WHITE)
        self.window.blit(level_text, (40, 40))
        self.window.blit(queue_text, (SIDE_WIDTH + CORE_WIDTH + 40, 40))
        
        # Hold
        hold_text = FONT_SMALL.render('ON HOLD', True, WHITE)
        if (held_block != None and self.is_visible):
            self.window.blit(hold_text, (60, 100))
            pygame.draw.circle(self.window, RED, (40, 125), 8*SCALE)
    
    
    



class TetrisPyGame:
    
    # TODO: Game over, make controls not shit, soft drop locks weirdly, change hold to only allow one.. Screen shake?
    
    def __init__(self):
        self.game = Tetris()
        self.window = TetrisPyGameWindow()
        self.game_started = False
        pygame.display.set_caption("TETRIS, BABY")
        
        
    def get_pygame_block(self, shape):
        coords = shape.coords
        blocks = [pygame.Rect(coords[i][0]*BLOCK_SIZE, coords[i][1]*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE) for i in range(4)]
        return (shape.shape_name, blocks)
        
        
    def draw_game_screen(self):
        self.window.draw_backgrounds()
        self.window.draw_board(self.get_pygame_block(self.game.current_block), 
                               self.game.get_ghost_block(), 
                               self.game.board.board, 
                               self.game.width, 
                               self.game.height)
        self.window.draw_side_modules(self.game.held_block, 
                                      self.game.queue, 
                                      self.game.get_current_level())
        

    def draw_window(self):
        if (not self.game_started):
            self.window.draw_start_screen() 
        else:                            
            self.draw_game_screen()
            
        pygame.display.update()
        
        
    def start_screen_loop(self, events):
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif (event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]):
                self.game_started = True
                mixer.music.load(TETRIS_A)
                mixer.music.play(3)
                mixer.music.set_volume(0.1)
                pygame.time.set_timer(MOVE_DOWN_EVENT, int(self.game.get_time_interval()*1000))
                
    
    def handle_events(self, events, at_bottom):
        for event in events:
            
            if (event.type == CLEAR_LINES_EVENT):
                cleared_lines = self.game.get_cleared_lines()
                self.game.clear_lines(cleared_lines)
                CLEAR_SOUNDS[len(cleared_lines)].play()
                
            
            if (event.type == MOVE_DOWN_EVENT):
                if (at_bottom):
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
                
                if (event.key == pygame.K_ESCAPE):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    
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
                
            
    
     
    def game_loop(self, events, keys_pressed, clock, level, prev_t, at_bottom, prev_music_change, music_ticker, clock_2):
        
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
        
        clock.tick(FPS)
        
        ################# EVENT LOOP #################
        
        self.handle_events(events, at_bottom)
                
        ################# EVENT LOOP END #################        
        
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
        
        if self.game.check_cleared_lines():
            pygame.event.post(pygame.event.Event(CLEAR_LINES_EVENT))
        
        
        
    def main_loop(self):
        
        clock = pygame.time.Clock()
        clock_2 = 0
        t = self.game.get_time_interval()*1000
        prev_t = t
        at_bottom = False
        prev_music_change = None
        
        run = True
        music_ticker = None
        level = 1
        pygame.time.set_timer(BLINK_EVENT, 500)
        pygame.time.set_timer(MOVE_DOWN_EVENT, int(t))
        
        while run:
            
            events = pygame.event.get()
            event_types = [event.type for event in events]
            
            # Global events
            if (pygame.QUIT in event_types):
                run = False
            if (BLINK_EVENT in event_types):
                self.window.is_visible = not self.window.is_visible
                
            # Primary game logic
            if (not self.game_started):
                self.start_screen_loop(events)
            else:
                keys_pressed = pygame.key.get_pressed()
                self.game_loop(events, keys_pressed, clock, level, prev_t, at_bottom, prev_music_change, music_ticker, clock_2)
                
            self.draw_window()
                    
        pygame.quit()


def main():
    gui = TetrisPyGame()
    gui.main_loop()
    
    
    
if __name__ == "__main__":
    main()