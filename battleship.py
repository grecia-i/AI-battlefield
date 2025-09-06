import pygame
from pygame.locals import *
import time
import os
import re
import random 
from sys import exit

# pygame setup constants
BOARD_SIZE = 10
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 700
FPS = 60
#font_path = "AI-battlefield/others/upheavtt.ttf"
font_path = "Battlefield/AI-battlefield/others/upheavtt.ttf"
COLOR_inner = '#E5E5E5' # light white
COLOR_back = "#EEEEEE"
COLOR_opp = "#DFD2D7"
COLOR_lining = "#90a7c6"#296270" #4849B1"
COLOR_hover = "#B8C4CE"
COLOR_font = "#4f7d92" #133844"
COLOR_main = "#a9d6e4" # #ADCCDA # "#C2DCEB"
COLOR_btn = "#5096a7"
COLOR_btn_font = "#c6e1f3"
CELL_SIZE = 35 # px

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

def buttons(width, height, color):
    """
    color = COLOR_hover if rect.collidepoint(mouse) else COLOR_btn
    pygame.draw.rect(screen, color, rect, border_radius=12)
    label = font.render(text, True, COLOR_font)
    screen.blit(label,
        (   rect.x + rect.width // 2 - label.get_width() // 2,
            rect.y + rect.height // 2 - label.get_height() // 2
        )
    )
    """
    surf = pygame.Surface((width, height), pygame.SRCALPHA)  # allows transparency
    pygame.draw.rect(surf, color, surf.get_rect(), border_radius=12)
    return surf

pygame.init()

BUTTON_WIDTH = 400
BUTTON_HEIGHT = 80
button_pvai_surf = buttons(BUTTON_WIDTH, BUTTON_HEIGHT, COLOR_btn)
button_aivai_surf = buttons(BUTTON_WIDTH, BUTTON_HEIGHT, COLOR_btn)

# Button positions
button_pvai_rect = button_pvai_surf.get_rect(center=(SCREEN_WIDTH//2, 300))
button_aivai_rect = button_aivai_surf.get_rect(center=(SCREEN_WIDTH//2, 450))

AI_PLAYER = 0
AI_AI = 1

# for sprite and image handling
imgs = {}   # dictionary for loaded images
ships = []
'''
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
'''
images_path = [
    ("playBtn", "Battlefield\AI-battlefield\sprites\PlayButton.png", "A"),
    ("background", "Battlefield\AI-battlefield\sprites\Background.png", "C"),
    ("mouse", "Battlefield\AI-battlefield\sprites\CursorDefault.png", "A"),
    ("patrolBoat2", "Battlefield\AI-battlefield\sprites\patrolBoat2.png", "A"),
    ("cruiser3", "Battlefield\AI-battlefield\sprites\Cruiser3.png", "A"),
    ("submarine3", "Battlefield\AI-battlefield\sprites\Submarine3.png", "A"),
    ("battle4", "Battlefield\AI-battlefield\sprites\Battleship4.png", "A"),
    ("carrier5", "Battlefield\AI-battlefield\sprites\Carrier5.png", "A")
]

def create_board(size, def_value=' '): # ~ for water
    return [[def_value for _ in range(size)] for _ in range(size)] # 2D matrix grid

player_board = create_board(BOARD_SIZE)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE) # pygame.FULLSCREEN
pygame.display.set_caption("Battleship")
font = pygame.font.Font(font_path, size=18)

# Image loading
for name, path, CA in images_path:
    try:
        if CA == "C":
            imgs[name] = pygame.image.load(path).convert()           
        elif CA == "A":
            imgs[name] = pygame.image.load(path).convert_alpha()
            match = re.match(r'[a-z]*[A-Z]*[a-z]*([0-9]+)$', name)            
            if match:
                length = int(match.group(1))  # extract number at the end
                ship = Ships(imgs[name], (50, SCREEN_HEIGHT-100), length)
                ships.append(ship)
                #start_x += CELL_SIZE + 20
    except pygame.error as e:
        print(f"Error. Failed to load {path}: {e}")
        pygame.quit()

clock = pygame.time.Clock()
clock.tick(FPS)
pygame.mouse.set_visible(False)
pygame.display.flip()


def ingame_board(surface, board, leftRight, colorgrid, font, mode):
    """
    if leftRight == 'L':
        offset_x = (SCREEN_WIDTH - 950) // 2   # 500: CELLS TOP * PIXELS
        offset_y = (SCREEN_HEIGHT - 450) // 2  
    elif leftRight == 'R':
        offset_x = (SCREEN_WIDTH + 150) // 2   # 500: CELLS TOP * PIXELS
        offset_y = (SCREEN_HEIGHT - 450) // 2 
    else:
        return
    """
    base_x = (SCREEN_WIDTH - 950) // 2
    base_y = (SCREEN_HEIGHT - 450) // 2
    spacing_x = 650   # distance between left/right boards
    spacing_y = 550   # distance between top/bottom boards

    # Decide offsets based on position
    if leftRight == "TL":
        offset_x, offset_y = base_x, base_y
    elif leftRight == "TR":
        offset_x, offset_y = base_x + spacing_x, base_y
    elif leftRight == "BL":
        offset_x, offset_y = base_x, base_y + spacing_y
    elif leftRight == "BR":
        offset_x, offset_y = base_x + spacing_x, base_y + spacing_y
    else:
        return  # invalid position
     
    for i, row in enumerate(board):
            for j, cell in enumerate(row):
                rectangle = pygame.Rect(offset_x + j*CELL_SIZE, offset_y + i*CELL_SIZE, CELL_SIZE, CELL_SIZE,border_radius = 8)
                pygame.draw.rect(surface, colorgrid, rectangle, border_radius = 6)
                pygame.draw.rect(surface, COLOR_lining, rectangle, 1,  border_radius = 6)
    
            if cell == "ship" and mode:
                pygame.draw.rect(surface, (60, 60, 60), rect)  # ship shown
            elif cell == "hit":
                pygame.draw.circle(surface, (200, 0, 0), rect.center, CELL_SIZE//3)
            elif cell == "miss":
                pygame.draw.circle(surface, (0, 0, 200), rect.center, CELL_SIZE//5)


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


def all_boards(surface, player_board, ai_board, colorgrid, font, mode="player_vs_ai"):
    # --- Top row ---
    ingame_board(surface, player_board, "TL", colorgrid, font, mode=True)
    if mode == "player_vs_ai":
        ingame_board(surface, ai_board, "TR", colorgrid, font, mode=False)
    else:  # ai_vs_ai
        ingame_board(surface, ai_board, "TR", colorgrid, font, mode=True)

    # --- Bottom row only in AI vs AI ---
    if mode == "ai_vs_ai":
        ingame_board(surface, player_board, "BL", colorgrid, font, mode=True)
        ingame_board(surface, ai_board, "BR", colorgrid, font, mode=True)



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

def menu():
    running = True
    while True:
        screen.blit(imgs["background"], (0,0))
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_pvai_rect.collidepoint(mouse_pos):
                    return AI_PLAYER
                elif button_aivai_rect.collidepoint(mouse_pos):
                    return AI_AI
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Draw text on buttons
        pvai_color = COLOR_hover if button_pvai_rect.collidepoint(mouse_pos) else COLOR_btn
        aivai_color = COLOR_hover if button_aivai_rect.collidepoint(mouse_pos) else COLOR_btn
        button_pvai_surf = buttons(BUTTON_WIDTH, BUTTON_HEIGHT, pvai_color)
        button_aivai_surf = buttons(BUTTON_WIDTH, BUTTON_HEIGHT, aivai_color)

        screen.blit(button_pvai_surf, button_pvai_rect)
        screen.blit(button_aivai_surf, button_aivai_rect)

        pvai_label = font.render("Player vs AI", True, COLOR_btn_font)
        aivai_label = font.render("AI vs AI", True, COLOR_btn_font)

        screen.blit(pvai_label, (button_pvai_rect.centerx - pvai_label.get_width()//2,
                                 button_pvai_rect.centery - pvai_label.get_height()//2))
        screen.blit(aivai_label, (button_aivai_rect.centerx - aivai_label.get_width()//2,
                                  button_aivai_rect.centery - aivai_label.get_height()//2))

        x, y = pygame.mouse.get_pos()
        x -= imgs["mouse"].get_width() // 2
        y -= imgs["mouse"].get_height() // 2
        screen.blit(imgs["mouse"], (x,y))
        
        pygame.display.flip()
        clock.tick(60)


# -----------------------------------------------------------

def main_game(mode):
    global imgs # Setting the window
    """
    # Update the display
    clock = pygame.time.Clock()
    clock.tick(FPS)
    pygame.mouse.set_visible(False)
    pygame.display.flip()
    """ 

    # GAME GAME



    # EXECUTION
    running = True
    while running:
        for event in pygame.event.get():
            # EVENT HANDLING
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mode = menu()

            # DRAGGING SHIPS


            # DROP PIECES


            # loads background and mouse
            screen.blit(imgs["background"], (0,0))

            background_blocks(1050, 550, screen)
            if mode == 0: # player_ai
                offset_px1, offset_py1 = ingame_board(screen, player_board, 'TL', COLOR_main, font, mode=True)
                offset_px2, offset_py2 = ingame_board(screen, player_board, 'TR', COLOR_opp, font, mode=False)
            elif mode == 1: # ai_ai
                offset_px1, offset_py1 = ingame_board(screen, player_board, 'TL', COLOR_main, font, mode=True)
                offset_px2, offset_py2 = ingame_board(screen, player_board, 'TR', COLOR_opp, font, mode=True)
                offset_px3, offset_py3 = ingame_board(screen, player_board, 'BL', COLOR_main, font, mode=True)
                offset_px4, offset_py4 = ingame_board(screen, player_board, 'BR', COLOR_opp, font, mode=True)

                        
            button_img = pygame.Surface((400, 80))
            button_img.fill((70, 130, 180))
            button_hover_img = pygame.Surface((400, 80))
            button_hover_img.fill((100, 180, 255))

            # Button positions
            button_pvai_rect = button_img.get_rect(center=(SCREEN_WIDTH//2, 300))
            button_aivai_rect = button_img.get_rect(center=(SCREEN_WIDTH//2, 450))

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

mode = menu()
main_game(mode)
pygame.quit()