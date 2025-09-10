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
from agents.srAgent import SimpleReflexAgent
from agents.gbAgent import GoalBasedAgent
import json

#STATS_FILE = "game_stats.json"
end_game_flag = False
game_stats = []

def save_stats(game_stats, filename="game_stats.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                all_stats = json.load(f)
            except json.JSONDecodeError:
                all_stats = []  # corrupted or empty file → reset
    else:
        all_stats = []

    all_stats.append(game_stats)

    with open(filename, "w") as f:
        json.dump(all_stats, f, indent=4)

pygame.init()

def button(text, y_offset, screen, font, color=COLOR_btn):
    screen_w, screen_h = pygame.display.get_surface().get_size()
    width, height = 380, 65  # button size
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
    ("Patrolboat2", "AI-battlefield\sprites\Patrolboat2.png", "A"),
    ("Cruiser3", "AI-battlefield\sprites\Cruiser3.png", "A"),
    ("Submarine3", "AI-battlefield\sprites\Submarine3.png", "A"),
    ("Battle4", "AI-battlefield\sprites\Battleship4.png", "A"),
    ("Carrier5", "AI-battlefield\sprites\Carrier5.png", "A"),
    ("restart", "AI-battlefield\sprites\Restart.png", "A")
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


player_guessed = set()
ai_guessed = set()
ai2_guessed = set()
player_ships_coords = []
ai_ships_coords = []
ai2_ships_coords = []
sunk_ai_ships = set()
sunk_player_ships = set()
moves_count = 0

def menu():
    # INITIALIZES BUTTONS
    button_pvaiS_rect = button("Player vs Simple-Reflex Agent", -80, screen, font)
    button_pvaiG_rect = button("Player vs Goal-Based Agent", -80, screen, font)
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
                if button_pvaiS_rect.collidepoint(mouse_pos):
                    return SFAI_PLAYER
                elif button_pvaiG_rect.collidepoint(mouse_pos):
                    return GBAI_PLAYER
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
        pvaiS_color = COLOR_hover if button_pvaiS_rect.collidepoint(mouse_pos) else COLOR_btn
        pvaiG_color =  COLOR_hover if button_pvaiG_rect.collidepoint(mouse_pos) else COLOR_btn
        aivai_color = COLOR_hover if button_aivai_rect.collidepoint(mouse_pos) else COLOR_btn
        quit_color = COLOR_hover if button_quit_rect.collidepoint(mouse_pos) else COLOR_btn
        button_pvaiS_rect = button("Player vs Simple-Reflex Agent", -160, screen, font, color=pvaiS_color)
        button_pvaiG_rect = button("Player vs Goal-Based Agent", -80, screen, font, color=pvaiG_color)
        button_aivai_rect = button("AI vs AI", 0, screen, font, color=aivai_color)
        button_quit_rect = button("Exit", 80, screen, font, color=quit_color)

        pvaiS_label = font.render("Player vs Simple-Reflex Agent", True, COLOR_btn_font)
        pvaiG_label = font.render("Player vs Goal-Based Agent", True, COLOR_btn_font)
        aivai_label = font.render("AI vs AI", True, COLOR_btn_font)
        quit_label = font.render("Exit", True, COLOR_btn_font)

        screen.blit(pvaiS_label, (button_pvaiS_rect.centerx - pvaiS_label.get_width()//2,
                                 button_pvaiS_rect.centery - pvaiS_label.get_height()//2))
        screen.blit(pvaiG_label, (button_pvaiG_rect.centerx - pvaiG_label.get_width()//2,
                                 button_pvaiG_rect.centery - pvaiG_label.get_height()//2))
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


def reset_game(mode):
    global ships, message_log
    global player_ships_coords, ai_ships_coords
    global player_guessed, ai_guessed, ai2_guessed
    global sunk_ai_ships, sunk_player_ships
    global moves_count, ai2_ships_coords

    ships.clear()
    message_log.clear()
    player_ships_coords.clear()
    ai_ships_coords.clear()
    ai2_ships_coords.clear()
    ai2_guessed.clear()
    player_guessed.clear()
    ai_guessed.clear()
    sunk_ai_ships.clear()
    sunk_player_ships.clear()
    moves_count = 0

    for b in [player_boardL, player_boardR,
                ai_board_topL, ai_board_topR,
                ai_board_bottomL, ai_board_bottomR]:
        b.reset()

    if mode == SFAI_PLAYER or mode == GBAI_PLAYER:
        init_fleet()   # only once, player’s draggable fleet
    else:
        init_fleet(ai_board_topL)    # AI vs AI
        init_fleet(ai_board_bottomL)


# -----------------------------------------------------------

def init_ai_fleet(ai_board):
    """
    Coloca barcos de forma aleatoria en el board y devuelve:
    - lista de objetos Ships
    - lista de diccionarios con 'name' y 'coords' para seguimiento de disparos
    """
    standard_lengths = [2, 3, 3, 4, 5]
    ai_board.reset()

    ships_list = []
    ships_coords = []

    for idx, length in enumerate(standard_lengths):
        placed = False
        attempts = 0
        while not placed:
            horizontal = random.choice([True, False])
            if horizontal:
                x = random.randint(0, ai_board.size - length)
                y = random.randint(0, ai_board.size - 1)
            else:
                x = random.randint(0, ai_board.size - 1)
                y = random.randint(0, ai_board.size - length)

            # Verifica solapamiento
            overlap = False
            for i in range(length):
                xi = x + i if horizontal else x
                yi = y if horizontal else y + i
                if ai_board.grid[yi][xi] == 'ship':
                    overlap = True
                    break

            if not overlap:
                coords = []
                for i in range(length):
                    xi = x + i if horizontal else x
                    yi = y if horizontal else y + i
                    ai_board.grid[yi][xi] = 'ship'
                    coords.append((yi, xi))

                ship = Ships(img=None, pos=(0,0), length=length, horizontal=horizontal)
                ship.grid_x = x
                ship.grid_y = y
                ship.name = f"Ship{length}_{idx+1}"
                ships_list.append(ship)
                ships_coords.append({"name": ship.name, "coords": coords})
                placed = True

            attempts += 1
            if attempts > 1000:
                raise RuntimeError(f"No se pudo colocar un barco de longitud {length} tras 1000 intentos.")

    return ships_list, ships_coords




def main_game(mode):
    # CLEARS AND INITIALIZES BOATS AGAIN
    global ships, message_log
    global player_ships_coords, ai_ships_coords, ai2_ships_coords
    global player_guessed, ai_guessed, ai2_guessed
    global sunk_ai_ships, sunk_player_ships
    global moves_count 

    reset_game(mode)
    if not ships:
        print("No ships in the list!")
        return
    print(f"--- DEBUG: {len(ships)} ships ---")
    for i, ship in enumerate(ships, start=1):
        name = getattr(ship, "name", "Unnamed")
        length = getattr(ship, "length", "Unknown")
        horizontal = getattr(ship, "horizontal", "?")
        print(f"{i}: Name={name}, Length={length}, Horizontal={horizontal}")
    print("--- END DEBUG ---")
    # GAME CONSTANTS
    ships_locked = False
    turn = "player1" # AI or human 
    game_over = False

    ai1 = SimpleReflexAgent() # Simple Reflex Agent
    ai2 = GoalBasedAgent(board_size=10) # Goal-Based Agent

    if mode == SFAI_PLAYER or mode == GBAI_PLAYER:
        lock_btn = button("Lock Ships", 200, screen, font, color=COLOR_btn_decision) 

    
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
        if mode == SFAI_PLAYER or mode == GBAI_PLAYER: # player_ai
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
            restart_btn = imgs["restart"].get_rect()
            restart_btn.topleft = (lock_btn.right + 40, lock_btn.top)

            for ship in ships:
                if ship.grid_x is not None and ship.grid_y is not None:
                    ship.rect.x = offset_px1 + ship.grid_x * CELL_SIZE
                    ship.rect.y = offset_py1 + ship.grid_y * CELL_SIZE
                ship.draw(screen)

        elif mode == AI_AI: # ai_ai
            offset_px1, offset_py1 = ai_board_topL.ingame(screen, COLOR_main, font, leftRight='L', mode=True, screen_part="top")
            #offset_px2, offset_py2 = ai_board_topR.ingame(screen, COLOR_opp, font, leftRight='R', mode=True, screen_part="top")
            #offset_px3, offset_py3 = ai_board_bottomL.ingame(screen, COLOR_main, font, leftRight='L', mode=True, screen_part="bottom")
            offset_px3, offset_py3 = ai_board_bottomL.ingame(screen, COLOR_main, font, leftRight='R', mode=True, screen_part="top")
            #offset_px4, offset_py4 = ai_board_bottomR.ingame(screen, COLOR_opp, font, leftRight='R',mode=True, screen_part="bottom")
            board_label(screen, "AI_1 PLACEMENT BOARD", offset_px1, offset_py1, CELL_SIZE)
            #board_label(screen, "AI_1 GUESSING BOARD", offset_px2, offset_py2, CELL_SIZE)
            board_label(screen, "AI_2 PLACEMENT BOARD", offset_px3, offset_py3, CELL_SIZE)
            #board_label(screen, "AI_2 GUESSING BOARD", offset_px4, offset_py4, CELL_SIZE)

            player_label(screen, "AI 1", offset_px1, offset_py1, CELL_SIZE)
            player_label(screen, "AI 2", offset_px3, offset_py3, CELL_SIZE)

            restart_btn = imgs["restart"].get_rect()
            screen_w, screen_h = screen.get_size()
            restart_btn.centerx = screen_w // 2
            restart_btn.top = offset_py3 + ai_board_bottomL.size * CELL_SIZE + 20
            #restart_btn.topleft = (lock_btn.right + 40, lock_btn.top)


        # SHIP DRAWING
        

        if game_over:
            screen.blit(imgs["restart"], restart_btn)


        if mode == AI_AI and not ships_locked:
            ai_ships, ai_ships_coords = init_ai_fleet(ai_board_topL)
            ai2_ships, ai2_ships_coords  = init_ai_fleet(ai_board_bottomL)
            ships_locked = True

        if mode == AI_AI and ships_locked and not game_over:
            r, c = ai1.choose_shot(ai_board_bottomL)
            moves_count += 1
            if ai_board_bottomL.grid[r][c] == 'ship':
                ai_board_bottomL.grid[r][c] = 'H'
                normal_message(f"AI 1 hit at ({r},{c})")
            else:
                ai_board_bottomL.grid[r][c] = 'M'
                normal_message(f"AI 1 missed at ({r},{c})")

            pygame.time.delay(100)

            r2, c2 = ai2.choose_shot(ai_board_topL)
            if ai_board_topL.grid[r2][c2] == 'ship':
                ai_board_topL.grid[r2][c2] = 'H'
                result = 'H'
                normal_message(f"AI 2 hit at ({r2},{c2})")
            else:
                ai_board_topL.grid[r2][c2] = 'M'
                result = 'M'
                normal_message(f"AI 2 missed at ({r2},{c2})")

            # Report result to modify state
            ai2.report_result((r2, c2), result)

            pygame.time.delay(40)

            if all(cell != 'ship' for row in ai_board_topL.grid for cell in row):
                main_message("AI 2 wins!")
                save_stats({"winner": "AI 2", "moves": moves_count, "mode": "AI_AI"})
                game_over = True
                ai2.reset()
                ships.clear()
            elif all(cell != 'ship' for row in ai_board_bottomL.grid for cell in row):
                main_message("AI 1 wins!")
                save_stats({"winner": "AI 1", "moves": moves_count, "mode": "AI_AI"})
                game_over = True
                ships.clear()


        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if lock_btn.collidepoint(mouse_pos) and mode == SFAI_PLAYER and not ships_locked:
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
                        ai_ships = [Ships(ship.img_original, ship.original_pos, ship.length) for ship in ships]
                        for i, ship in enumerate(ai_ships):
                            ship.name = ships[i].name  # Copy the name attribute
                            x, y, horizontal = ai1.choose_ship_placement(ai_boardR, ship)
                            coords = [(y, x+i) if horizontal else (y+i, x) for i in range(ship.length)]
                            for r, c in coords:
                                ai_boardR.grid[r][c] = 'ship'
                            ship.grid_x = x
                            ship.grid_y = y
                            ship.horizontal = horizontal
                            ai_ships_coords.append({"name": ship.name, "coords": coords})   

                    else:
                        normal_message("Place all 5 ships before locking them!")
                        if len(message_log) > MAX_MESSAGES:
                            message_log.pop(0)
                
                # PLAYER ONE GUESSING
                if ships_locked and turn == "player1" and not game_over and mode == SFAI_PLAYER:
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
                        turn = "SFAI"

                        # SUNK SHIPS
                        for ship in ai_ships_coords:
                             if ship["name"] not in sunk_ai_ships and ship_sunk(ship, ai_boardR):
                                sunk_ai_ships.add(ship["name"])  # marcar como ya hundido
                                base_name = ''.join([c for c in ship["name"] if not c.isdigit()])
                                main_message(f"AI's {base_name} sunk!")
                        if all(ship_sunk(ship, ai_boardR) for ship in ai_ships_coords):
                            main_message("Player wins!")
                            save_stats({"winner": "Player", "moves": moves_count, "mode": "SFAI_PLAYER"})
                            message_log.clear()
                            game_over = True

            # AI TURN, IMPLEMENT YOUR FUNCTION IDK
            if ships_locked and turn == "SFAI" and not game_over and mode == SFAI_PLAYER:
                # Use the agent to choose a shot
                shot = ai1.choose_shot(player_boardL)
                if shot:
                    row, col = shot
                    ai_guessed.add((row, col))
                    moves_count += 1
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
                        save_stats({"winner": "AI", "moves": moves_count, "mode": "SFAI_PLAYER"})
                        game_over = True

            
            # NEW STUFF -----------------------------------
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:   
                if lock_btn.collidepoint(mouse_pos) and mode == GBAI_PLAYER and not ships_locked:
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
                            start_col = (ship.rect.x - offset_px1) // CELL_SIZE
                            start_row = (ship.rect.y - offset_py1) // CELL_SIZE
                            ship.place_on_grid(start_col, start_row, offset_px1, offset_py1)
                            
                            coords = [(start_row, start_col+i) if ship.horizontal else (start_row+i, start_col) for i in range(ship.length)]
                            for r, c in coords:
                                player_boardL.grid[r][c] = 'ship'

                            player_ships_coords.append({"name": ship.name, "coords": coords})
                        normal_message("Ships locked!")
                    
                        # --- AI SHIP PLACEMENT USING AGENT ---
                        ai_ships_coords.clear()
                        ai_boardR.reset()

                        # Make copies of player's ships (only for length and name)
                        ai_ships = [Ships(ship.img_original, ship.original_pos, ship.length) for ship in ships]

                        for i, ship in enumerate(ai_ships):
                            ship.name = ships[i].name  # Copy name
                            
                            # Let AI pick a placement
                            col, row, horizontal = ai2.choose_ship_placement(ai_boardR, ship)  # x = col, y = row
                            ship.horizontal = horizontal
                            ship.grid_x = col
                            ship.grid_y = row
                            
                            # Generate the list of coordinates safely
                            coords = []
                            for j in range(ship.length):
                                c = col + j if horizontal else col
                                r = row if horizontal else row + j
                                
                                # Extra safety check
                                if r < 0 or r >= ai_boardR.size or c < 0 or c >= ai_boardR.size:
                                    raise RuntimeError(f"AI tried to place ship {ship.name} out of bounds at ({r},{c})")
                                
                                ai_boardR.grid[r][c] = 'ship'
                                coords.append((r, c))
                            
                            ai_ships_coords.append({"name": ship.name, "coords": coords})
                    else:
                        normal_message("Place all 5 ships before locking them!")
                        if len(message_log) > MAX_MESSAGES:
                            message_log.pop(0)

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
                        turn = "GBAI"

                        # SUNK SHIPS
                        for ship in ai_ships_coords:
                             if ship["name"] not in sunk_ai_ships and ship_sunk(ship, ai_boardR):
                                sunk_ai_ships.add(ship["name"])  # marcar como ya hundido
                                base_name = ''.join([c for c in ship["name"] if not c.isdigit()])
                                main_message(f"AI's {base_name} sunk!")
                        if all(ship_sunk(ship, ai_boardR) for ship in ai_ships_coords):
                            main_message("Player wins!")
                            ai2.reset()
                            message_log.clear()
                            game_over = True

            # AI TURN, GOAL-BASED AGENT
            if ships_locked and turn == "GBAI" and not game_over and mode == GBAI_PLAYER:
                # AGENT PICKS A SHOOT
                row, col = ai2.choose_shot(player_boardL)
                moves_count += 1
                # APPLY RESULT TO BOARD
                if player_boardL.grid[row][col] == 'ship':
                    player_boardL.grid[row][col] = 'H'
                    result = 'H'
                    normal_message(f"AI hit at ({row},{col})")
                else:
                    player_boardL.grid[row][col] = 'M'
                    result = 'M'
                    normal_message(f"AI missed at ({row},{col})")

                # REPORT RESULT BACK TO THE AGENT
                ai2.report_result((row, col), result)
                turn = "player1"

                # SUNK SHIPS
                for ship in player_ships_coords:
                    if ship["name"] not in sunk_player_ships and ship_sunk(ship, player_boardL):
                        sunk_player_ships.add(ship["name"])
                        base_name = ''.join([c for c in ship["name"] if not c.isdigit()])
                        main_message(f"Your {base_name} sunk!")
                        # Inform the agent that the ship is sunk
                        ai2.report_result((row, col), "S")

                if all(ship_sunk(ship, player_boardL) for ship in player_ships_coords):
                    main_message("AI wins!")
                    ai2.reset()
                    message_log.clear()
                    save_stats({"winner": "AI", "moves": moves_count, "mode": "GBAI_PLAYER"})
                    game_over = True



            if not ships_locked:
                ship_events(screen, ships, event, player_boardL, offset_px1, offset_py1)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over and restart_btn.collidepoint(event.pos):
                    reset_game(mode)
                    ships_locked = False
                    turn = "player1"
                    game_over = False


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

        #if game_over:
        #    screen.blit(imgs["restart"], restart_btn)

        pygame.display.flip()

    #pygame.quit()



while not end_game_flag:
    mode = menu()
    if mode is None:
        break
    #reset_game(mode)
    main_game(mode)
    print("Returned to the main menu.")

pygame.quit()