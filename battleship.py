import pygame
from pygame.locals import *
import time
import os
import re
import random 
import sys


# pygame setup constants
BOARD_SIZE = 10
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 700
FPS = 60
BTN_WIDTH = 400
BTN_HEIGHT = 80
font_path = "AI-battlefield/others/upheavtt.ttf"
#font_path = "Battlefield/AI-battlefield/others/upheavtt.ttf"
COLOR_inner = '#E5E5E5' # light white
COLOR_back = "#EEEEEE"
COLOR_opp = "#DFD2D7"
COLOR_lining = "#90a7c6"#296270" #4849B1"
COLOR_hover = "#B8C4CECF"
COLOR_font = "#4f7d92" #133844"
COLOR_main = "#a9d6e4" # #ADCCDA # "#C2DCEB"
COLOR_btn = "#5096a7"
COLOR_btn_font = "#c6e1f3"
CELL_SIZE = 30 # px
AI_PLAYER = 0
AI_AI = 1

class Ships:
    def __init__(self, img, pos, length=1, horizontal=True):
        self.length = length
        self.horizontal = horizontal
        if horizontal:
            self.image = pygame.transform.scale(img, (CELL_SIZE * length, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE * length))
        self.rect = self.image.get_rect(topleft=pos)
        self.image = pygame.transform.scale(img, (CELL_SIZE * length, CELL_SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.original_pos = pos

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def reset_position(self):
        self.rect.topleft = self.original_pos



def ship_events(ships, event, board, board_offset_x, board_offset_y):
        mouse_pos = pygame.mouse.get_pos()
        hovering_any = False

        for ship in reversed(ships):
            # Cursor change
            if ship.rect.collidepoint(mouse_pos): # CHECK THISSS
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                hovering_any = True
                # Drag start
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    ship.dragging = True
                    ship.offset_x = ship.rect.x - mouse_pos[0]
                    ship.offset_y = ship.rect.y - mouse_pos[1]
                    ships.remove(ship)
                    ships.append(ship)
                    break 

            # Drag & drop
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and ship.dragging:
                ship.dragging = False
                # Snap to grid horizontally
                grid_x = (ship.rect.x - board_offset_x + CELL_SIZE//2) // CELL_SIZE
                grid_y = (ship.rect.y - board_offset_y + CELL_SIZE//2) // CELL_SIZE

                grid_x = max(0, min(10- (ship.length if ship.horizontal else 1), grid_x))
                grid_y = max(0, min(10 - (1 if ship.horizontal else ship.length), grid_y))

                
                collision = False
                for other in ships:
                    if other == ship:
                        continue
                    if ship.horizontal:
                        ship_rect_cells = [(grid_x+i, grid_y) for i in range(ship.length)]
                    else:
                        ship_rect_cells = [(grid_x, grid_y+i) for i in range(ship.length)]
                    if other.horizontal:
                        other_cells = [( (other.rect.x - board_offset_x)//CELL_SIZE + i, (other.rect.y - board_offset_y)//CELL_SIZE ) 
                                    for i in range(other.length)]
                    else:
                        other_cells = [( (other.rect.x - board_offset_x)//CELL_SIZE, (other.rect.y - board_offset_y)//CELL_SIZE + i ) 
                                    for i in range(other.length)]
                    if any(cell in other_cells for cell in ship_rect_cells):
                        collision = True
                        break

                # Place ship if no collision
                if 0 <= grid_x < 10 and 0 <= grid_y < 10 and not collision:
                    ship.rect.x = board_offset_x + grid_x * CELL_SIZE
                    ship.rect.y = board_offset_y + grid_y * CELL_SIZE
                else:
                    ship.reset_position()

            elif event.type == pygame.MOUSEMOTION and ship.dragging:
                ship.rect.x = mouse_pos[0] + ship.offset_x
                ship.rect.y = mouse_pos[1] + ship.offset_y

        if not hovering_any:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

def buttons_template(width, height, color):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)  # allows transparency
    pygame.draw.rect(surf, color, surf.get_rect(), border_radius=12)
    return surf

def button(text, y_offset, screen, font, color=COLOR_btn):
    screen_w, screen_h = pygame.display.get_surface().get_size()
    width, height = 220, 65  # button size
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, surf.get_rect(), border_radius=12)

    # render text
    txt = font.render(text, True, (0,0,0))
    txt_rect = txt.get_rect(center=(width//2, height//2))
    surf.blit(txt, txt_rect)

    # center horizontally, shifted vertically
    rect = surf.get_rect(center=(screen_w//2, screen_h//2 + y_offset))
    screen.blit(surf, rect)

    return rect 


pygame.init()


# for sprite and image handling
imgs = {}   # dictionary for loaded images
ships = []

images_path = [
    ("playBtn", "AI-battlefield\sprites\PlayButton.png", "A"),
    ("background", "AI-battlefield\sprites\Background.png", "C"),
    ("mouse", "AI-battlefield\sprites\CursorDefault.png", "A"),
    ("mouseP", "AI-battlefield\sprites\CursorPoint.png", "A"),
    ("mouseG", "AI-battlefield\sprites\CursorGrab.png", "A"),
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
'''

def create_board(size, def_value=' '): # ~ for water
    return [[def_value for _ in range(size)] for _ in range(size)] # 2D matrix grid

player_board = create_board(BOARD_SIZE)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE) # pygame.FULLSCREEN
pygame.display.set_caption("Battleship")
font = pygame.font.Font(font_path, size=18)
spacing = 20

# Image loading
for name, path, CA in images_path:
    try:
        if CA == "C":
            imgs[name] = pygame.image.load(path).convert()           
        elif CA == "A":
            imgs[name] = pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"Error. Failed to load {path}: {e}")
        pygame.quit()

cursor_hand = pygame.cursors.Cursor((0,0), imgs["mouseP"])

clock = pygame.time.Clock()
clock.tick(FPS)
pygame.mouse.set_visible(False)
pygame.display.flip()


def ingame_board(surface, board, leftRight, colorgrid, font, mode, screen_part="top"):
    rows = len(board)
    cols = len(board[0])
    screen_w, screen_h = pygame.display.get_surface().get_size()
    grid_w = cols * CELL_SIZE
    grid_h = rows * CELL_SIZE
    margin_x = screen_w // 5 
    margin_y = screen_h // 8
    spacing = 150

    # Decide offsets based on position
    if screen_part == "top":
        base_y = margin_y
    elif screen_part == "bottom":
        half_h = screen_h // 2
        base_y = half_h + spacing // 2
    else:
        base_y = margin_y
    
    if leftRight == "L":
        offset_x, offset_y = margin_x, base_y
    elif leftRight == "R":
        offset_x, offset_y = screen_w - grid_w - margin_x, base_y
    else:
        return  None, None
     
    for i, row in enumerate(board):
            for j, cell in enumerate(row):
                rectangle = pygame.Rect(offset_x + j*CELL_SIZE, offset_y + i*CELL_SIZE, CELL_SIZE, CELL_SIZE,border_radius = 8)
                pygame.draw.rect(surface, colorgrid, rectangle, border_radius = 6)
                pygame.draw.rect(surface, COLOR_lining, rectangle, 1,  border_radius = 6)
    
            if cell == "ship":
                pygame.draw.rect(surface, (60, 60, 60), rectangle)
            elif cell == "hit":
                pygame.draw.circle(surface, (200,0,0), rectangle.center, CELL_SIZE//3)
            elif cell == "miss":
                pygame.draw.circle(surface, (0,0,200), rectangle.center, CELL_SIZE//5)

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
        return  

    row, col = hover_cell
    # temporary surface with per-pixel alpha
    hover_surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    hover_surf.fill(color)
    # pixel position on the screen
    x = offset_x + col * cell_size
    y = offset_y + row * cell_size
    surface.blit(hover_surf, (x, y))


def background_blocks(width, height):
    screen_w, screen_h = screen.get_size()

    # Optional: leave some margin from window edges
    margin_x = screen_w // 20
    margin_y = screen_h // 12

    # width and height cover most of the screen
    width = screen_w - 2 * margin_x
    height = screen_h - 2 * margin_y

    rect = pygame.Rect(0, 0, width, height)
    rect.center = (screen_w // 2, screen_h // 2)

    pygame.draw.rect(screen, pygame.Color(COLOR_back), rect, border_radius=18)


def init_fleet():
    ships.clear()
    spacing_x = 20
    spacing_y = 20

    # Divide ships into two rows
    ship_items = [ (name, img) for name, img in imgs.items() if re.match(r'[A-Za-z]*([0-9]+)$', name) ]
    half = (len(ship_items) + 1) // 2

    # First row
    current_x = 50
    current_y = SCREEN_HEIGHT - 150
    for name, img in ship_items[:half]:
        length = int(re.match(r'[A-Za-z]*([0-9]+)$', name).group(1))
        ship = Ships(img, (current_x, current_y), length)
        ships.append(ship)
        current_x += CELL_SIZE * length + spacing_x

    # Second row
    current_x = 50
    current_y = SCREEN_HEIGHT - 80
    for name, img in ship_items[half:]:
        length = int(re.match(r'[A-Za-z]*([0-9]+)$', name).group(1))
        ship = Ships(img, (current_x, current_y), length)
        ships.append(ship)
        current_x += CELL_SIZE * length + spacing_x


def menu():
    button_pvai_rect = button("Player vs AI", -80, screen, font)
    button_aivai_rect = button("AI vs AI", 0, screen, font)
    button_quit_rect = button("Exit", 80, screen, font)

    running = True
    while True:
        screen.blit(imgs["background"], (0,0))
        mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_visible(False)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_pvai_rect.collidepoint(mouse_pos):
                    return AI_PLAYER
                elif button_aivai_rect.collidepoint(mouse_pos):
                    return AI_AI
                elif button_quit_rect.collidepoint(mouse_pos):
                    pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # Draw text on buttons
        pvai_color = COLOR_hover if button_pvai_rect.collidepoint(mouse_pos) else COLOR_btn
        aivai_color = COLOR_hover if button_aivai_rect.collidepoint(mouse_pos) else COLOR_btn
        quit_color = COLOR_hover if button_quit_rect.collidepoint(mouse_pos) else COLOR_btn
        button_pvai_rect = button("Player vs AI", -80, screen, font, color=pvai_color)
        button_aivai_rect = button("AI vs AI", 0, screen, font, color=aivai_color)
        button_quit_rect = button("Exit", 80, screen, font, color=quit_color)

        pvai_label = font.render("Player vs AI", True, COLOR_btn_font)
        aivai_label = font.render("AI vs AI", True, COLOR_btn_font)
        quit_label = font.render("Exit", True, COLOR_btn_font)

        screen.blit(pvai_label, (button_pvai_rect.centerx - pvai_label.get_width()//2,
                                 button_pvai_rect.centery - pvai_label.get_height()//2))
        screen.blit(aivai_label, (button_aivai_rect.centerx - aivai_label.get_width()//2,
                                  button_aivai_rect.centery - aivai_label.get_height()//2))
        screen.blit(quit_label, (button_quit_rect.centerx - quit_label.get_width()//2,
                                  button_quit_rect.centery - quit_label.get_height()//2))

        x, y = pygame.mouse.get_pos()
        x -= imgs["mouse"].get_width() // 2
        y -= imgs["mouse"].get_height() // 2
        screen.blit(imgs["mouse"], (x,y))
        
        pygame.display.flip()
        clock.tick(60)


# -----------------------------------------------------------

def main_game(mode):
    init_fleet()

    # GAME GAME


    # EXECUTION
    running = True
    while running:
        # loads background and mouse
        screen.blit(imgs["background"], (0,0))
        background_blocks(1050, 550)
        pygame.mouse.set_visible(False)
        
        if mode == 0: # player_ai
            offset_px1, offset_py1 = ingame_board(screen, player_board, 'L', COLOR_main, font, mode=True, screen_part="top")
            offset_px2, offset_py2 = ingame_board(screen, player_board, 'R', COLOR_opp, font, mode=False, screen_part="top")
        elif mode == 1: # ai_ai
            offset_px1, offset_py1 = ingame_board(screen, player_board, 'L', COLOR_main, font, mode=True, screen_part="top")
            offset_px2, offset_py2 = ingame_board(screen, player_board, 'R', COLOR_opp, font, mode=True, screen_part="top")
            offset_px3, offset_py3 = ingame_board(screen, player_board, 'L', COLOR_main, font, mode=True, screen_part="bottom")
            offset_px4, offset_py4 = ingame_board(screen, player_board, 'R', COLOR_opp, font, mode=True, screen_part="bottom")

        for event in pygame.event.get():
            # EVENT HANDLING
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mode = menu()

            # DRAGGING SHIPS
            ship_events(ships, event, player_board, offset_px1, offset_py1)

        
            # loads background and mouse
            screen.blit(imgs["background"], (0,0))
            background_blocks(1050, 550)
            pygame.mouse.set_visible(False)

            if mode == 0: # player_ai
                offset_px1, offset_py1 = ingame_board(screen, player_board, 'L', COLOR_main, font, mode=True, screen_part="top")
                offset_px2, offset_py2 = ingame_board(screen, player_board, 'R', COLOR_opp, font, mode=False, screen_part="top")
            elif mode == 1: # ai_ai
                offset_px1, offset_py1 = ingame_board(screen, player_board, 'L', COLOR_main, font, mode=True, screen_part="top")
                offset_px2, offset_py2 = ingame_board(screen, player_board, 'R', COLOR_opp, font, mode=True, screen_part="top")
                offset_px3, offset_py3 = ingame_board(screen, player_board, 'L', COLOR_main, font, mode=True, screen_part="bottom")
                offset_px4, offset_py4 = ingame_board(screen, player_board, 'R', COLOR_opp, font, mode=True, screen_part="bottom")

            for ship in ships:
                ship.draw(screen)

            x, y = pygame.mouse.get_pos()
            hover_1 = get_hover_cell(x, y, player_board, offset_px1, offset_py1)
            hover_2 = get_hover_cell(x, y, player_board, offset_px2, offset_py2)
            draw_hover(screen, hover_1, cell_size=CELL_SIZE, offset_x=offset_px1, offset_y=offset_py1)
            draw_hover(screen, hover_2, cell_size=CELL_SIZE, offset_x=offset_px2, offset_y=offset_py2)
            cx = x-imgs["mouse"].get_width() // 2
            cy = y-imgs["mouse"].get_height() // 2
            screen.blit(imgs["mouse"], (cx,cy))
    
            pygame.display.flip()

    pygame.quit()

mode = menu()
main_game(mode)
pygame.quit()