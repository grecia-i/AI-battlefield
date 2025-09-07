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

#player_board = create_board(BOARD_SIZE)

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

player_board = Board(10)
player_board_right = Board(10)
ai_board_topL = Board(10)
ai_board_topR = Board(10)
ai_board_bottomL = Board(10)
ai_board_bottomR = Board(10)

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
            offset_px1, offset_py1 = player_board.ingame(
                screen, COLOR_main, font, leftRight='L', mode=True, screen_part="top")
            offset_px2, offset_py2 = player_board_right.ingame(
                screen, COLOR_opp, font, leftRight='R', mode=False, screen_part="top")
            #offset_px1, offset_py1 = ingame_board(screen, player_board, 'L', COLOR_main, font, mode=True, screen_part="top")
            #offset_px2, offset_py2 = ingame_board(screen, player_board, 'R', COLOR_opp, font, mode=False, screen_part="top")
        elif mode == 1: # ai_ai
            offset_px1, offset_py1 = ai_board_topL.ingame(screen, COLOR_main, font, leftRight='L', mode=True, screen_part="top")
            offset_px2, offset_py2 = ai_board_topR.ingame(screen, COLOR_opp, font, leftRight='R', mode=True, screen_part="top")
            offset_px3, offset_py3 = ai_board_bottomL.ingame(screen, COLOR_main, font, leftRight='L', mode=True, screen_part="bottom")
            offset_px4, offset_py4 = ai_board_bottomR.ingame(screen, COLOR_opp, font, leftRight='R',mode=True, screen_part="bottom")

        for event in pygame.event.get():
            # EVENT HANDLING
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                mode = menu()  # return to menu
                # Reset boards & ships if coming back
                player_board.reset()
                player_board_right.reset()
                ai_board_topL.reset()
                ai_board_topR.reset()
                ai_board_bottomL.reset()
                ai_board_bottomR.reset()
                ships.clear()

            # DRAGGING SHIPS
            ship_events(screen, ships, event, player_board, offset_px1, offset_py1)

        
            # loads background and mouse
            screen.blit(imgs["background"], (0,0))
            background_blocks(1050, 550)
            pygame.mouse.set_visible(False)

            if mode == 0: # player_ai
                offset_px1, offset_py1 = player_board.ingame(
                    screen, COLOR_main, font, leftRight='L', mode=True, screen_part="top")
                offset_px2, offset_py2 = player_board_right.ingame(
                    screen, COLOR_opp, font, leftRight='R', mode=False, screen_part="top")
                #offset_px1, offset_py1 = ingame_board(screen, player_board, 'L', COLOR_main, font, mode=True, screen_part="top")
                #offset_px2, offset_py2 = ingame_board(screen, player_board, 'R', COLOR_opp, font, mode=False, screen_part="top")
            elif mode == 1: # ai_ai
                offset_px1, offset_py1 = ai_board_topL.ingame(screen, COLOR_main, font, leftRight='L', mode=True, screen_part="top")
                offset_px2, offset_py2 = ai_board_topR.ingame(screen, COLOR_opp, font, leftRight='R', mode=True, screen_part="top")
                offset_px3, offset_py3 = ai_board_bottomL.ingame(screen, COLOR_main, font, leftRight='L', mode=True, screen_part="bottom")
                offset_px4, offset_py4 = ai_board_bottomR.ingame(screen, COLOR_opp, font, leftRight='R',mode=True, screen_part="bottom")


            for ship in ships:
                ship.draw(screen)

            x, y = pygame.mouse.get_pos()
            hover_1 = player_board.get_hover_cell(x, y)
            hover_2 = player_board_right.get_hover_cell(x, y)
            player_board.draw_hover(screen, hover_1, COLOR_hover)
            player_board_right.draw_hover(screen, hover_2, COLOR_hover)
            cx = x-imgs["mouse"].get_width() // 2
            cy = y-imgs["mouse"].get_height() // 2
            screen.blit(imgs["mouse"], (cx,cy))
    
            pygame.display.flip()

    pygame.quit()

mode = menu()
main_game(mode)
pygame.quit()