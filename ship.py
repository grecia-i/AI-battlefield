import pygame
import re
from settings import CELL_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, imgs
import random

ships = []

class Ships:
    def __init__(self, img, pos, length, horizontal=True):
        self.length = length
        self.horizontal = horizontal
        self.img_original = img  # keep the original
        self.image = self.orient_image()
        self.rect = self.image.get_rect(topleft=pos)
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.original_pos = pos

        self.grid_x = None
        self.grid_y = None

    def orient_image(self):
        if self.horizontal:
            return self.img_original
        else:
            return pygame.transform.rotate(self.img_original, 90)
        
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def reset_position(self):
        self.rect.topleft = self.original_pos

    def rotate(self):
        self.horizontal = not self.horizontal
        # Save current top-left
        current_pos = self.rect.topleft
        self.image = self.orient_image()
        self.rect = self.image.get_rect(topleft=current_pos)

    def place_on_grid(self, grid_x, grid_y, board_offset_x, board_offset_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.rect.x = board_offset_x + grid_x * CELL_SIZE
        self.rect.y = board_offset_y + grid_y * CELL_SIZE

    @property
    def grid_size(self):
        """Return width, height in grid cells"""
        return (self.length, 1) if self.horizontal else (1, self.length)

def init_fleet(board=None):
    ships.clear()
    spacing_x = 50

    # DIVIDES INTO TWO ROWS FOR AI_VS_AI
    ship_items = [ (name, img)
        for name, img in imgs.items()
        if re.match(r'[A-Za-z]*([0-9]+)$', name)
    ]
    half = (len(ship_items) + 1) // 2

    # TOP ROW
    current_x = 100
    current_y = SCREEN_HEIGHT - 200
    for name, img in ship_items[:half]:
        length = int(re.match(r'[A-Za-z]*([0-9]+)$', name).group(1))
        ship = Ships(img, (current_x, current_y), length)
        ship.name = name  
        ships.append(ship)
        current_x += CELL_SIZE * length + spacing_x

    # BOTTOM ROW
    current_x = 100
    current_y = SCREEN_HEIGHT - 160
    for name, img in ship_items[half:]:
        length = int(re.match(r'[A-Za-z]*([0-9]+)$', name).group(1))
        ship = Ships(img, (current_x, current_y), length)
        ship.name = name 
        ships.append(ship)
        current_x += CELL_SIZE * length + spacing_x
    # COLOCA LOS BARCOS EN EL GRID
    if board:
        place_ai_fleet(board)


## ESTA ES PROVISIONAL OBVIO solo fue para probar 
def place_ai_fleet(board):
    ship_lengths = [2, 3, 3, 4, 5] 
    for length in ship_lengths:
        placed = False
        while not placed:
            horizontal = random.choice([True, False])
            if horizontal:
                x = random.randint(0, board.size - length)
                y = random.randint(0, board.size - 1)
            else:
                x = random.randint(0, board.size - 1)
                y = random.randint(0, board.size - length)
            
            # CELLS ARE FREE
            overlap = False
            for i in range(length):
                xi = x + i if horizontal else x
                yi = y if horizontal else y + i
                if board.grid[yi][xi] == 'S':
                    overlap = True
                    break
            
            if not overlap:
                # MARKS SHIPS ONLY LOGICALLY (NO DRAWING)
                for i in range(length):
                    xi = x + i if horizontal else x
                    yi = y if horizontal else y + i
                    board.grid[yi][xi] = 'S'
                placed = True

def ship_events(screen, ships, event, board, board_offset_x, board_offset_y):
    # SHIP INTERACTION MOSTLY FOR PLAYER
    mouse_pos = pygame.mouse.get_pos()
    hovering_any = False

    for ship in reversed(ships):  # topmost first
        ship_rect = ship.rect

        # HOVER CURSOR
        if ship_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            hovering_any = True

            # STARTS DRAGGING
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                ship.dragging = True
                ship.offset_x = ship_rect.x - mouse_pos[0]
                ship.offset_y = ship_rect.y - mouse_pos[1]

            # RIGHT CLICK ROTATES THE SHIP
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                ship.rotate()

        # DROPS THE SHIP
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and ship.dragging:
            ship.dragging = False

            # ACCOMODATES IT TO THE GRID
            grid_x = (ship.rect.x - board_offset_x + CELL_SIZE//2) // CELL_SIZE
            grid_y = (ship.rect.y - board_offset_y + CELL_SIZE//2) // CELL_SIZE

            w, h = ship.grid_size

            # CHECKS IF WITHIN BOUNDARIES
            if grid_x < 0 or grid_y < 0 or grid_x + w > 10 or grid_y + h > 10:
                ship.reset_position()
                continue

            # CHECKS COLLISIONS 
            collision = False
            for other in ships:
                if other == ship:
                    continue
                ox, oy = (other.rect.x - board_offset_x)//CELL_SIZE, (other.rect.y - board_offset_y)//CELL_SIZE
                ow, oh = other.grid_size
                other_cells = [(ox + i, oy + j) for i in range(ow) for j in range(oh)]
                ship_cells = [(grid_x + i, grid_y + j) for i in range(w) for j in range(h)]
                if any(cell in other_cells for cell in ship_cells):
                    collision = True
                    break

            if collision:
                ship.reset_position()
            else:
                ship.rect.topleft = (board_offset_x + grid_x*CELL_SIZE,
                                     board_offset_y + grid_y*CELL_SIZE)

        # WHILE DRAGGING
        elif event.type == pygame.MOUSEMOTION and ship.dragging:
            ship.rect.x = mouse_pos[0] + ship.offset_x
            ship.rect.y = mouse_pos[1] + ship.offset_y

    # RESET CURSOR IF NOT HOVERING THIS WAS FOR SPRITES BUT DIDNT WORK
    if not hovering_any:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
