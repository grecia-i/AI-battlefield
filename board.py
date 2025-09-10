import pygame
from settings import *
from ship import *

class Board:
    def __init__(self, size, default_value=' '):
        self.size = size
        self.grid = [[default_value for _ in range(size)] for _ in range(size)]
        self.offset_x = 0
        self.offset_y = 0

    def ingame(self, surface, colorgrid, font, leftRight, mode=True, screen_part="top"):
        rows, cols = self.size, self.size
        screen_w, screen_h = pygame.display.get_surface().get_size()
        grid_w = cols * CELL_SIZE
        grid_h = rows * CELL_SIZE
        margin_x = screen_w // 5 
        margin_y = screen_h // 8
        spacing = 150

        # OFFSETS
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
            return None, None

        self.offset_x = offset_x
        self.offset_y = offset_y

        # DRAWS CELLS
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                rect = pygame.Rect(self.offset_x + j*CELL_SIZE, self.offset_y + i*CELL_SIZE, CELL_SIZE, CELL_SIZE, border_radius=8)
                pygame.draw.rect(surface, colorgrid, rect, border_radius=6)
                pygame.draw.rect(surface, COLOR_lining, rect, 1, border_radius=6)

                # HITS/MISSES
                if cell == 'H':  # hit
                    pygame.draw.rect(surface, (255,105,180), rect, border_radius=6)  # pink
                elif cell == 'M':  # miss
                    pygame.draw.rect(surface, (180,180,180), rect, border_radius=6)  # grey


        # ROW NUMBERS
        for i in range(rows):
            num_rows = font.render(chr(ord('@')+(i+1)), True, COLOR_font)
            x = self.offset_x - 25
            y = self.offset_y + i*CELL_SIZE + CELL_SIZE//2 - num_rows.get_height()//2
            surface.blit(num_rows, (x, y))
        # COLUMN NUMBERS
        for j in range(cols):
            num_cols = font.render(str(j+1), True, COLOR_font)
            x = self.offset_x + j*CELL_SIZE + CELL_SIZE//2 - num_cols.get_width()//2
            y = self.offset_y - 25
            surface.blit(num_cols, (x, y))

        return offset_x, offset_y

    # TO GET THE CELL TO HIGHLIGHT
    def get_hover_cell(self, x, y):
        col = (x - self.offset_x) // CELL_SIZE
        row = (y - self.offset_y) // CELL_SIZE
        if 0 <= row < self.size and 0 <= col < self.size:
            return (row, col)
        return None

    # DRAWS THE HOVER WITH ANOTHER COLOR
    def draw_hover(self, surface, hover_cell, color=COLOR_hover):
        if hover_cell is None:
            return
        row, col = hover_cell
        hover_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        hover_surf.fill(color)
        x = self.offset_x + col * CELL_SIZE
        y = self.offset_y + row * CELL_SIZE
        surface.blit(hover_surf, (x, y))

    def reset(self):
        self.grid = [[' ' for _ in range(self.size)] for _ in range(self.size)]

    # PLACES THE SHIP ON THE GRID
    def place_ship(self, ship, x, y):
        cells = []

        for i in range(ship.length):
            xi = x + i if ship.horizontal else x
            yi = y if ship.horizontal else y + i

            # LIMITS
            if not (0 <= xi < self.size and 0 <= yi < self.size):
                return False

            # OVERLAP
            if self.grid[yi][xi] == 'ship':
                return False

            cells.append((xi, yi))

        for xi, yi in cells:
            self.grid[yi][xi] = 'S'

        return True
    
    # TO CHECK IF THE SHOT IS VALID (NEITHER HIT NOR MISS)
    def valid_shots(self):
        valid = []
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] not in ('H', 'M'):  
                    valid.append((r, c))
        return valid
    