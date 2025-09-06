import pygame
from pygame.locals import *
import time
import os
import re
import random 
from sys import exit

# pygame setup constants
BOARD_SIZE = 10
SCREEN_WIDTH = 1480
SCREEN_HEIGHT = 780
FPS = 60
font_path = "AI-battlefield/others/upheavtt.ttf"
COLOR_inner = '#E5E5E5' # light white
COLOR_back = "#EEEEEE"
COLOR_opp = "#DFD2D7"
COLOR_lining = "#90a7c6"#296270" #4849B1"
COLOR_hover = "#B8C4CE"
COLOR_font = "#4f7d92" #133844"
COLOR_main = "#a9d6e4" # #ADCCDA # "#C2DCEB"
CELL_SIZE = 40 # px

class Ships:
    def __init__(self, img, pos, length=1):
        self.length = length
        self.image = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE * length))
        self.rect = self.image.get_rect(topleft=pos)
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

# for sprite and image handling
imgs = {}   # dictionary for loaded images
ships = []
images_path = [
    ("playBtn", "AI-battlefield\sprites\PlayButton.png", "A"),
    ("background", "AI-battlefield\sprites\Background.png", "C"),
    ("mouse", "AI-battlefield\sprites\CursorDefault.png", "A"),
    ("patrolBoat2", "AI-battlefield\sprites\patrolBoat2.png", "A"),
    ("cruiser3", "AI-battlefield\sprites\Cruiser3.png", "A"),
    ("submarine3", "AI-battlefield\sprites\Submarine3.png", "A"),
    ("battle4", "AI-battlefield\sprites\Battleship4.png", "A"),
    ("carrier5", "AI-battlefield\sprites\Carrier5.png", "A")
]

def create_board(size, def_value=' '): # ~ for water
    return [[def_value for _ in range(size)] for _ in range(size)] # 2D matrix grid

player_board = create_board(BOARD_SIZE)

def ingame_board(surface, board, leftRight, colorgrid, font):
    if leftRight == 'L':
        offset_x = (SCREEN_WIDTH - 950) // 2   # 500: CELLS TOP * PIXELS
        offset_y = (SCREEN_HEIGHT - 450) // 2  
    elif leftRight == 'R':
        offset_x = (SCREEN_WIDTH + 150) // 2   # 500: CELLS TOP * PIXELS
        offset_y = (SCREEN_HEIGHT - 450) // 2 
    else:
        return
    for i, row in enumerate(board):
            for j, cell in enumerate(row):
                rectangle = pygame.Rect(offset_x + j*CELL_SIZE, offset_y + i*CELL_SIZE, CELL_SIZE, CELL_SIZE,border_radius = 8)
                pygame.draw.rect(surface, colorgrid, rectangle, border_radius = 6)
                pygame.draw.rect(surface, COLOR_lining, rectangle, 1,  border_radius = 6)

    rows = len(board)
    cols = len(board[0])

    for i in range(rows):
        num_rows = font.render(chr(ord('@')+(i+1)), True, COLOR_font)
        x = offset_x - 25
        y = offset_y + i*CELL_SIZE + CELL_SIZE//2 - num_rows.get_height()//2
        surface.blit(num_rows, (x, y))
    for j in range(cols):
        num_cols = font.render(str(j+1), True, COLOR_font)
        x = offset_x + j*CELL_SIZE + CELL_SIZE//2 - num_cols.get_width()//2
        y = offset_y - 25
        surface.blit(num_cols, (x, y))
    
    return offset_x, offset_y

def get_hover_cell(x, y, board, offset_x, offset_y):
    # position the hover in the actual grid cell
    rows = len(board)
    cols = len(board[0])
    col = (x - offset_x) // CELL_SIZE
    row = (y - offset_y) // CELL_SIZE

    if 0 <= row < rows and 0 <= col < cols:
        return (row, col)
    return None


def draw_hover(surface, hover_cell, cell_size=CELL_SIZE, color=COLOR_hover, offset_x=0, offset_y=0):
    if hover_cell is None:
        return  # nothing to draw

    row, col = hover_cell

    # Create a temporary surface with per-pixel alpha
    hover_surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    hover_surf.fill(color)

    # Compute pixel position on the screen
    x = offset_x + col * cell_size
    y = offset_y + row * cell_size
    surface.blit(hover_surf, (x, y))


def background_blocks(width, height, screen):
    rect = pygame.Rect(0,0,width, height)
    rect.center = (screen.get_width() // 2, screen.get_height() // 2)
    pygame.draw.rect(screen, pygame.Color(COLOR_back), rect, border_radius=18)


def main():
    pygame.init()

    # Setting the window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # pygame.FULLSCREEN
    pygame.display.set_caption("Battleship")
    font = pygame.font.Font(font_path, size=18)

    # Image loading
    for name, path, CA in images_path: 
        try:
            if CA == "C":
                imgs[name] = pygame.image.load(path).convert()
                match = re.match(r'[a-z]*[A-Z]*[a-z]*([0-9]+)$', name)  # adjust logic as needed
                if match:
                    length = int(match.group(1))  # extract number at the end
                    ship = Ships(imgs[name], (50, SCREEN_HEIGHT-100), length)
                    ships.append(ship)
                    start_x += CELL_SIZE + 20
            elif CA == "A":
                imgs[name] = pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Error. Failed to load {path}: {e}")
            pygame.quit()

    # Update the display
    clock = pygame.time.Clock()
    clock.tick(FPS)
    pygame.mouse.set_visible(False)
    pygame.display.flip()

    # GAME GAME



    # EXECUTION
    running = True
    while running:
        for event in pygame.event.get():
            # EVENT HANDLING
            if event.type == pygame.QUIT:
                running = False
            
            # DRAGGING SHIPS


            # DROP PIECES


            # loads background and mouse
            screen.blit(imgs["background"], (0,0))

            background_blocks(1050, 550, screen)
            offset_px1, offset_py1 = ingame_board(screen, player_board, 'L', COLOR_main, font)
            offset_px2, offset_py2 = ingame_board(screen, player_board, 'R', COLOR_opp, font)
            
            x, y = pygame.mouse.get_pos()
            hover_1 = get_hover_cell(x, y, player_board, offset_px1, offset_py1)
            hover_2 = get_hover_cell(x, y, player_board, offset_px2, offset_py2)

            draw_hover(screen, hover_1, cell_size=CELL_SIZE, offset_x=offset_px1, offset_y=offset_py1)
            draw_hover(screen, hover_2, cell_size=CELL_SIZE, offset_x=offset_px2, offset_y=offset_py2)
            cx = x-imgs["mouse"].get_width() // 2
            cy = y-imgs["mouse"].get_height() // 2
            screen.blit(imgs["mouse"], (cx,cy))
    
            for ship in ships:
                ship.draw(screen)

            pygame.display.flip()


    pygame.quit()

# Quit pygame
# sys.exit()

if __name__ == "__main__":
    main()