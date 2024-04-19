import pygame
from pygame import event, mixer, font, image, USEREVENT
from pygame.transform import scale


from pathlib import Path
from itertools import product
from time import time

from tetris_logic import Tetris

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

BLINK_EVENT = USEREVENT + 1
MOVE_DOWN_EVENT = USEREVENT + 2
CLEAR_LINES_EVENT = USEREVENT + 3
LEVEL_UP_EVENT = USEREVENT + 4
MUSIC_EVENT = USEREVENT + 5

GAMEPLAY_KEYS = [pygame.K_ESCAPE, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_z, pygame.K_x, pygame.K_LSHIFT, pygame.K_RSHIFT]
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GOLD = (255, 223, 0)
FPS = 60
MUSIC_CHANGE_LEVEL_1 = 5
MUSIC_CHANGE_LEVEL_2 = 11
mixer.init()
font.init()

SOFT_DELAY_TIMES = {}


################## ASSET LOADING ##################


# Graphics
LOGO = scale(image.load(Path('Assets')/'pyTetris.png'), LOGO_SIZE)

BACKGROUNDS_PATH = Path("Assets/Backgrounds")
START_BACKGROUND = scale(image.load(BACKGROUNDS_PATH/'Start.png'), (WIDTH, HEIGHT))
BOARD_BACKGROUND = scale(image.load(BACKGROUNDS_PATH/'Background.png'), BACKGROUND_SCALE)
BORDER = scale(image.load(BACKGROUNDS_PATH/'Border_transparent.png'), BACKGROUND_SCALE)
SIDE_BACKGROUND = scale(image.load(BACKGROUNDS_PATH/'Pattern01.png'), SIDE_BACKGROUND_SCALE)


GRAPHICS_PATH = Path("Assets/Graphics")
SHAPE_NAMES = ["I", "J", "L", "O", "S", "Z", "T"]
BLOCK_GRAPHICS = {shape: scale(image.load(GRAPHICS_PATH/"Block"/f'{shape}_Block.png'), BLOCK_SCALE) for shape in SHAPE_NAMES}
PIECE_GRAPHICS = {shape: scale(image.load(GRAPHICS_PATH/"Piece"/f'{shape}_Piece.png'), PIECE_SCALE) for shape in SHAPE_NAMES}
PIECE_GRAPHICS_GREY = {shape: scale(image.load(GRAPHICS_PATH/"Grey"/f'{shape}_Piece_Grey.png'), PIECE_SCALE) for shape in SHAPE_NAMES}
GHOST = scale(image.load(GRAPHICS_PATH/"Block"/'ghost.png'), BLOCK_SCALE)


# Music
MUSIC_PATH = Path("Assets/Music")
TETRIS_A = MUSIC_PATH/'tetris_a.ogg'
TETRIS_B = MUSIC_PATH/'tetris_b.ogg'
GOD_SHATTERING_STAR = MUSIC_PATH/'GOD_SHATTERING_STAR.ogg'


# Sounds
SOUNDS_PATH = Path("Assets/Sounds")
SOUND_NAMES = ["MOVE_X_SOUND", "MOVE_Y_SOUND", "ROTATE_SOUND", "HOLD_SOUND", 
               "HARD_DROP_SOUND", "SOFT_DROP_SOUND", "LEVEL_UP_SOUND", "B2B_BREAK_SOUND"]
SOUNDS = {sound: mixer.Sound(str(SOUNDS_PATH/f'{sound[:-6].lower()}.ogg')) for sound in SOUND_NAMES}

SINGLE_CLEAR_SOUNDS = {i: mixer.Sound(str(Path("Assets/Sounds")/f'clear_{i}.ogg')) for i in range(1, 4)}
TETRIS_SOUNDS = {i+3 :mixer.Sound(str(Path("Assets/Sounds")/f'clear_b2b_{i}.ogg')) for i in range(1, 5)}
CLEAR_SOUNDS = SINGLE_CLEAR_SOUNDS | TETRIS_SOUNDS

for sound in SOUNDS.values():
    sound.set_volume(0.2)
for sound in CLEAR_SOUNDS.values():
    sound.set_volume(0.2)

# Fonts
FONT_PATH = Path("Assets/Fonts")
FONT_BIG = font.Font(FONT_PATH/'Viga-Regular.ttf', 60)
FONT_SMALL = font.Font(FONT_PATH/'Viga-Regular.ttf', 40)
FONT_BIG_ITALIC = font.Font(FONT_PATH/'Lora-VariableFont_wght.ttf', 60)
FONT_SMALL_ITALIC = font.Font(FONT_PATH/'PlayfairDisplay-Italic-VariableFont_wght.ttf', 40)


# aseteroid.move_ip(random.randint(-1, 1), random.randint(-1, 1)) Screen shake?

class TetrisPyGameWindow:
    
    def __init__(self):
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.is_visible = True
        self.fade_in_stage = 255
        
        
    def get_render_block(self, shape):
        """
        Converts a Tetris shape into a Pygame block.
        
        Args:
            shape (TetrisShape): The Tetris shape to convert.
            
        Returns:
            tuple: A tuple containing the shape name and a list of Pygame Rect objects representing the blocks.
        """
        coords = shape.coords
        blocks = [pygame.Rect(coords[i][0]*BLOCK_SIZE, (coords[i][1]-4)*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE) for i in range(4)]
        return (shape.shape_name, blocks)
    
    
    def draw_start_screen(self):
        """
        Draws the start screen.
        """
        self.window.blit(START_BACKGROUND, (0, 0))
        LOGO.set_alpha(255 - self.fade_in_stage)
        if self.fade_in_stage > 0:
            self.fade_in_stage -= 5
        self.window.blit(LOGO, (WIDTH//2 - LOGO_SIZE[0]//2, 200))
        start_text = FONT_SMALL.render("PRESS ANY BUTTON TO START", True, WHITE)
        if (self.is_visible and self.fade_in_stage == 0):
            self.window.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 800))
        
    def draw_backgrounds(self):
        """
        Draws the backgrounds of the game (main background, side panels).
        """
        self.window.blit(BOARD_BACKGROUND, (SIDE_WIDTH, 0))
        for y in range((int(CORE_HEIGHT/SIDE_WIDTH))):
            self.window.blit(SIDE_BACKGROUND, (0, SIDE_WIDTH*y))
            self.window.blit(SIDE_BACKGROUND, (SIDE_WIDTH + CORE_WIDTH, SIDE_WIDTH*y))
        
    
    def draw_board(self, current_block, ghost_block, board, width, height):
        """
        Draws the Tetris game board on the screen.
        
        Args:
            current_block (TetrisBlock): The current block being played.
            ghost_block (TetrisBlock): The ghost block that shows where the current block will land.
            board (list): A 2D list representing the Tetris board.
            width (int): The width of the board.
            height (int): The height of the board.
        """
        shape_name, coords = current_block
        top_left_x, top_left_y = BOARD_TOP_LEFT
        
        # Blocks
        for block in coords:
            self.window.blit(BLOCK_GRAPHICS[shape_name], (block.x + top_left_x, block.y + top_left_y))
        for x, y in product(range(width), range(height)):
            if board[y][x]:
                self.window.blit(BLOCK_GRAPHICS[board[y][x]], 
                                 (top_left_x + x*BLOCK_SIZE, top_left_y + (y-4)*BLOCK_SIZE))
        for x, y in ghost_block.coords:
            self.window.blit(GHOST, (top_left_x + x*BLOCK_SIZE, top_left_y + (y-4)*BLOCK_SIZE))
            
        # Border to go over shapes
        self.window.blit(BORDER, (SIDE_WIDTH, 0))
        
        
    def draw_side_modules(self, held_block, just_held, queue, level, score, prev_clear):
        """
        Draws the side modules of the game (level, held block, score, queue).
        
        Args:
            held_block (TetrisBlock): The block currently being held.
            just_held (bool): Whether the block was just held.
            queue (list): A list of upcoming blocks.
            level (int): The current level of the game.
            score (int): The current score of the game.
            prev_clear (int): The number of lines cleared in the previous turn.
        """
        
        # Queue blocks
        for i, piece in enumerate(queue):
            self.window.blit(PIECE_GRAPHICS[piece.shape_name], (SIDE_WIDTH + CORE_WIDTH + 65, (BLOCK_SIZE+QUEUE_SPACING)*i + 120))
        
        # Text
        level_text = FONT_BIG.render(f'LEVEL {level}', True, WHITE)
        score_text = FONT_SMALL_ITALIC.render(f'score: {score}', True, WHITE)
        queue_text = FONT_BIG.render('NEXT:', True, WHITE)
        self.window.blit(level_text, (30, 40))
        self.window.blit(score_text, (SIDE_WIDTH + CORE_WIDTH + 40, 20))
        self.window.blit(queue_text, (SIDE_WIDTH + CORE_WIDTH + 40, 70))
        
        # Hold
        if (held_block != None):
            if just_held:
                self.window.blit(PIECE_GRAPHICS_GREY[held_block.shape_name], (50, 120))
            else:
                self.window.blit(PIECE_GRAPHICS[held_block.shape_name], (50, 120))
        hold_text = FONT_SMALL_ITALIC.render('on hold', True, WHITE)
        if (held_block != None and self.is_visible):
            self.window.blit(hold_text, (60, 100))
            pygame.draw.circle(self.window, RED, (40, 125), 8*SCALE)
            
        # B2B text
        b2b_text = FONT_BIG_ITALIC.render(F'B2B ×{prev_clear - 4}', True, GOLD)
        if (prev_clear > 4):
            self.window.blit(b2b_text, (40, 260))
        
        
    def draw_game_screen(self, game):
        """
        Draws the entire game.
        
        Args:
            game (TetrisGame): The Tetris game object.
        """
        self.draw_backgrounds()
        self.draw_board(self.get_render_block(game.current_block), 
                        game.get_ghost_block(), 
                        game.board.board, 
                        game.width, 
                        game.height)
        self.draw_side_modules(game.held_block,
                               game.just_held,
                               game.queue, 
                               game.get_current_level(),
                               game.score,
                               game.prev_clear)
    

class TetrisPyGame:
    
    # TODO: Game over, main menu, pause menu, refactor globals, fix game crashing when block pokes out top, error handling. Screen shake? Check window class?
    # Options: Starting speed, progression speed, different soft drop lock speed, sprint mode. Credits, Keybinds extc.
    
    def __init__(self):
        self.init_globals()
        self.init_settings()
        

    def init_globals(self):
        """
        Initializes global variables for the game.
        """
        self.game = Tetris()
        self.window = TetrisPyGameWindow()
        self.clock = pygame.time.Clock()
        self.run = True
        self.game_started = False
        self.prev_level = 1
        self.time_last_moved = 0
        self.music_ticker = 0
        self.prev = time()
        
        
    def init_settings(self):
        """
        Initializes settings for the game.
        """
        self.reset_move_down_interval()
        self.clock.tick(FPS)
        pygame.display.set_caption("TETRIS, BABY")
        pygame.key.set_repeat(135, 35)
        

    def draw_window(self):
        """
        Draws the game window. Called on each iteration of the main loop.
        """
        if (not self.game_started):
            self.window.draw_start_screen() 
        else:                            
            self.window.draw_game_screen(self.game)
            
        pygame.display.update()
        
        
    def play_music(self, song):
        """
        Plays music in the game.
        
        Args:
            song (str): The path to the music file.
        """
        mixer.music.load(song)
        mixer.music.play(3)
        
    
    def reset_move_down_interval(self):
        """
        Resets the move down interval. Interval changes based on level, according to the function in the Tetris class.
        """
        t = int(self.game.get_move_time_interval()*1000)
        pygame.time.set_timer(MOVE_DOWN_EVENT, t)
        
        
    def check_level_change(self):
        """
        Checks if the level has changed.
        
        Returns:
            bool: True if the level has changed, False otherwise.
        """
        return self.prev_level != self.game.get_current_level()
    
    
    def check_music_event(self, change_level):
        """
        Checks if a music event has occurred.
        
        Args:
            change_level (int): The level at which the music changes.
            
        Returns:
            bool: True if a music event has occurred, False otherwise.
        """
        current_level = self.game.get_current_level()
        return self.check_level_change() and (current_level == change_level or (current_level == change_level+1 and self.prev_level == change_level-1))
        
    
    def start_screen_loop(self, events):
        """
        Handles events on the start screen.
        
        Args:
            events (list): A list of Pygame events.
        """
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                event.post(event.Event(pygame.QUIT))
            elif (event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]):
                self.game_started = True
                self.play_music(TETRIS_A)
                mixer.music.set_volume(0.1)
                self.reset_move_down_interval
                    
                    
    def handle_move_down_event(self):  
        """
        Handles the move down event. Moves the current block down and checks for collisions.
        """      
        if (self.game.check_y_collision(self.game.current_block) and (time() - self.time_last_moved) >= self.game.get_lock_time_interval()):
            # Place and lock block
            self.game.place_block()
            SOUNDS["SOFT_DROP_SOUND"].play()
            self.time_last_moved = time()
        elif (not self.game.check_y_collision(self.game.current_block)):
            # Just move block down by one
            self.game.move_down(self.game.current_block)
            self.time_last_moved = time()
        
    
    def handle_game_state_events(self, events, keys_pressed):
        """
        Handles game state events - key presses and line clears.
        
        Args:
            events (list): A list of Pygame events.
            keys_pressed (list): A list of pressed keys.
        """
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key in GAMEPLAY_KEYS):
                
                if (event.key == pygame.K_ESCAPE):
                    event.post(event.Event(pygame.QUIT))
                    
                if (event.key == pygame.K_LEFT):
                    self.game.move_x(self.game.current_block, True)
                    SOUNDS["MOVE_X_SOUND"].play()

                if (event.key == pygame.K_RIGHT):
                    self.game.move_x(self.game.current_block, False)
                    SOUNDS["MOVE_X_SOUND"].play()

                if (event.key == pygame.K_UP):
                    self.game.hard_drop()
                    SOUNDS["HARD_DROP_SOUND"].play()

                if (event.key == pygame.K_z):
                    self.game.current_block.rotate(self.game.width, self.game.height, self.game.board.board, False)
                    SOUNDS["ROTATE_SOUND"].play()

                if (event.key == pygame.K_x):
                    self.game.current_block.rotate(self.game.width, self.game.height, self.game.board.board, True)
                    SOUNDS["ROTATE_SOUND"].play()

                if (event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT] and not self.game.just_held):
                    self.game.hold_block()
                    SOUNDS["HOLD_SOUND"].play()
                    
                self.time_last_moved = time()
        
        if (keys_pressed[pygame.K_DOWN]):
            self.game.move_down(self.game.current_block)  
            self.reset_move_down_interval()
            SOUNDS["MOVE_Y_SOUND"].play()
            
        if (self.game.check_cleared_lines()):
            self.handle_line_clear_event()
            
                
    def handle_line_clear_event(self):
        """
        Handles line clear events, clearing full lines and updating the score.
        """
        cleared_lines = self.game.get_cleared_lines()
        if (self.game.prev_clear > 4 and len(cleared_lines) < 4):
            SOUNDS["B2B_BREAK_SOUND"].play()
            self.game.clear_lines(cleared_lines)
        else:
            self.game.clear_lines(cleared_lines)
            CLEAR_SOUNDS[min(self.game.prev_clear, 8)].play()
            
            
    def handle_level_up_event(self):
        """
        Handles the level up event, increasing the level and updating the game speed.
        """
        SOUNDS["LEVEL_UP_SOUND"].play()
        self.reset_move_down_interval()
        self.prev_level = self.game.get_current_level()
            
    
    def handle_music_event(self):
        """
        Handles the music event, changing the music based on the current level.
        """
        self.music_ticker += 1
        mixer.music.fadeout(5000)
        
                
    def check_game_events(self):
        """
        Checks for new game events.
        """
        if (self.check_music_event(MUSIC_CHANGE_LEVEL_1) or self.check_music_event(MUSIC_CHANGE_LEVEL_2)):
            event.post(event.Event(MUSIC_EVENT))
        if self.check_level_change():
            event.post(event.Event(LEVEL_UP_EVENT))
    
            
    def handle_game_events(self, events, keys_pressed):
        """
        Handles main game events: key presses, level ups, music changes.
        
        Args:
            events (list): A list of Pygame events.
            keys_pressed (list): A list of pressed keys.
        """
        event_types = [event.type for event in events]
        if (MOVE_DOWN_EVENT in event_types):
            self.handle_move_down_event()
        if (pygame.KEYDOWN in event_types or keys_pressed != []):
            self.handle_game_state_events(events, keys_pressed)
        if (LEVEL_UP_EVENT in event_types):
            self.handle_level_up_event()
        if (MUSIC_EVENT in event_types):
            self.handle_music_event()
            
        # Use music.get_bsuy()?
        if (self.music_ticker not in [0, 150, 300]):
            self.music_ticker += 1
        if (self.music_ticker == 149):
            self.play_music(TETRIS_B)
        if (self.music_ticker == 299):
            self.play_music(GOD_SHATTERING_STAR)
        
    
     
    def game_loop(self, events):
        """
        Runs the main game loop.
        
        Args:
            events (list): A list of Pygame events.
        """
        
        self.check_game_events()
        self.handle_game_events(events, pygame.key.get_pressed())
    
    
    def handle_global_events(self, events):
        """
        Handles global events.
        
        Args:
            events (list): A list of Pygame events.
        """
        event_types = [event.type for event in events]
            
        # Global events
        if (pygame.QUIT in event_types):
            self.run = False
        if (BLINK_EVENT in event_types):
            self.window.is_visible = not self.window.is_visible
        
        
        
    def main_loop(self):
        """
        Runs the main game loop.
        """
        
        pygame.time.set_timer(BLINK_EVENT, 500)
        
        while self.run:
            
            self.draw_window()
            events = event.get()
            
            self.handle_global_events(events)
            
            if (not self.game_started):
                self.start_screen_loop(events)
            else:
                self.game_loop(events)
                
                    
        pygame.quit()


def main():
    gui = TetrisPyGame()
    gui.main_loop()
    
    
    
if __name__ == "__main__":
    main()