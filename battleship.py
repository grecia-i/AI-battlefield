import pygame
from pygame.locals import *
import time
import os
import re
import random 
import sys
from board import Board
from settings import *
from ship import *

pygame.init()

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
    

# IMAGE HANDLING
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

# SETS UP THE WINDOW
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE) # pygame.FULLSCREEN
pygame.display.set_caption("Battleship")
font = pygame.font.Font(font_path, size=18)
font_big = pygame.font.Font(font_path, size=35)
spacing = 20

# IMAGE LOADING
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

# REFRESHES AND UPDATES 
clock = pygame.time.Clock()
clock.tick(FPS)
pygame.mouse.set_visible(False)
pygame.display.flip()


def background_blocks(width, height):
    screen_w, screen_h = screen.get_size()
    margin_x = screen_w // 20
    margin_y = screen_h // 12

    # width and height cover most of the screen
    width = screen_w - 2 * margin_x
    height = screen_h - 2 * margin_y

    rect = pygame.Rect(0, 0, width, height)
    rect.center = (screen_w // 2, screen_h // 2)

    pygame.draw.rect(screen, pygame.Color(COLOR_back), rect, border_radius=18)

def ship_sunk(ship_dict, board):
    return all(board.grid[r][c] == 'H' for r, c in ship_dict["coords"])

def main_message(text, duration=2, color=(255,0,0), font_size=64):
    font = pygame.font.Font(font_path, font_size)
    text = font.render(text, True, color)
    screen_w, screen_h = screen.get_size()
    x = screen_w//2 - text.get_width()//2
    y = screen_h//2 - text.get_height()//2
    screen.blit(text, (x, y))
    pygame.display.flip()
    pygame.time.delay(int(duration*1000)) 

def normal_message(text):
    message_log.append({"text": text, "time": pygame.time.get_ticks()})

def board_label(surface, text, offset_x, offset_y, cell_size, color='#90a7c6'):
    label = font.render(text, True, color)
    label_rect = label.get_rect(center=(offset_x + (cell_size * 10) // 2, offset_y + cell_size * 10 + 25))
    surface.blit(label, label_rect)

def player_label(surface, text, offset_x, offset_y, cell_size, color='#705b8b'):
    label = font_big.render(text, True, color)
    rotate = pygame.transform.rotate(label, 270)
    label_rect = rotate.get_rect(midleft=(offset_x + (cell_size * 10) + 20, offset_y + (cell_size * 10) // 2))
    surface.blit(rotate, label_rect)

# BOARD INITIALIZATION
player_boardL = Board(10)
player_boardR = Board(10)
ai_boardL = Board(10)
ai_boardR = Board(10)
ai_board_topL = Board(10)
ai_board_topR = Board(10)
ai_board_bottomL = Board(10)
ai_board_bottomR = Board(10)

message_log = []
current_time = pygame.time.get_ticks()

def menu():
    # INITIALIZES BUTTONS
    button_pvai_rect = button("Player vs AI", -80, screen, font)
    button_aivai_rect = button("AI vs AI", 0, screen, font)
    button_quit_rect = button("Exit", 80, screen, font)

    running = True
    while True:
        # BACKGROUND AND MOUSE LOADING
        screen.blit(imgs["background"], (0,0))
        mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_visible(False)

        # EVENT HANDLING
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

        # TEXT ON BUTTONS AND DRAWING
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

        # MOUSE HANDLING
        x, y = pygame.mouse.get_pos()
        x -= imgs["mouse"].get_width() // 2
        y -= imgs["mouse"].get_height() // 2
        screen.blit(imgs["mouse"], (x,y))
        
        # REFRESHES
        pygame.display.flip()
        clock.tick(60)


# -----------------------------------------------------------

def main_game(mode):
    # CLEARS AND INITIALIZES BOATS AGAIN
    ships.clear()
    message_log.clear()
    if mode == 0:
        init_fleet()
        init_fleet(ai_boardL)
        lock_btn = button("Lock Ships", 200, screen, font, color=COLOR_btn_decision) 
    else: 
        init_fleet(ai_board_topL)
        init_fleet(ai_board_bottomL)
    
    # GAME CONSTANTS
    ships_locked = False
    turn = "player1" # AI or human 
    game_over = False
    player_guessed = set()
    ai_guessed = set()
    player_ships_coords = []
    ai_ships_coords = []
    sunk_ai_ships = set()
    sunk_player_ships = set()

    # EXECUTION
    running = True
    while running:
        # BACKGROUND AND MOUSE LOADING
        screen.blit(imgs["background"], (0,0))
        background_blocks(1050, 550)
        pygame.mouse.set_visible(False)
        mouse_pos = pygame.mouse.get_pos()
        clock.tick(60)
        
        # BOARD AND LABELS DRAWING
        if mode == 0: # player_ai
            offset_px1, offset_py1 = player_boardL.ingame(
                screen, COLOR_main, font, leftRight='L', mode=True, screen_part="top")
            offset_px2, offset_py2 = player_boardR.ingame(
                screen, COLOR_opp, font, leftRight='R', mode=False, screen_part="top")
            board_label(screen, "PLACEMENT BOARD", offset_px1, offset_py1, CELL_SIZE)
            board_label(screen, "GUESSING BOARD", offset_px2, offset_py2, CELL_SIZE)
            #offset_px1, offset_py1 = ingame_board(screen, player_board, 'L', COLOR_main, font, mode=True, screen_part="top")
            #offset_px2, offset_py2 = ingame_board(screen, player_board, 'R', COLOR_opp, font, mode=False, screen_part="top")
            player_label(screen, "PLAYER 1", offset_px1, offset_py1, CELL_SIZE)
            
            lock_color = COLOR_hover if lock_btn.collidepoint(mouse_pos) else COLOR_btn
            lock_btn = button("Lock Ships", 200, screen, font, color=lock_color)
            lock_label = font.render("Lock Ships", True, COLOR_btn_font)
            screen.blit(lock_label, (lock_btn.centerx - lock_label.get_width()//2,
                                  lock_btn.centery - lock_label.get_height()//2))
        elif mode == 1: # ai_ai
            offset_px1, offset_py1 = ai_board_topL.ingame(screen, COLOR_main, font, leftRight='L', mode=True, screen_part="top")
            offset_px2, offset_py2 = ai_board_topR.ingame(screen, COLOR_opp, font, leftRight='R', mode=True, screen_part="top")
            offset_px3, offset_py3 = ai_board_bottomL.ingame(screen, COLOR_main, font, leftRight='L', mode=True, screen_part="bottom")
            offset_px4, offset_py4 = ai_board_bottomR.ingame(screen, COLOR_opp, font, leftRight='R',mode=True, screen_part="bottom")
            board_label(screen, "AI_1 PLACEMENT BOARD", offset_px1, offset_py1, CELL_SIZE)
            board_label(screen, "AI_1 GUESSING BOARD", offset_px2, offset_py2, CELL_SIZE)
            board_label(screen, "AI_2 PLACEMENT BOARD", offset_px3, offset_py3, CELL_SIZE)
            board_label(screen, "AI_2 GUESSING BOARD", offset_px4, offset_py4, CELL_SIZE)

            player_label(screen, "AI 1", offset_px1, offset_py1, CELL_SIZE)
            player_label(screen, "AI 2", offset_px3, offset_py3, CELL_SIZE)
    
        # SHIP DRAWING
        for ship in ships:
            if ship.grid_x is not None and ship.grid_y is not None:
                ship.rect.x = offset_px1 + ship.grid_x * CELL_SIZE
                ship.rect.y = offset_py1 + ship.grid_y * CELL_SIZE
            ship.draw(screen)
    

        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                mode = menu()
                # RESETS
                for b in [player_boardL, player_boardR,
                          ai_board_topL, ai_board_topR,
                          ai_board_bottomL, ai_board_bottomR]:
                    b.reset()
                ships.clear()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if lock_btn.collidepoint(mouse_pos):
                    
                    placed_ships = 0
                    for ship in ships:
                        start_x = (ship.rect.x - offset_px1) // CELL_SIZE
                        start_y = (ship.rect.y - offset_py1) // CELL_SIZE
                        # CHECKS IF SHIP IS IN THE BOUNDARIES OF THE GRID
                        if 0 <= start_x < 10 and 0 <= start_y < 10:
                            if ship.horizontal:
                                if start_x + ship.length <= 10:
                                    placed_ships += 1
                            else:
                                if start_y + ship.length <= 10:
                                    placed_ships += 1
                    
                    # CHECKS IF ALL SHIPS ARE LOCKED
                    if placed_ships == len(ships):
                        ships_locked = True
                        player_ships_coords.clear()
                        for ship in ships:
                            start_x = (ship.rect.x - offset_px1) // CELL_SIZE
                            start_y = (ship.rect.y - offset_py1) // CELL_SIZE
                            ship.place_on_grid(start_x, start_y, offset_px1, offset_py1)
                            coords = [(start_y, start_x+i) if ship.horizontal else (start_y+i, start_x) for i in range(ship.length)]
                            for r, c in coords:
                                player_boardL.grid[r][c] = 'ship'

                            player_ships_coords.append({"name": ship.name, "coords": coords})
                        normal_message("Ships locked!")

                        # PLACES AI SHIPS (CHANGE) !!!!!! 
                        ai_ships_coords.clear()
                        ai_boardR.reset()
                        for length in [5,4,3,3,2]:
                            placed = False
                            while not placed:
                                horizontal = random.choice([True, False])
                                row = random.randint(0, 9)
                                col = random.randint(0, 9)
                                coords = [(row, col+i) if horizontal else (row+i, col) for i in range(length)]
                                if all(0 <= r < 10 and 0 <= c < 10 and ai_boardR.grid[r][c]==' ' for r,c in coords):
                                    for r,c in coords:
                                        ai_boardR.grid[r][c] = 'ship'
                                    ai_ships_coords.append({"name": ship.name, "coords": coords})
                                    placed = True

                    else:
                        normal_message("Place all 5 ships before locking them!")
                        if len(message_log) > MAX_MESSAGES:
                            message_log.pop(0)
                
                # PLAYER ONE GUESSING
                if ships_locked and turn == "player1" and not game_over:
                    col = (mouse_pos[0] - offset_px2) // CELL_SIZE
                    row = (mouse_pos[1] - offset_py2) // CELL_SIZE
                    if 0 <= row < 10 and 0 <= col < 10 and (row,col) not in player_guessed:
                        player_guessed.add((row,col))
                        if ai_boardR.grid[row][col] == 'ship':
                            ai_boardR.grid[row][col] = 'H'
                            player_boardR.grid[row][col] = 'H'
                        else:
                            ai_boardR.grid[row][col] = 'M'
                            player_boardR.grid[row][col] = 'M'
                        normal_message(f"Player guessed ({row},{col})")
                        turn = "AI"

                        # SUNK SHIPS
                        for ship in ai_ships_coords:
                             if ship["name"] not in sunk_ai_ships and ship_sunk(ship, ai_boardR):
                                sunk_ai_ships.add(ship["name"])  # marcar como ya hundido
                                base_name = ''.join([c for c in ship["name"] if not c.isdigit()])
                                main_message(f"AI's {base_name} sunk!")
                        if all(ship_sunk(ship, ai_boardR) for ship in ai_ships_coords):
                            main_message("Player wins!")
                            message_log.clear()
                            game_over = True

            # AI TURN, IMPLEMENT YOUR FUNCTION IDK
            if ships_locked and turn == "AI" and not game_over:
                available = [(r, c) for r in range(10) for c in range(10) if (r, c) not in ai_guessed]
                if available:
                    row, col = random.choice(available)
                    ai_guessed.add((row,col))
                    if player_boardL.grid[row][col] == 'ship':
                        player_boardL.grid[row][col] = 'H'
                        normal_message(f"AI hit at ({row},{col})")
                    else:
                        player_boardL.grid[row][col] = 'M'
                        normal_message(f"AI missed at ({row},{col})")
                    turn = "player1"

                    for ship in player_ships_coords:
                        if ship["name"] not in sunk_player_ships and ship_sunk(ship, player_boardR):
                            sunk_player_ships.add(ship["name"])
                            base_name = ''.join([c for c in ship["name"] if not c.isdigit()])
                            main_message(f"Your {base_name} sunk!")
                    if all(ship_sunk(ship, player_boardL) for ship in player_ships_coords):
                        main_message("AI wins!")
                        message_log.clear()
                        game_over = True
                    
            if not ships_locked:
                ship_events(screen, ships, event, player_boardL, offset_px1, offset_py1)

        # MESSAGE DISPLAY
        screen_w, screen_h = screen.get_size()
        msg_x = 20
        msg_y_start = screen_h - 20  # start near bottom
        line_height = 18
        for i, msg in enumerate(reversed(message_log)):
            text_surf = font.render(msg["text"], True, (231, 226, 243))
            screen.blit(text_surf, (msg_x, msg_y_start - i * line_height))
        
        # MOUSE HANDLING
        x, y = pygame.mouse.get_pos()
        hover_1 = player_boardL.get_hover_cell(x, y)
        hover_2 = player_boardR.get_hover_cell(x, y)
        player_boardL.draw_hover(screen, hover_1, COLOR_hover)
        player_boardR.draw_hover(screen, hover_2, COLOR_hover)
        cx = x-imgs["mouse"].get_width() // 2
        cy = y-imgs["mouse"].get_height() // 2
        screen.blit(imgs["mouse"], (cx,cy))
    
        pygame.display.flip()

    pygame.quit()

mode = menu()
main_game(mode)
pygame.quit()