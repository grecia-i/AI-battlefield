import pygame
import re
from settings import CELL_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, imgs

ships = []

class Ships:
    def __init__(self, img, pos, length, horizontal=True):
        self.length = length
        self.horizontal = horizontal
        self.img_original = img  # keep the original
        self.image = self.orient_image(img)
        self.rect = self.image.get_rect(topleft=pos)
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.original_pos = pos

    def orient_image(self, img):
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
        self.image = self.orient_image(self.image)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)


def init_fleet():
    ships.clear()
    spacing_x = 20

    # Divide ships into two rows
    ship_items = [
        (name, img)
        for name, img in imgs.items()
        if re.match(r'[A-Za-z]*([0-9]+)$', name)
    ]
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


def ship_events(ships, event, board, board_offset_x, board_offset_y):
    mouse_pos = pygame.mouse.get_pos()
    '''
    mouse_pos = pygame.mouse.get_pos()
    cx = x-imgs["mouse"].get_width() // 2
    cy = y-imgs["mouse"].get_height() // 2
    screen.blit(imgs["mouse"], (cx,cy))
    hovering_any = False
    '''
    for ship in reversed(ships):  # check topmost first
        # Hover cursor
        if ship.rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            hovering_any = True

            # Start dragging
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                ship.dragging = True
                ship.offset_x = ship.rect.x - mouse_pos[0]
                ship.offset_y = ship.rect.y - mouse_pos[1]
                ship.drag_start = mouse_pos
                # bring to top
                ships.remove(ship)
                ships.append(ship)
                break

            # Rotate on right click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                ship.rotate()
                break

        # Release
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and ship.dragging:
            ship.dragging = False
            dx = abs(event.pos[0] - ship.drag_start[0])
            dy = abs(event.pos[1] - ship.drag_start[1])

            # If it was a click (not drag), rotate
            if dx < 5 and dy < 5:
                ship.rotate()
                break

            # Snap to grid
            grid_x = (ship.rect.x - board_offset_x + CELL_SIZE // 2) // CELL_SIZE
            grid_y = (ship.rect.y - board_offset_y + CELL_SIZE // 2) // CELL_SIZE

            grid_x = max(0, min(10 - (ship.length if ship.horizontal else 1), grid_x))
            grid_y = max(0, min(10 - (1 if ship.horizontal else ship.length), grid_y))

            # collision
            ship_cells = [(grid_x + i, grid_y) if ship.horizontal else (grid_x, grid_y + i) for i in range(ship.length)]
            collision = False
            for other in ships:
                if other == ship:
                    continue
                other_cells = [
                    ((other.rect.x - board_offset_x) // CELL_SIZE + i, (other.rect.y - board_offset_y) // CELL_SIZE)
                    if other.horizontal else
                    ((other.rect.x - board_offset_x) // CELL_SIZE, (other.rect.y - board_offset_y) // CELL_SIZE + i)
                    for i in range(other.length)
                ]
                if any(cell in other_cells for cell in ship_cells):
                    collision = True
                    break

            if not collision:
                ship.rect.x = board_offset_x + grid_x * CELL_SIZE
                ship.rect.y = board_offset_y + grid_y * CELL_SIZE
            else:
                ship.reset_position()

        # Dragging movement
        elif event.type == pygame.MOUSEMOTION and ship.dragging:
            ship.rect.x = mouse_pos[0] + ship.offset_x
            ship.rect.y = mouse_pos[1] + ship.offset_y

    if not hovering_any:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)