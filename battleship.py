import pygame
from pygame.locals import *
import time
import os
import random 
from sys import exit

# pygame setup constants
BOARD_SIZE = 10
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
## screen.fill(color1)
COLOR_inner = '#E5E5E5' # light white
COLOR_grid = '#696CFF'
CELL_SIZE = 45 # px


def create_board(size, def_value=' '): # ~ for water
    return [[def_value for _ in range(size)] for _ in range(size)] # 2D matrix grid

player_board = create_board(BOARD_SIZE)
opposite_board = create_board(BOARD_SIZE)

def ingame_board(surface, board):
    offset_x = (SCREEN_WIDTH - 800) // 2   # 500: CELLS TOP * PIXELS
    offset_y = (SCREEN_HEIGHT - 500) // 2  
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            rectangle = pygame.Rect(offset_x + j*CELL_SIZE, offset_y + i*CELL_SIZE, CELL_SIZE, CELL_SIZE,border_radius = 8)
            pygame.draw.rect(surface, COLOR_inner, rectangle, border_radius = 6)
            pygame.draw.rect(surface, COLOR_grid, rectangle, 1,  border_radius = 6)



# for sprite and image handling
imgs = {}   # dictionary for loaded images
images_path = [
    ("playBtn", "Battlefield\AI-battlefield\sprites\PlayButton.png", "A"),
    ("background", "Battlefield\AI-battlefield\sprites\Background.png", "C"),
    ("mouse", "Battlefield\AI-battlefield\sprites\CursorDefault.png", "A")
]



def main():
    pygame.init()

    # Setting the window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Battleship")

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
            if event.type == pygame.QUIT:
                running = False

            # loads background and mouse
            screen.blit(imgs["background"], (0,0))
            pygame.display.flip()

            x, y = pygame.mouse.get_pos()
            x -= imgs["mouse"].get_width() / 2
            y -= imgs["mouse"].get_height() / 2
            screen.blit(imgs["mouse"], (x,y))

            pygame.display.update()

            ingame_board(screen, player_board)
            pygame.display.update()


    pygame.quit()

# Quit pygame
# sys.exit()

if __name__ == "__main__":
    main()